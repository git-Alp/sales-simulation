# ABM Simulation Scenarios for Master's Thesis

## Realistic Scenarios to Test

### Scenario 1: High Demand Flash Sale (Default)
```bash
export NUM_AGENTS=1000
export INITIAL_STOCK=100
export TIME_LIMIT=60
python main.py
```
- **Purpose**: Standard flash sale with 10% stock-to-agent ratio
- **Expected**: High competition, quick sellout

### Scenario 2: Large-Scale E-commerce Event
```bash
export NUM_AGENTS=5000
export INITIAL_STOCK=500
export TIME_LIMIT=120
python main.py
```
- **Purpose**: Major online shopping event (Black Friday scale)
- **Expected**: Sustained buying activity over longer period

### Scenario 3: Limited Drop (Scarcity Focus)
```bash
export NUM_AGENTS=2000
export INITIAL_STOCK=50
export TIME_LIMIT=30
```
- **Purpose**: High scarcity (2.5% stock ratio) to study FOMO
- **Expected**: Intense early buying pressure

### Scenario 4: Extended Sale Window
```bash
export NUM_AGENTS=1000
export INITIAL_STOCK=200
export TIME_LIMIT=180
```
- **Purpose**: Lower urgency, more thoughtful decisions
- **Expected**: Gradual sales, more careful buyers

### Scenario 5: Massive Audience Test
```bash
export NUM_AGENTS=10000
export INITIAL_STOCK=1000
export TIME_LIMIT=90
```
- **Purpose**: Stress test and study large-scale behavior
- **Expected**: Performance limits, realistic e-commerce scale

## Research Questions to Explore

1. **How does scarcity affect buyer behavior?**
   - Compare scenarios 1, 3, 4

2. **Do impulsive vs careful buyers respond differently to time pressure?**
   - Analyze persona breakdowns across scenarios

3. **What is the optimal stock-to-agent ratio for sales velocity?**
   - Test 5%, 10%, 20%, 40% ratios

4. **Does urgency create irrational purchases?**
   - Compare budget utilization across time limits

## Performance Notes

- **1,000 agents**: ~1-2 minutes runtime
- **5,000 agents**: ~5-10 minutes runtime  
- **10,000 agents**: ~15-20 minutes runtime

Each agent makes an LLM call, so runtime scales with agent count.
