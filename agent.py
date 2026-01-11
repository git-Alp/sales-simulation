import time
import random
from mesa import Agent
from langchain_ollama import ChatOllama

class ConsumerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.budget = random.randint(2000, 5000)
        self.impulsivity = random.triangular(0.0, 1.0, 0.5)
        self.needs_product = random.choice([True] + [False] * 3)
        self.has_bought = False

        self.persona = "Impulsive" if self.impulsivity > 0.6 else "Careful"
        
        self.llm = ChatOllama(model="llama3.1", temperature=0.7)

    def step(self):
        if self.has_bought or self.model.stock <= 0:
            return

        # Build a rich behavioral profile
        behavioral_traits = []
        if self.impulsivity > 0.7:
            behavioral_traits.append("You tend to make quick decisions and are easily excited by deals.")
        elif self.impulsivity < 0.3:
            behavioral_traits.append("You prefer to think carefully before making purchases and rarely impulse buy.")
        else:
            behavioral_traits.append("You sometimes make spontaneous purchases but also consider value.")
        
        if self.needs_product:
            behavioral_traits.append("You've been looking for headphones for a while.")
        else:
            behavioral_traits.append("You don't currently need headphones, but a good deal might change your mind.")
        
        # Calculate financial pressure
        affordability = (self.budget / 3500) * 100
        
        prompt = f"""
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
        - Only {self.model.stock} units left in stock
        - Sale ends in {self.model.time_left} minutes
        - This is a "Premium Headphones" flash sale
        
        Consider ALL factors: Do you actually need this? Is it worth spending this much of your budget? 
        Does the time pressure/scarcity make you anxious or motivated? Does the discount feel genuine or manipulative?
        Would buying this affect your other financial plans?
        
        IMPORTANT: Even if you CAN afford it (budget >= 3500), you might choose NOT to buy based on:
        - Not actually needing it
        - Preferring to save money
        - Feeling manipulated by sales tactics
        - Having other priorities
        - Simply not being interested
        
        Respond ONLY in this format:
        DECISION: [BUY/NO] | REASON: [One sentence explaining your behavioral reasoning]
        """

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Logging (Save the thought to the model)
            self.model.journal.append(f"Agent {self.unique_id} ({self.persona}, Budget:{self.budget}): {content}")

            if "DECISION: BUY" in content:
                self._buy_product()
                
        except Exception as e:
            print(f"Error: {e}")

    def _buy_product(self):
        if self.model.stock > 0:
            self.model.stock -= 1
            self.has_bought = True