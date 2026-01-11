from model import FlashSaleModel

# --- CONFIGURATION ---
NUMBER_OF_AGENTS = 150     # Let's start small
INITIAL_STOCK = 10        # High scarcity (FOMO trigger)
TIME_LIMIT = 20          # Short duration

def run_simulation():
    print("Starting Flash Sale Simulation...")
    
    # Initialize the model
    model = FlashSaleModel(
        N=NUMBER_OF_AGENTS, 
        initial_stock=INITIAL_STOCK, 
        time_limit=TIME_LIMIT
    )

    # Run the simulation loop
    while model.is_active:
        model.step()

    print("Simulation Finished.")
    
    # Show final results
    # We can access the data collected by DataCollector
    data = model.datacollector.get_model_vars_dataframe()
    print("\n--- FINAL DATA SUMMARY ---")
    print(data.tail()) # Print last 5 rows

if __name__ == "__main__":
    run_simulation()