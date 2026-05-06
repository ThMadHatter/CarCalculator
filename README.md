# Car Cost Estimator

This application helps users estimate the total cost of owning a car over time, comparing it with renting and analyzing the impact of loans, maintenance, and inflation.

## How to use the app

1.  **Vehicle Information**: Enter the brand, model, and any specific details of the car you are interested in.
2.  **Registration and Ownership**: Select the car's registration year, how long you plan to own it, and how old it will be when you purchase it.
3.  **Location**: Provide your ZIP code or location to get regional price estimates.
4.  **Financial Parameters**:
    *   **Monthly Maintenance**: Estimated monthly cost for upkeep.
    *   **Inflation Rate**: Annual inflation rate to be applied to maintenance costs.
    *   **Loan Details**: If you are financing the car, enter the loan value, annual interest rate, and duration in years.
5.  **Price Data**:
    *   By default, the app fetches real-time price data from AutoScout24.
    *   **Extend missing values**: If enabled, the app will attempt to fill in gaps in historical price data using interpolation and extrapolation.
6.  **Simulate Car Costs**: Click this button to generate a detailed breakdown of monthly depreciation, maintenance, and loan payments.
7.  **Compare to Renting**: Use this feature to see a break-even analysis between owning the selected vehicle and renting one at a specified monthly cost.

## Hosted App

The application is hosted at: [https://carcalculatorsite.onrender.com/](https://carcalculatorsite.onrender.com/)

## Features

*   Real-time price fetching from AutoScout24.
*   Inflation-adjusted maintenance cost calculations.
*   Amortizing loan calculator integrated into total ownership costs.
*   Break-even analysis comparing buying vs. renting.
*   Visualizations of car value depreciation over time.
