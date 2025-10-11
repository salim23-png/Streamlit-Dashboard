# ------------
# 0️⃣ Importing Libraries
# ------------
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
# ------------
# 1️⃣ Page Setup
# ------------
st.set_page_config(page_title="ESG & Financial Performance",
                   page_icon="ESG.jpeg",
                   layout="wide")
st.title("ESG & Financial Performance")
# ------------
# 2️⃣ Load Data
# ------------
try:
    df = pd.read_csv("company_esg_financial_dataset.csv")
except FileNotFoundError:
    st.error("❗ File 'company_esg_financial_dataset.csv' Not Found")
    st.stop()
# ------------
# 3️⃣ Add KPI Metrics
# ------------
st.markdown("### Key Performance Indicator (KPI)")
def format_million(value: float) -> str:
    if abs(value) >= 1_000_000:  
        return f"${value / 1_000_000:,.2f}T"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:,.2f}B"
    else:
        return f"${value:,.1f}M"

def format_delta(value: float) -> str:
    if abs(value) >= 1_000:  
        return f"${value / 1_000:,.2f}K"
    else:
        return f"${value:,.1f}"
    
# ------------
# 4️⃣ Aggregating KPI By Year
# ------------
df["CarbonIntensity"] = df["CarbonEmissions"]/df["Revenue"]
kpi = (
    df.groupby("Year")
    .agg({
        "Revenue": "sum",
        "MarketCap": "sum",
        "ProfitMargin": "mean",
        "ESG_Overall": "mean",
        "CarbonIntensity": "mean"
    })
    .reset_index()
)
# ------------
# 5️⃣ Take the Last 2 Years
# ------------
latest_year = kpi["Year"].max()
prev_year = kpi["Year"].nlargest(2).iloc[-1] if len(kpi) > 1 else None

latest_row = kpi.loc[kpi["Year"] == latest_year].iloc[0]
prev_row = kpi.loc[kpi["Year"] == prev_year].iloc[0]

# ------------
# 6️⃣ Count The Different YoY (%)
# ------------
revenue_delta = ((latest_row["Revenue"] - prev_row["Revenue"]))
marketcap_delta = ((latest_row["MarketCap"] - prev_row["MarketCap"]))
margin_delta = ((latest_row["ProfitMargin"] - prev_row["ProfitMargin"]))
esg_delta = ((latest_row["ESG_Overall"] - prev_row["ESG_Overall"]))
carbon_delta = ((latest_row["CarbonIntensity"] - prev_row["CarbonIntensity"]))

revenue_delta_percent = ((latest_row["Revenue"] - prev_row["Revenue"]) / abs(prev_row["Revenue"])) * 100
marketcap_delta_percent = ((latest_row["MarketCap"] - prev_row["MarketCap"]) / abs(prev_row["MarketCap"])) * 100
margin_delta_percent = ((latest_row["ProfitMargin"] - prev_row["ProfitMargin"]) / abs(prev_row["ProfitMargin"])) * 100
esg_delta_percent = ((latest_row["ESG_Overall"] - prev_row["ESG_Overall"]) / abs(prev_row["ESG_Overall"])) * 100
carbon_delta_percent = ((latest_row["CarbonIntensity"] - prev_row["CarbonIntensity"]) / abs(prev_row["CarbonIntensity"])) * 100

revenue_delta_str = f"{revenue_delta:+,.0f} ({revenue_delta_percent:+.2f}%)"
marketcap_delta_str = f"{marketcap_delta:+,.0f} ({marketcap_delta_percent:+.2f}%)"
margin_delta_str = f"{margin_delta:+,.1f} ({margin_delta_percent:+.2f}%)"
esg_delta_str = f"{esg_delta:+,.1f} ({esg_delta_percent:+.2f}%)"
carbon_delta_str = f"{carbon_delta:+,.1f} ({carbon_delta_percent:+.2f}%)"

# ------------
# 7️⃣ KPI Metrics Display
# ------------
col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
col1.metric(label=f"📈 Revenue {latest_year}", value=format_million(latest_row["Revenue"]), 
          delta=revenue_delta_str, delta_color="normal", border=True)
col2.metric(label=f"📊 Market Cap {latest_year}", value=format_million(latest_row["MarketCap"]), 
          delta=marketcap_delta_str, delta_color="normal", border=True)
col3.metric(label=f"💰 Profit Margin {latest_year}", value=f"{latest_row["ProfitMargin"]:.2f}%", 
          delta=margin_delta_str, delta_color="normal", border=True)
col4.metric(label=f"🌿 ESG Score {latest_year}", value=f"{latest_row["ESG_Overall"]:.2f}", 
          delta=esg_delta_str, delta_color="normal", border=True)
col5.metric(label=f"🌎 Carbon Intensity {latest_year}", value=f"{latest_row["CarbonIntensity"]:.2f}", 
          delta=carbon_delta_str, delta_color="normal", border=True)

with st.expander("ℹ️ About Metrics"):
    st.markdown("""
    ### 📊 Financial Performance Metrics
    | Metric | Definition | Formula / Basis | Unit | Interpretation |
    |--------|-------------|-----------------|------|----------------|
    | **Revenue Growth** | The year-over-year change in total revenue. | (Current Revenue − Previous Revenue) / Previous Revenue × 100 | % | Higher growth indicates business expansion and stronger sales performance. |
    | **Profit Margin** | The ratio of net income to total revenue. | Net Income / Revenue × 100 | % | A higher margin reflects better efficiency and profitability. |
    | **Market Capitalization** | The total market value of a company. | Stock Price × Outstanding Shares | USD (Million) | Represents market confidence and company valuation. |

    ---

    ### 🌱 ESG & Sustainability Metrics
    | Metric | Definition | Formula / Basis | Unit | Interpretation |
    |--------|-------------|-----------------|------|----------------|
    | **ESG Score** | Composite score reflecting Environmental, Social, and Governance performance. | Weighted average score (0–100) from ESG data provider. | - | Higher score indicates stronger sustainability performance. |
    | **Carbon Intensity** | Amount of carbon emissions relative to revenue. | CO₂ Emissions / Revenue | tCO₂ / Million USD | Lower values reflect better energy efficiency and lower emissions. |

    ---

    💬 **Interpretation Note:**  
    A positive correlation between ESG Score and Financial Growth suggests that companies investing in sustainability practices tend to achieve stronger long-term financial performance.
    """)

col_left, col_right = st.columns(2)
col_left.markdown("### ESG Dimension Comparison")
esg_means = df[["ESG_Environmental", "ESG_Social", "ESG_Governance"]].mean()
radar_fig = go.Figure()
radar_fig.add_trace(go.Scatterpolar(
    r=esg_means.values,
    theta=esg_means.index,
    fill="toself",
    name="Average ESG"
))
radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False)
col_left.plotly_chart(radar_fig, use_container_width=True)

col_right.markdown("### ESG vs Financial Performance")
scatter_fig = px.scatter(df, x="ESG_Overall", y="Revenue", 
                         color="Industry", size="MarketCap",
                         hover_data=["CompanyID", "Region"])
col_right.plotly_chart(scatter_fig, use_container_width=True)

st.markdown("### 🚀Top Company by Growth Rate")
top_growth = df.sort_values("GrowthRate", ascending=False).head(5)
st.dataframe(top_growth[["CompanyID", "GrowthRate", "ProfitMargin", "ESG_Overall"]])