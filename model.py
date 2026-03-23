from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import ConsumerAgent, logger
import random
import time
import os
import math
from collections import Counter, defaultdict

class FlashSaleModel(Model):
    """
    The main simulation model representing the 'Flash Sale' market environment.
    It manages the global state (stock, time, price) and the agents.
    """

    def __init__(self, N=10, initial_stock=5, time_limit=20, batch_size=100, product_price=3500, prompt_variant="persona"):
        super().__init__()  # Initialize Mesa Model properly
        # --- Parameters ---
        self.num_agents = N
        self.stock = initial_stock
        self.initial_stock = initial_stock
        self.time_left = time_limit
        self.initial_time = time_limit
        self.is_active = True
        self.batch_size = batch_size  # Number of agents to process in parallel
        self.product_price = product_price
        self.prompt_variant = prompt_variant
        if prompt_variant == "persona":
            self.segment_label_name = "Persona"
        elif prompt_variant == "age":
            self.segment_label_name = "Age Group"
        else:
            self.segment_label_name = "Education"
        self.batch_pause_min = float(os.getenv("BATCH_PAUSE_MIN", "0.1"))
        self.batch_pause_max = float(os.getenv("BATCH_PAUSE_MAX", "0.3"))

        # NEW: tracking counters
        self.persona_counts = Counter()
        self.intent_counts = Counter()  # counts of intents BUY/NO
        self.purchased_counts = Counter()  # counts of actual purchases by persona
        self.budget_blocked_counts = Counter()  # intents blocked by budget (occurrences)
        self.budget_blocked_total = 0  # total budget-blocked intent occurrences
        # Track unique agents that experienced budget blocks per persona
        self._budget_blocked_agents = defaultdict(set)
        self.stock_blocked_intents = 0
        # Track seen agent ids to avoid double-counting personas across ticks
        self._seen_agents = {}

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
        logger.info(
            f"FlashSaleModel initialized: agents={N}, stock={initial_stock}, time_limit={time_limit}, batch_size={batch_size}, variant={prompt_variant}"
        )

    def step(self):
        """
        Advance the model by one step (e.g., 1 minute or 1 tick).
        """
        
        # 1. Check if the sale should end
        if self.stock <= 0:
            self.is_active = False
            logger.info("--- SOLD OUT! Simulation Ending. ---")
            self.finish()
            return

        if self.time_left <= 0:
            self.is_active = False
            logger.info("--- TIME UP! Simulation Ending. ---")
            self.finish()
            return

        # If sale is over, stop collecting data and return
        if not self.is_active:
            return

        # 2. Collect Data (Record current stock level)
        self.datacollector.collect(self)

        # 3. Agents Act (Everyone makes a decision) - BATCHED
        self._step_agents_batched()

        # 4. Decrease Timer
        self.time_left -= 1
        
        # Log progress
        logger.info(f"Tick: {self.initial_time - self.time_left} | Stock: {self.stock} | Time Left: {self.time_left}")
    
    def _step_agents_batched(self):
        """Process agents in batches synchronously"""
        agents = list(self.schedule.agents)
        batch_count = math.ceil(len(agents) / self.batch_size)
        
        for i in range(0, len(agents), self.batch_size):
            batch = agents[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            logger.info(f"Processing batch {batch_num}/{batch_count} ({len(batch)} agents)")
            
            for agent in batch:
                agent.step()  # ✅ Sync call
                time.sleep(0.05)  # Rate limiting (50ms)

    def record_decision(self, segment, intent, purchased, budget_blocked=False, agent_id=None):
        """Record an agent's decision and update counters for summaries."""
        # Track persona totals only once per unique agent
        if agent_id is not None:
            if agent_id not in self._seen_agents:
                self._seen_agents[agent_id] = segment
                self.persona_counts[segment] += 1
        else:
            # fallback: increment, but this may double-count across ticks
            self.persona_counts[segment] += 1
        # Track intent totals (BUY/NO)
        self.intent_counts[intent] += 1
        # Track purchases by persona
        if purchased:
            self.purchased_counts[segment] += 1
        # Track budget-blocked intents by persona
        if budget_blocked:
            # occurrence
            self.budget_blocked_counts[segment] += 1
            self.budget_blocked_total += 1
            # unique agent tracking
            if agent_id is not None:
                self._budget_blocked_agents[segment].add(agent_id)
        # Track buy intents that failed due to stock
        if intent == "BUY" and not purchased and not budget_blocked:
            self.stock_blocked_intents += 1
        # Append to journal for later inspection
        try:
            self.journal.append({
                "segment": segment,
                "intent": intent,
                "purchased": purchased,
                "budget_blocked": budget_blocked,
                "stock": self.stock,
                "tick": self.initial_time - self.time_left,
                "variant": self.prompt_variant,
                "agent_id": agent_id,
            })
        except Exception:
            # Be conservative: don't let journaling break the simulation
            pass

    def finish(self):
        # existing termination logging lines...
        logger.info("--- SIMULATION SUMMARY ---")
        logger.info(f"Variant: {self.prompt_variant}")
        total_agents = sum(self.persona_counts.values()) or len(self.schedule.agents)
        logger.info(f"Total agents: {total_agents}")
        for segment, count in sorted(self.persona_counts.items()):
            bought = self.purchased_counts.get(segment, 0)
            budget_blocked_occ = self.budget_blocked_counts.get(segment, 0)
            budget_blocked_unique = len(self._budget_blocked_agents.get(segment, set()))
            logger.info(
                f"{self.segment_label_name} {segment}: {count} agents | Purchased: {bought} | Budget-blocked-intents(occurrences): {budget_blocked_occ} | Budget-blocked-unique-agents: {budget_blocked_unique}"
            )
        total_buy = self.intent_counts.get('BUY', 0)
        total_no = self.intent_counts.get('NO', 0)
        logger.info(f"Total BUY intents (occurrences): {total_buy}")
        logger.info(f"Total NO intents (occurrences): {total_no}")
        # Sanity check: journal length should equal total intents recorded
        total_intents_recorded = total_buy + total_no
        if total_intents_recorded != len(self.journal):
            logger.warning(f"Intent count mismatch: intents={total_intents_recorded} journal_entries={len(self.journal)}")
        logger.info(f"Total purchases completed: {sum(self.purchased_counts.values())}")
        logger.info(f"Total BUY intents blocked by stock: {self.stock_blocked_intents}")
        logger.info(f"Total budget-blocked intents (occurrences): {self.budget_blocked_total}")
        logger.info("----- end summary -----")

        total_intents_recorded = total_buy + total_no
# Note: `finish()` is called from the model's `step()` method above.
        if total_intents_recorded != len(self.journal):
            logger.warning(f"Intent count mismatch: intents={total_intents_recorded} journal_entries={len(self.journal)}")
        logger.info(f"Total purchases completed: {sum(self.purchased_counts.values())}")
        logger.info(f"Total BUY intents blocked by stock: {self.stock_blocked_intents}")
        logger.info(f"Total budget-blocked intents (occurrences): {self.budget_blocked_total}")
        logger.info("----- end summary -----")

# Note: `finish()` is called from the model's `step()` method above.