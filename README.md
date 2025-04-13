# Gridcog - Optimisation test - April 2025 - Sam MacIntyre

## Problem context

- Customer in VIC, Australia considering intalling 250 kW/500 kWh battery and solar panel to reduce energy costs on an office building
- Peak power charges apply, $12/kW on weekdays, 3$7kW on weekends. Power calculated by averaging half-hourly energy import values.
- We will assume equal charge and discharge efficiency of $\eta = 0.95$


## Repository structure
```
├── data/                     # Input data (load, solar, pricing)
├── results/
├── results_1_week/               # Generated result tables and plots (.csv)
├── plots/                    # All output plots (.png)
│   ├── soc.png
│   ├── import_export.png
│   ├── net_load.png
│   ├── monthly_savings.png
│   └── ...
├── main.py                   # Model creation and solving
├── results.py                # Plots and cost comparison logic
├── validation.py             # Model verification (SOC, power balance)
├── requirements.txt          # Dependencies
└── README.md                 # You're here
```




## Data processing steps

1. Firstly, given 2024 is a leap year, for simplicity we do not consider February 29 in the analysis
2. All data is converted to GMT+10 timezone
3. If necessary, data is mean resampled to 30m intervals
4. Timezone localisation dropped for input into model
5. In load data case, first two entries moved to end of dataset due to timezone shift

## Modelling approach

The **MILP** is set up using the linopy package

1. Firstly set up variables for battery state of charge, battery charge power, battery discharge power, peak weekday power, peak weekend power, grid export power and grid import power.
2. Then add constraints for:
   - Battery state of charge update
   - Power balance
   - Max grid export limit
   - Monthly max peak power values
3. I have demonstrated how to add binary constraints to ensure that the battery does not charge or discharge simultaneously, but have deactivated them as the run time increased significantly.
4. Objective function which includes grid import costs, grid export revenues and peak monthly power values is added.
5. Model is solved by HIGHs solver and results extracted


## Outputs - 1 week model

To see more clearly the optimised behaviour, we can show the results from a 1 week run of the model, before presenting the full results.





### 📊 Monthly Cost Breakdown

Here’s an example of the monthly cost breakdown from the optimization results:

![Monthly Cost Breakdown](results/monthly_cost_breakdown.png)

### 💰 Monthly Cost Savings

![Monthly Savings](results/monthly_savings.png)

## 📈 Other Visualizations

- **Battery State of Charge Over Time**

  ![SoC](results_1_week/soc.png)

- **Load and Solar Production**

  ![Load and Solar](results_1_week/load_solar.png)

- **Battery Charge/Discharge Behavior**

  ![Charge/Discharge](results_1_week/charge_discharge.png)

## 📄 Summary CSVs

- [Monthly Cost Summary](results/monthly_cost_summary.csv)
- [Monthly Cost Breakdown](results/monthly_cost_breakdown.csv)

> To view these CSVs, open them in Excel or use pandas in Python.
