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
        
        self.llm = ChatOllama(model="llama3.2", temperature=0.7)

    def step(self):
        if self.has_bought or self.model.stock <= 0:
            return

        prompt = f"""
        You are {self.persona}, Budget: {self.budget} TL.
        Product: Premium Headphones. Price: 2500 TL (Normal: 5000 TL).
        Stock: {self.model.stock} left. Time: {self.model.time_left} mins.
        
        Strictly decide based on your budget and personality.
        If Budget < 2500, you CANNOT buy.
        Answer ONLY in this format: "DECISION: [BUY/NO] | REASON: [Short reason]"
        """

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Logging (Save the thought to the model)
            self.model.journal.append(f"Agent {self.unique_id} ({self.persona}): {content}")

            if "DECISION: BUY" in content:
                self._buy_product()
                
        except Exception as e:
            print(f"Error: {e}")

    def _buy_product(self):
        if self.model.stock > 0:
            self.model.stock -= 1
            self.has_bought = True