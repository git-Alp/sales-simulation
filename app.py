import streamlit as st
import time
import pandas as pd
from model import FlashSaleModel

st.set_page_config(page_title="Flash Sale Simulator ⚡", layout="wide")

st.title("⚡ AI Agent 'Flash Sale' Simulation")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    num_agents = st.slider("Number of Customers", 5, 50, 30)
    stock_count = st.slider("Stock Quantity", 1, 50, 15)
    time_limit = st.slider("Duration (Min)", 5, 60, 30)
    speed = st.slider("Speed", 0.1, 2.0, 0.5)
    start_btn = st.button("Start Simulation", type="primary")

if start_btn:
    model = FlashSaleModel(N=num_agents, initial_stock=stock_count, time_limit=time_limit)
    
    # --- INTERFACE LAYOUT (3 Columns) ---
    col_kpi, col_chart, col_logs = st.columns([1, 2, 2])

    with col_kpi:
        st.subheader("📊 Situation")
        kpi_stock = st.empty()
        kpi_sales = st.empty()
        kpi_time = st.empty()
    
    with col_chart:
        st.subheader("📉 Stock Meltdown")
        chart_place = st.empty()
    
    with col_logs:
        st.subheader("💭 Agent Thoughts")
        log_place = st.empty()

    sales_data = []
    all_logs = []

    while model.is_active:
        model.step()
        
        # 1. Update KPI
        remaining = model.stock
        sold = stock_count - remaining
        kpi_stock.metric("Remaining Stock", remaining)
        kpi_sales.metric("Sold", sold)
        kpi_time.metric("Time", f"{model.time_left} dk")

        # 2. Update Chart
        sales_data.append({"Tick": model.initial_time - model.time_left, "Stok": remaining})
        df = pd.DataFrame(sales_data).set_index("Tick")
        chart_place.line_chart(df, height=250)

        # 3. Update Logs (Newest at the top)
        if model.journal:
            for log in model.journal:
                # Coloring
                if "DECISION: BUY" in log:
                    all_logs.insert(0, f"🟢 {log}")
                else:
                    all_logs.insert(0, f"⚪ {log}")
            
            model.journal = []
            
            # Press screen
            with log_place.container(height=400):
                for line in all_logs:
                    st.text(line)

        time.sleep(speed)

    st.success("SIMULATION IS OVER!")