# ⚡ Flash Sale Simulation with AI Agents

An Agent-Based Modeling (ABM) simulation that explores consumer behavior during a high-stakes "Flash Sale" event. This project uses **Large Language Models (LLMs)** to give each agent a unique personality, budget, and decision-making capability.

Built with **Python**, **Mesa**, **LangChain**, and **Streamlit**. Powered locally by **Ollama (Llama 3.2)**.

## 🚀 Features

* **🧠 AI-Powered Agents:** Each consumer agent has a distinct personality ("Impulsive" vs. "Careful") and financial situation. They use an LLM to reason before buying.
* **🏠 100% Local & Privacy-Focused:** Runs entirely on your machine using Ollama. No API keys or cloud costs required.
* **📊 Real-Time Dashboard:** Interactive Streamlit interface to visualize stock depletion, sales velocity, and agent thought processes.
* **📉 Scarcity Dynamics:** Simulates the "Fear Of Missing Out" (FOMO) as stock and time run out.

## 🛠️ Tech Stack

* **Simulation Core:** [Mesa](https://mesa.readthedocs.io/en/main/)
* **LLM Integration:** [LangChain](https://www.langchain.com/)
* **Local LLM Runner:** [Ollama](https://ollama.com/)
* **Visualization:** [Streamlit](https://streamlit.io/)

---

## ⚙️ Installation & Setup

Follow these steps to get the simulation running on your machine.

### 1. Prerequisites

* **Python 3.9+** installed.
* **Ollama** installed.

### 2. Install & Configure Ollama (The Brain)

This project requires a local LLM to function.

1.  Download Ollama from [ollama.com](https://ollama.com).
2.  Install and run the application.
3.  Open your terminal and pull the `llama3.2` model (lightweight and fast):

```bash
ollama run llama3.2
```
*Note: Keep the Ollama app running in the background while using the simulation.*

### 3. Clone the Repository

```bash
git clone https://github.com/git-Alp/sales-simulation.git
cd sales-simulation
```

### 4. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**For macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Once everything is installed and Ollama is running in the background:

1.  Start the Streamlit dashboard:
    ```bash
    streamlit run app.py
    ```

2.  A new tab will open in your browser (usually at `http://localhost:8501`).
3.  Use the sidebar to adjust parameters:
    * **Number of Agents:** How many buyers are in the market.
    * **Stock Quantity:** How scarce the item is.
    * **Simulation Speed:** Control the flow of time.
4.  Click **"Start Simulation"** and watch the agents decide!

---

## 📂 Project Structure

```text
sales-simulation/
├── app.py           # The Streamlit dashboard and visualization logic
├── model.py         # The environment/market logic (Mesa Model)
├── agent.py         # The consumer agent logic & LLM connection
├── main.py          # (Optional) CLI version of the simulation
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
```

## 🤝 Contributing

Feel free to fork this repository and submit pull requests. Ideas for improvement:
* Add different types of promotion strategies (e.g., "Buy 1 Get 1").
* Visualize social influence (agents talking to each other).
* Add different LLM models support.

## 📜 License

This project is open-source and available under the MIT License.