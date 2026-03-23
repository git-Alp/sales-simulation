from model import FlashSaleModel
import os
import time

# --- CONFIGURATION ---
# Realistic parameters for master's thesis on ABM
NUMBER_OF_AGENTS = int(os.getenv("NUM_AGENTS", "1000"))  # Realistic online flash sale audience
INITIAL_STOCK = int(os.getenv("INITIAL_STOCK", "100"))   # Realistic product inventory (10% stock-to-agent ratio)
TIME_LIMIT = int(os.getenv("TIME_LIMIT", "60"))          # 60 minutes = realistic flash sale duration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))         # Number of agents to process in parallel per batch
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "compare")
VARIANT_COOLDOWN_SEC = float(os.getenv("VARIANT_COOLDOWN_SEC", "10"))


def print_segment_breakdown(model):
    print(f"\n--- {model.segment_label_name.upper()} BREAKDOWN ---")
    for segment, created in sorted(model.persona_counts.items()):
        purchased = model.purchased_counts.get(segment, 0)
        budget_blocked_occ = model.budget_blocked_counts.get(segment, 0)
        budget_blocked_unique = len(model._budget_blocked_agents.get(segment, set()))
        print(
            f"{segment}: Created={created} | Purchased={purchased} | "
            f"BudgetBlockedOccurrences={budget_blocked_occ} | BudgetBlockedUniqueAgents={budget_blocked_unique}"
        )


def cooldown_between_variants(previous_variant, next_variant):
    if VARIANT_COOLDOWN_SEC <= 0:
        return
    print(
        f"\nCooling down for {VARIANT_COOLDOWN_SEC:.1f} seconds between {previous_variant} and {next_variant} to ease Vertex AI rate limits..."
    )
    time.sleep(VARIANT_COOLDOWN_SEC)


def run_single_simulation(prompt_variant, title):
    print(f"\n{'='*60}")
    print(title)
    print(f"{'='*60}")
    print(
        f"Agents: {NUMBER_OF_AGENTS} | Stock: {INITIAL_STOCK} | Duration: {TIME_LIMIT} minutes | "
        f"Batch: {BATCH_SIZE} | Variant: {prompt_variant}"
    )
    print(f"Stock-to-Agent Ratio: {(INITIAL_STOCK/NUMBER_OF_AGENTS)*100:.1f}%")
    print(f"{'='*60}\n")

    model = FlashSaleModel(
        N=NUMBER_OF_AGENTS,
        initial_stock=INITIAL_STOCK,
        time_limit=TIME_LIMIT,
        batch_size=BATCH_SIZE,
        prompt_variant=prompt_variant,
    )

    tick = 0
    while model.is_active:
        model.step()
        if not model.is_active:
            break
        tick += 1
        if tick % 10 == 0:
            sold = INITIAL_STOCK - model.stock
            print(f"[Progress:{prompt_variant}] Tick {tick}/{TIME_LIMIT} | Sold: {sold}/{INITIAL_STOCK} | Stock: {model.stock}")

    if tick == 0 and (INITIAL_STOCK - model.stock) > 0:
        tick = 1

    data = model.datacollector.get_model_vars_dataframe()
    final_sales = INITIAL_STOCK - model.stock
    sales_rate = (final_sales / INITIAL_STOCK) * 100 if INITIAL_STOCK else 0

    print("\n--- FINAL RESULTS ---")
    print(f"Variant: {prompt_variant}")
    print(f"Total Sales: {final_sales}/{INITIAL_STOCK} ({sales_rate:.1f}%)")
    print(f"Remaining Stock: {model.stock}")
    print(f"Duration: {tick} ticks")
    print(f"Sales per Tick: {final_sales/tick:.2f}" if tick else "Sales per Tick: 0.00")
    print(f"Total BUY intents: {model.intent_counts.get('BUY', 0)}")
    print(f"Total NO intents: {model.intent_counts.get('NO', 0)}")
    print(f"Total purchases completed: {sum(model.purchased_counts.values())}")
    print(f"Total stock-blocked BUY intents: {model.stock_blocked_intents}")
    print(f"Total budget-blocked BUY intents: {model.budget_blocked_total}")
    print_segment_breakdown(model)
    print("\n--- LAST 5 TICKS DATA ---")
    print(data.tail())
    print(f"\n{'='*60}\n")

    return {
        "variant": prompt_variant,
        "sales": final_sales,
        "remaining_stock": model.stock,
        "ticks": tick,
        "buy_intents": model.intent_counts.get("BUY", 0),
        "no_intents": model.intent_counts.get("NO", 0),
        "purchases": sum(model.purchased_counts.values()),
        "stock_blocked": model.stock_blocked_intents,
        "budget_blocked": model.budget_blocked_total,
    }

def run_simulation():
    if SIMULATION_MODE == "single":
        run_single_simulation("persona", "Starting Flash Sale ABM Simulation (Persona Model)")
        return

    baseline = run_single_simulation("persona", "Starting Flash Sale ABM Simulation (Persona Model)")
    cooldown_between_variants("persona", "age")
    age_model = run_single_simulation("age", "Starting Flash Sale ABM Simulation (Age Model)")
    cooldown_between_variants("age", "education")
    education_model = run_single_simulation("education", "Starting Flash Sale ABM Simulation (Education Model)")

    print("\n--- COMPARISON SUMMARY ---")
    print(
        f"Persona Model | Sales={baseline['sales']} | BUY intents={baseline['buy_intents']} | "
        f"NO intents={baseline['no_intents']} | Purchases={baseline['purchases']} | "
        f"BudgetBlocked={baseline['budget_blocked']} | StockBlocked={baseline['stock_blocked']}"
    )
    print(
        f"Age Model     | Sales={age_model['sales']} | BUY intents={age_model['buy_intents']} | "
        f"NO intents={age_model['no_intents']} | Purchases={age_model['purchases']} | "
        f"BudgetBlocked={age_model['budget_blocked']} | StockBlocked={age_model['stock_blocked']}"
    )
    print(
        f"Education Model | Sales={education_model['sales']} | BUY intents={education_model['buy_intents']} | "
        f"NO intents={education_model['no_intents']} | Purchases={education_model['purchases']} | "
        f"BudgetBlocked={education_model['budget_blocked']} | StockBlocked={education_model['stock_blocked']}"
    )

if __name__ == "__main__":
    run_simulation()