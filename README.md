# Flash Sale Agent-Based Model (ABM) Simulation

A multi-agent simulation studying consumer behavior during flash sales using LLM-powered agents. This project compares how different demographic segmentation strategies (persona, age, education) influence purchasing decisions under time and stock pressure.

## 📋 Project Overview

### What It Does
* **Simulates a flash sale** with limited stock and time constraints.
* **Creates agents** with realistic budgets, personalities, and demographics.
* **Uses Google Vertex AI Gemini LLM** to make individualized purchase decisions.
* **Compares three variants** to understand which segmentation strategy best predicts buyer behavior:
  * **Persona Model**: Agents classified by impulsivity (Impulsive, Moderate, Careful).
  * **Age Model**: Agents classified by age group (18-29, 30-44, 45-59, 60-80).
  * **Education Model**: Agents classified by education level.

### Key Features
✅ Synchronous LLM calls with rate limiting  
✅ Batched agent processing to manage API limits  
✅ Comprehensive decision tracking and statistics  
✅ Budget constraints and stock scarcity dynamics  
✅ Realistic behavioral prompts accounting for time pressure  
✅ Detailed logging and performance metrics  

---

## 📁 Project Structure

```text
sales-simulation/
├── main.py          # Entry point & simulation runner
├── model.py         # Mesa Model (FlashSaleModel) - game logic
├── agent.py         # ConsumerAgent - LLM-powered decision making
├── .env             # Environment configuration (not in repo)
├── logs/            # Simulation logs (auto-generated)
└── README.md        # This file
```

## 🔄 How It Works

### The Simulation Flow

**1. INITIALIZATION**
* Create `N` agents with randomized attributes:
  * **Budget:** 2,000 - 8,000 TL
  * **Age:** 18 - 80 years old
  * **Education Level:** High School, Bachelors, Masters, etc.
  * **Impulsivity Score:** 0.0 to 1.0

⬇️

**2. SIMULATION LOOP (Each Tick = 1 minute)**
* **Check end conditions:**
  * Is `Stock == 0`? ➔ **SOLD OUT** (End)
  * Is `Time == 0`? ➔ **TIME UP** (End)
* **Process agents in batches:**
  * Build LLM prompt with context
  * Call Gemini API for decision
  * Parse response (`BUY` or `NO`)
  * Check constraints (budget, stock)
  * Execute purchase if valid
  * Record metrics
* **Decrease time counter**

⬇️

**3. FINALIZATION**
* Print final statistics & breakdown by segment.

---

## 🚀 Setup

### Prerequisites
* **Python:** 3.10+
* **Google Cloud:** Project with Vertex AI enabled
* **Credentials:** Service account credentials or `gcloud` CLI

### 1. Clone & Install

```bash
git clone <repo-url>
cd sales-simulation
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 2️⃣ Create `.env` File
Create a `.env` file in the root directory to configure the simulation:

```env
# --- Required ---
GOOGLE_PROJECT_ID=your-project-id

# --- Optional (Defaults provided) ---
GOOGLE_LOCATION=us-central1
AGENT_MODEL_ID=gemini-2.0-flash
NUM_AGENTS=1000
INITIAL_STOCK=100
TIME_LIMIT=60
BATCH_SIZE=20
BATCH_PAUSE_MIN=0.1
BATCH_PAUSE_MAX=0.3
SIMULATION_MODE=compare
VARIANT_COOLDOWN_SEC=10
```

## ▶️ Running Simulations
### 🏃‍♂️ Quick Test (Single Variant)
Test with small numbers before running the full simulation to ensure API connections work:

```bash
SIMULATION_MODE=single NUM_AGENTS=10 INITIAL_STOCK=20 TIME_LIMIT=15 python3 main.py
```

## 📊 Understanding Output
### 🖥️ Console Output Example
The simulation provides real-time progress and a detailed breakdown of the results.
```text
============================================================
Starting Flash Sale ABM Simulation (Persona Model)
============================================================
Agents: 100 | Stock: 100 | Duration: 60 minutes | Batch: 20 | Variant: persona
Stock-to-Agent Ratio: 100.0%
============================================================

Processing batch 1/5 (20 agents)
[Progress:persona] Tick 10/60 | Sold: 15/100 | Stock: 85
[Progress:persona] Tick 20/60 | Sold: 32/100 | Stock: 68
[Progress:persona] Tick 30/60 | Sold: 50/100 | Stock: 50

--- FINAL RESULTS ---
Variant: persona
Total Sales: 75/100 (75.0%)
Remaining Stock: 25
Duration: 45 ticks
Sales per Tick: 1.67
Total BUY intents: 92
Total NO intents: 2408
Total purchases completed: 75
Total stock-blocked BUY intents: 15
Total budget-blocked BUY intents: 2

--- PERSONA BREAKDOWN ---
Careful: Created=35 | Purchased=20 | BudgetBlockedOccurrences=0 | BudgetBlockedUniqueAgents=0
Impulsive: Created=32 | Purchased=30 | BudgetBlockedOccurrences=2 | BudgetBlockedUniqueAgents=2
Moderate: Created=33 | Purchased=25 | BudgetBlockedOccurrences=0 | BudgetBlockedUniqueAgents=0

--- COMPARISON SUMMARY ---
Persona Model    | Sales=75 | BUY intents=92  | Purchases=75 | BudgetBlocked=2 | StockBlocked=15
Age Model        | Sales=82 | BUY intents=105 | Purchases=82 | BudgetBlocked=3 | StockBlocked=20
Education Model  | Sales=78 | BUY intents=96  | Purchases=78 | BudgetBlocked=2 | StockBlocked=16
```

## 🧠 How Agents Decide

### ⚙️ The Decision-Making Process
1. **Observation:** Agent observes market state (Remaining stock percentage, remaining time, current price).
2. **Prompt Engineering:** Build the LLM prompt combining the agent's budget, demographic profile, market pressure, and behavioral traits.
3. **API Call:** Send the prompt to Vertex AI Gemini.
4. **Parsing:** Extract the binary decision (`BUY` or `NO`) and the reasoning behind it.
5. **Constraint Check:** * *Has budget?* (Budget ≥ 3500 TL)
   * *Stock available?* (Stock > 0)
6. **Execution:** Execute the purchase if valid; record it as "blocked" if constraints fail.
7. **Logging:** Update metrics and save the decision to the simulation log.

### 🎭 Agent Profiles

* ⚡ **Impulsive Agent** *(Impulsivity > 0.8)*
  * **Budget:** 2,000-8,000 TL
  * **Traits:** Quick decisions, FOMO-driven, highly susceptible to urgency.
  * *Example Thought:* "Stock is critically low! I must buy now before it's gone!"
* 🛡️ **Careful Agent** *(Impulsivity < 0.3)*
  * **Budget:** 2,000-8,000 TL
  * **Traits:** Analytical, thorough evaluation, resistant to time pressure.
  * *Example Thought:* "I need to carefully analyze if this purchase is truly necessary despite the discount..."
* ⚖️ **Moderate Agent** *(0.3 ≤ Impulsivity ≤ 0.8)*
  * **Budget:** 2,000-8,000 TL
  * **Traits:** Balanced emotion + logic, influenced by both value and urgency.
  * *Example Thought:* "It's a good deal and time is limited, I'll make the purchase."

---

## 📚 Technical Details

### 💻 Technologies Used
* **Mesa:** Agent-based modeling framework
* **Vertex AI Gemini:** LLM for agent cognitive decisions
* **LangChain:** LLM prompt management and chaining
* **Python Logging:** Comprehensive event and error tracking
* **DataCollector:** Time-series metrics collection for analysis

### 🏗️ Key Design Decisions
* **Synchronous Processing:** Sequential LLM calls (no async) to ensure strict reproducibility.
* **Batching:** Groups agents (e.g., 20 agents/batch) to respect Google API rate limits.
* **Shared LLM Instance:** A single model instance is reused across agents to optimize memory.
* **Safety Settings:** Disabled to allow open commercial/sales discussions without false flags.
* **Detailed Prompts:** Full context injected (market state + agent profile) for higher-quality decisions.

### ⏱️ Performance Notes
* **Duration:** 1000 agents × 60 ticks ≈ 5-10 minutes per variant (heavily depends on batch size).
* **Rate Limiting:** Batch pause of ~50ms per agent in a batch.
* **Cooldowns:** 10 seconds variant cooldown between comparison runs (adjustable).
* **API Volume:** ~60,000 calls per full comparison (1000 agents × 60 ticks × 3 variants ÷ 3 per batch).

---

## 📂 Project Structure Details

* **`main.py`**: CLI entry point with parameter parsing. Manages "single" vs "compare" modes, handles cooldowns between variants, and prints formatted results.
* **`model.py`** (`FlashSaleModel`): Core Mesa Model. Manages stock, time, agent list, tracks metrics (purchases, blocks, intents), records decisions to journal, and implements `step()` for tick progression.
* **`agent.py`** (`ConsumerAgent`): Mesa Agent with LLM. Builds persona-aware prompts, calls Vertex AI Gemini API, parses decisions + reasoning, and enforces budget & stock constraints.

---

## 🎓 Research Applications

This simulation can be used to:
* ✅ Study the impact of demographic segmentation on conversion rates.
* ✅ Analyze the FOMO and scarcity effect on different buyer types.
* ✅ Test marketing strategies (persona-based vs. age-based vs. education-based).
* ✅ Model budget constraint effects across diverse populations.
* ✅ Generate synthetic training data for behavioral economics research.
* ✅ Validate traditional consumer behavior theories using LLM agents.

---

## 🔮 Future Enhancements
* Async LLM calls for 10x speed improvement.
* Dynamic pricing models based on real-time demand.
* Agent-to-agent social influence (word-of-mouth).
* Multi-product scenarios and cross-selling.
* Statistical significance testing for variant comparison.
* Export detailed data to CSV/JSON formats.
* Web UI for intuitive parameter tuning.
* Real-time visualization dashboard.

---

## 📄 License
MIT License - Open source and free to use.

## 👤 Author
Built for Master's Thesis on Agent-Based Modeling research.

**Last Updated:** 2026-03-23  
**Version:** 1.0  
**Status:** Production Ready