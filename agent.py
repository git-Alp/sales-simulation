import time
import random
import re
import os
import logging
import warnings
from datetime import datetime
from mesa import Agent as MesaAgent

# Suppress noisy deprecation warnings from Google libraries
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, SafetySetting
from dotenv import load_dotenv

# Load environment variables from .env in parent or current directory
load_dotenv()

# ---- Logging setup ----
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Initialize Vertex AI once at module load
_project_id = os.getenv("GOOGLE_PROJECT_ID")
_location = os.getenv("GOOGLE_LOCATION", "us-central1")
_model_id = os.getenv("AGENT_MODEL_ID", "gemini-2.0-flash")

if (_project_id):
    vertexai.init(project=_project_id, location=_location)
    logger.info(f"[VertexAI init] project={_project_id} location={_location} model={_model_id}")
else:
    raise RuntimeError("Missing GOOGLE_PROJECT_ID in environment. Set it in .env or export it.")

# Shared model instance (avoids re-init per agent)
_generative_model = GenerativeModel(_model_id)
_generation_config = GenerationConfig(temperature=0.7, max_output_tokens=256)
_safety_settings = [
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
    SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE),
]

PRICE = 3500  # product price used in prompts


class ConsumerAgent(MesaAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # More realistic budget distribution (2000-8000 TL range)
        self.budget = random.randint(2000, 8000)
        self.impulsivity = random.triangular(0.0, 1.0, 0.5)
        self.age = random.randint(18, 80)
        self.age_group = self._get_age_group(self.age)
        self.education = random.choice([
            "High school graduate",
            "University graduate",
            "Master's graduate",
            "PhD graduate",
        ])
        # 15% actually need the product (more realistic than 25%)
        self.needs_product = random.random() < 0.15
        self.has_bought = False

        # More nuanced persona classification
        if self.impulsivity > 0.8:
            self.persona = "Impulsive"
        elif self.impulsivity < 0.3:
            self.persona = "Careful"
        else:
            self.persona = "Moderate"

    @staticmethod
    def _get_age_group(age):
        if age <= 29:
            return "18-29"
        if age <= 44:
            return "30-44"
        if age <= 59:
            return "45-59"
        return "60-80"

    def _get_segment_label(self):
        if self.model.prompt_variant == "age":
            return self.age_group
        if self.model.prompt_variant == "education":
            return self.education
        return self.persona

    def _get_log_profile(self):
        if self.model.prompt_variant == "age":
            return f"Age:{self.age} | AgeGroup:{self.age_group}"
        if self.model.prompt_variant == "education":
            return f"Education:{self.education}"
        return f"Persona:{self.persona}"

    def _build_prompt(self, affordability, behavioral_traits, scarcity_msg, time_msg):
        if self.model.prompt_variant == "age":
            return f"""
        You are a shopper with the following profile:

        FINANCIAL SITUATION:
        - Your budget: {self.budget} TL
        - Product price: 3500 TL (30% discount from 5000 TL)
        - Affordability: {"Easily affordable" if affordability > 150 else "Affordable but tight" if affordability > 100 else "Would use most of your budget" if affordability >= 100 else "Cannot afford"}

        PROFILE:
        - You are {self.age} years old.
        - {behavioral_traits[1]}

        SITUATION:
        - Stock: {self.model.stock} units left (started with {self.model.initial_stock})
        - {scarcity_msg}
        - {time_msg}
        - You've been observing for {self.model.initial_time - self.model.time_left} minutes
        - This is a "Premium Headphones" flash sale

        CONTEXT TO CONSIDER:
        - Time pressure level: {"High" if self.model.time_left <= 3 else "Moderate" if self.model.time_left <= 6 else "Low"}
        - Others are buying as stock decreases

        Consider ALL factors:
        - Do you actually need this product?
        - Is it worth spending this much of your budget?
        - Does the scarcity create genuine urgency or feel manipulative?
        - As stock/time decreases, does this change your decision?
        - Would you regret buying or NOT buying?
        - Is the discount genuine value or pressure tactic?

        Respond ONLY in this format:
        DECISION: [BUY/NO] | REASON: [One sentence explaining your behavioral reasoning]
        """

        if self.model.prompt_variant == "education":
            return f"""
        You are a shopper with the following profile:

        FINANCIAL SITUATION:
        - Your budget: {self.budget} TL
        - Product price: 3500 TL (30% discount from 5000 TL)
        - Affordability: {"Easily affordable" if affordability > 150 else "Affordable but tight" if affordability > 100 else "Would use most of your budget" if affordability >= 100 else "Cannot afford"}

        PROFILE:
        - You are a {self.education}.
        - {behavioral_traits[1]}
        - Your education is background information only. Do not use education level as a preference, personality trait, or justification in your decision.

        SITUATION:
        - Stock: {self.model.stock} units left (started with {self.model.initial_stock})
        - {scarcity_msg}
        - {time_msg}
        - You've been observing for {self.model.initial_time - self.model.time_left} minutes
        - This is a "Premium Headphones" flash sale

        CONTEXT TO CONSIDER:
        - Time pressure level: {"High" if self.model.time_left <= 3 else "Moderate" if self.model.time_left <= 6 else "Low"}
        - Others are buying as stock decreases

        Consider ALL factors:
        - Do you actually need this product?
        - Is it worth spending this much of your budget?
        - Does the scarcity create genuine urgency or feel manipulative?
        - As stock/time decreases, does this change your decision?
        - Would you regret buying or NOT buying?
        - Is the discount genuine value or pressure tactic?

        Respond ONLY in this format:
        DECISION: [BUY/NO] | REASON: [One sentence explaining your behavioral reasoning]
        """

        return f"""
        You are a {self.persona} shopper with the following profile:

        FINANCIAL SITUATION:
        - Your budget: {self.budget} TL
        - Product price: 3500 TL (30% discount from 5000 TL)
        - Affordability: {"Easily affordable" if affordability > 150 else "Affordable but tight" if affordability > 100 else "Would use most of your budget" if affordability >= 100 else "Cannot afford"}

        BEHAVIORAL PROFILE:
        - Personality: {self.persona}
        - Impulsivity level: {self.impulsivity:.2f} (0=very careful, 1=very impulsive)
        - {behavioral_traits[0]}
        - {behavioral_traits[1]}

        SITUATION:
        - Stock: {self.model.stock} units left (started with {self.model.initial_stock})
        - {scarcity_msg}
        - {time_msg}
        - You've been observing for {self.model.initial_time - self.model.time_left} minutes
        - This is a "Premium Headphones" flash sale

        CONTEXT TO CONSIDER:
        - Time pressure level: {"High" if self.model.time_left <= 3 else "Moderate" if self.model.time_left <= 6 else "Low"}
        - Others are buying as stock decreases

        Consider ALL factors:
        - Do you actually need this product?
        - Is it worth spending this much of your budget?
        - Does the scarcity create genuine urgency or feel manipulative?
        - As stock/time decreases, does this change your decision?
        - Would you regret buying or NOT buying?
        - Is the discount genuine value or pressure tactic?

        Respond ONLY in this format:
        DECISION: [BUY/NO] | REASON: [One sentence explaining your behavioral reasoning]
        """
    
    def step(self):
        """Synchronous step with LLM call"""
        try:
            # Build detailed prompt with all context
            affordability = self.budget / self.model.product_price * 100
            
            # Behavioral traits based on persona/impulsivity
            if self.persona == "Impulsive":
                behavioral_traits = [
                    "You tend to make quick decisions without overthinking.",
                    "FOMO (fear of missing out) significantly influences your choices."
                ]
            elif self.persona == "Careful":
                behavioral_traits = [
                    "You carefully evaluate every purchase decision.",
                    "You prefer to avoid impulsive decisions and analyze options thoroughly."
                ]
            else:  # Moderate
                behavioral_traits = [
                    "You balance impulse with rational thought.",
                    "You consider both emotions and logic in your decisions."
                ]
            
            # Scarcity message
            stock_percent = (self.model.stock / self.model.initial_stock) * 100
            if stock_percent > 50:
                scarcity_msg = "Stock is abundant, no immediate scarcity pressure."
            elif stock_percent > 20:
                scarcity_msg = "Stock is moderately low. Some scarcity pressure is building."
            else:
                scarcity_msg = "Stock is critically low. Strong scarcity and urgency."
            
            # Time message
            time_percent = (self.model.time_left / self.model.initial_time) * 100
            if time_percent > 50:
                time_msg = "Plenty of time remains for this sale."
            elif time_percent > 20:
                time_msg = "Time is running out. About half the sale duration remains."
            else:
                time_msg = "Very little time left. This is your last chance."
            
            prompt = self._build_prompt(affordability, behavioral_traits, scarcity_msg, time_msg)
            
            # Direct synchronous LLM call
            response = _generative_model.generate_content(
                prompt,
                generation_config=_generation_config,
                safety_settings=_safety_settings,
            )
            
            # Parse response
            raw_text = response.text.strip()
            decision_text = raw_text.upper()
            
            if "BUY" in decision_text:
                self.decision = "BUY"
            else:
                self.decision = "NO"
            
            # Extract reason - look for the detailed format
            if "REASON:" in decision_text:
                self.reason = decision_text.split("REASON:")[-1].strip()
            else:
                self.reason = "No reason provided"
                
            logger.info(f"{self} | Decision:{self.decision} | Reason:{self.reason[:50]}...")
            
            # Process the decision
            segment = self._get_segment_label()
            purchased = False
            budget_blocked = False
            
            if self.decision == "BUY":
                # Check if agent has budget
                if self.budget >= self.model.product_price:
                    # Try to buy
                    if self._buy_product():
                        self.budget -= self.model.product_price
                        purchased = True
                        logger.info(f"{self} | PURCHASED | Remaining budget: {self.budget}")
                    else:
                        # Stock was exhausted
                        logger.info(f"{self} | Stock exhausted, purchase blocked")
                else:
                    # Budget insufficient
                    budget_blocked = True
                    logger.info(f"{self} | Budget insufficient ({self.budget} < {self.model.product_price})")
            
            # Record decision in model
            self.model.record_decision(
                segment=segment,
                intent=self.decision,
                purchased=purchased,
                budget_blocked=budget_blocked,
                agent_id=self.unique_id
            )
            
        except Exception as e:
            logger.error(f"{self} | LLM Error: {str(e)}")
            self.decision = "NO"
            self.reason = f"Error: {str(e)}"
            # Still record the error as a NO decision
            segment = self._get_segment_label()
            self.model.record_decision(
                segment=segment,
                intent="NO",
                purchased=False,
                budget_blocked=False,
                agent_id=self.unique_id
            )
    
    def _buy_product(self):
        """Attempt to buy product. Returns True if successful, False if stock exhausted."""
        if self.model.stock > 0:
            self.model.stock -= 1
            self.has_bought = True
            return True
        return False