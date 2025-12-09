from mesa import Agent
import random

class TestConsumerAgent(Agent):
    """
    A consumer agent that has a specific personality, budget, and impulsivity level.
    It observes the market (Flash Sale) and decides whether to buy or not.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        # --- STATE: Fixed Attributes (Profile) ---
        # 1. Budget: How much money the agent has (Randomly assigned between 500 and 3000)
        self.budget = random.randint(500, 3000)
        
        # 2. Impulsivity Score: 0.0 (Very Rational) to 1.0 (Very Impulsive)
        # We use a triangular distribution to make extreme values less likely.
        self.impulsivity = random.triangular(0.0, 1.0, 0.5)
        
        # 3. Needs Product: Does the agent actually NEED this item? (True/False)
        # 20% chance they really need it, 80% chance they just want it.
        self.needs_product = random.choice([True] + [False] * 4)

        # 4. Status: Has the agent bought the item?
        self.has_bought = False

        # --- PERSONA GENERATION ---
        # We create a text-based persona to send to the LLM later.
        self.persona_description = self._generate_persona()

    def _generate_persona(self):
        """
        Helper method to create a natural language description of the agent.
        This will be part of the System Prompt for the LLM.
        """
        trait = "impulsive" if self.impulsivity > 0.6 else "careful"
        financial = "tight budget" if self.budget < 1000 else "comfortable budget"
        need = "really needs a new phone" if self.needs_product else "is just browsing"
        
        return f"You are a consumer who is {trait}, has a {financial}, and {need}."

    def step(self):
        """
        The step method is called in every tick of the simulation.
        Here, the agent will observe the environment and make a decision.
        """
        # If already bought, do nothing (exit the loop)
        if self.has_bought:
            return

        # TODO: Here we will connect the LLM later.
        # For now, let's just print the agent's status to verify creation.
        print(f"Agent {self.unique_id}: {self.persona_description} (Budget: {self.budget})")