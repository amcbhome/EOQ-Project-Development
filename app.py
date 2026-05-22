import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Supermarket BI Tool", layout="wide")

st.title("🛒 Supermarket Business Intelligence: Live EOQ Model")
st.write(
    "Adjust the **Daily Shrinkage (%)** column directly in the table below to see the real-time impact on optimal order quantities."
)

# 1. Define the foundational data structure (Long Format)
initial_data = {
    "SKU": ["SKU_A", "SKU_B", "SKU_C"],
    "Product Name": ["Fresh Avocados", "Premium Olive Oil", "Boxed Cereal"],
    "Unit Cost ($)": [1.00, 8.00, 2.00],
    "Daily Demand": [200, 30, 100],
    "Ordering Cost ($)": [25.00, 15.00, 20.00],
    "Daily Base Holding Cost ($)": [0.01, 0.05, 0.03],
    "Daily Shrinkage (%)": [2.0, 0.5, 0.1],  # User editable starting percentage
}

df_initial = pd.DataFrame(initial_data)

# 2. Render the interactive data editor
edited_df = st.data_editor(
    df_initial,
    disabled=[
        "SKU",
        "Product Name",
        "Unit Cost ($)",
        "Daily Demand",
        "Ordering Cost ($)",
        "Daily Base Holding Cost ($)",
    ],
    hide_index=True,
    use_container_width=True,
)


# 3. Process calculations based on the live table state
def process_inventory_logic(df):
    # Convert shrinkage percentage back to a decimal
    shrinkage_decimal = df["Daily Shrinkage (%)"] / 100.0

    # Calculate Adjusted Daily Holding Cost: Base + (Unit Cost * Shrinkage Rate)
    df["Adj. Daily Holding Cost ($)"] = df["Daily Base Holding Cost ($)"] + (
        df["Unit Cost ($)"] * shrinkage_decimal
    )

    # Annualize variables for standard EOQ formula (365 days)
    annual_demand = df["Daily Demand"] * 365
    annual_holding_cost = df["Adj. Daily Holding Cost ($)"] * 365

    # Apply EOQ math: sqrt((2 * D * S) / H)
    eoq_math = np.sqrt(
        (2 * annual_demand * df["Ordering Cost ($)"]) / annual_holding_cost
    )
    df["Live EOQ (Units)"] = np.round(eoq_math).astype(int)

    # Calculate financial loss metric (Monthly Cost of Shrinkage)
    df["Monthly Shrinkage Loss ($)"] = (
        df["Daily Demand"] * df["Unit Cost ($)"] * shrinkage_decimal * 30
    )

    return df


# Run calculations on the edited data
output_df = process_inventory_logic(edited_df)

# 4. Display the calculated results side-by-side
st.subheader("📊 Optimization & Financial Metrics")

# Formatting columns for display
display_df = output_df[
    [
        "SKU",
        "Product Name",
        "Adj. Daily Holding Cost ($)",
        "Live EOQ (Units)",
        "Monthly Shrinkage Loss ($)",
    ]
].copy()

st.dataframe(
    display_df.style.format(
        {
            "Adj. Daily Holding Cost ($)": "${:.3f}",
            "Monthly Shrinkage Loss ($)": "${:.2f}",
            "Live EOQ (Units)": "{:,}",
        }
    ),
    hide_index=True,
    use_container_width=True,
)
