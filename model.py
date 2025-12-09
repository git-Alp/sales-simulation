from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import ConsumerAgent

class FlashSaleModel(Model):
    """
    The main simulation model representing the 'Flash Sale' market environment.
    It manages the global state (stock, time, price) and the agents.
    """

    def __init__(self, N=10, initial_stock=5, time_limit=20):
        # --- Parameters ---
        self.num_agents = N
        self.stock = initial_stock
        self.time_left = time_limit
        self.initial_time = time_limit
        self.is_active = True
        
        # --- Scheduler ---
        # RandomActivation means agents act in random order each step (fairness).
        self.schedule = RandomActivation(self)
        self.journal = []
        
        # --- Create Agents ---
        for i in range(self.num_agents):
            a = ConsumerAgent(i, self)
            self.schedule.add(a)

        # --- Data Collector ---
        # This records data at every step so we can analyze it later (or plot charts).
        self.datacollector = DataCollector(
            model_reporters={
                "Stock": "stock",
                "Time": "time_left",
                "Sales": lambda m: initial_stock - m.stock
            }
        )

    def step(self):
        """
        Advance the model by one step (e.g., 1 minute or 1 tick).
        """
        
        # 1. Check if the sale should end
        if self.stock <= 0:
            self.is_active = False
            print("--- SOLD OUT! Simulation Ending. ---")
            
        if self.time_left <= 0:
            self.is_active = False
            print("--- TIME UP! Simulation Ending. ---")

        # If sale is over, stop collecting data and return
        if not self.is_active:
            return

        # 2. Collect Data (Record current stock level)
        self.datacollector.collect(self)

        # 3. Agents Act (Everyone makes a decision)
        self.schedule.step()

        # 4. Decrease Timer
        self.time_left -= 1
        
        # (Optional) Log progress to console
        print(f"Tick: {self.initial_time - self.time_left} | Stock: {self.stock} | Time Left: {self.time_left}")