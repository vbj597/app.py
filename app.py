import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="India Fiscal Intelligence System", layout="wide")
st.title("🇮🇳 INDIA FISCAL INTELLIGENCE SYSTEM")
st.markdown("Live Data • Fiscal Engine • ML Forecast • External Sector")

# -------------------------------------------------
# SAFE WORLD BANK FETCH
# -------------------------------------------------
def fetch_worldbank(indicator, fallback):
    try:
        url = f"https://api.worldbank.org/v2/country/IND/indicator/{indicator}?format=json&per_page=5"
        response = requests.get(url, timeout=10)
        data = response.json()

        if len(data) > 1:
            for entry in data[1]:
                if entry["value"] is not None:
                    return float(entry["value"])
        return fallback
    except:
        return fallback

# Live India anchors (with safe fallback values)
gdp_growth_live = fetch_worldbank("NY.GDP.MKTP.KD.ZG", 6.5)
inflation_live  = fetch_worldbank("FP.CPI.TOTL.ZG", 4.0)
debt_live       = fetch_worldbank("GC.DOD.TOTL.GD.ZS", 85.0)
exports_live    = fetch_worldbank("NE.EXP.GNFS.ZS", 20.0)

# -------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------
st.sidebar.header("Strategic Objective")
objective = st.sidebar.selectbox(
    "Policy Objective",
    ["Maximise Growth", "Debt Stability", "Inflation Targeting"]
)

st.sidebar.header("Global Shocks")
oil_shock = st.sidebar.checkbox("Oil Price Shock")
recession_shock = st.sidebar.checkbox("Global Recession")

st.sidebar.header("Fiscal Controls")
G = st.sidebar.slider("Government Spending Index", 10, 80, 35)
tax_rate = st.sidebar.slider("Tax Rate", 0.05, 0.4, 0.2)
exchange_rate = st.sidebar.slider("INR/USD Exchange Rate", 60, 100, 83)

# -------------------------------------------------
# MODEL PARAMETERS
# -------------------------------------------------
potential_gdp = 100
natural_growth = gdp_growth_live
inflation_target = inflation_live
initial_debt = debt_live
interest_on_debt = 7
years = 10

b = 0.7
multiplier = 1 / (1 - b)

# Shock adjustments
growth_penalty = -3 if recession_shock else 0
inflation_boost = 2 if oil_shock else 0

# -------------------------------------------------
# SIMULATION ENGINE
# -------------------------------------------------
GDP = potential_gdp
debt = initial_debt

gdp_list = []
debt_list = []
inflation_list = []
debt_ratio_list = []

for year in range(years):

    adjusted_growth = natural_growth + growth_penalty

    T = tax_rate * GDP
    fiscal_impact = multiplier * (G - T)

    # External sector channel
    export_boost = (exchange_rate - 83) * 0.2
    exports_effect = exports_live + export_boost

    GDP = GDP * (1 + adjusted_growth/100) + fiscal_impact + (exports_effect * 0.05)

    inflation = inflation_target + 0.25 * (GDP - potential_gdp) + inflation_boost

    deficit = G - T
    debt = debt + deficit + (interest_on_debt/100 * debt)

    debt_ratio = (debt / GDP) * 100

    gdp_list.append(GDP)
    debt_list.append(debt)
    inflation_list.append(inflation)
    debt_ratio_list.append(debt_ratio)

final_growth = ((gdp_list[-1] - potential_gdp)/potential_gdp)*100
final_debt_ratio = debt_ratio_list[-1]
final_inflation = inflation_list[-1]

# -------------------------------------------------
# MACHINE LEARNING FORECAST
# -------------------------------------------------
def forecast_series(series):
    X = np.array(range(len(series))).reshape(-1,1)
    y = np.array(series)
    model = LinearRegression()
    model.fit(X, y)
    future = model.predict(np.array(range(len(series), len(series)+5)).reshape(-1,1))
    return future

gdp_forecast = forecast_series(gdp_list)

# -------------------------------------------------
# SECTION 1 — STRATEGIC DASHBOARD
# -------------------------------------------------
st.header("📊 Strategic Overview")

col1, col2, col3 = st.columns(3)
col1.metric("10Y Growth Index", round(final_growth,2))
col2.metric("Debt-to-GDP (%)", round(final_debt_ratio,2))
col3.metric("Inflation (%)", round(final_inflation,2))

# Growth Gauge
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=final_growth,
    gauge={'axis': {'range': [-20, 40]}}
))
fig_gauge.update_layout(template="plotly_dark", height=250)
st.plotly_chart(fig_gauge, use_container_width=True)

# -------------------------------------------------
# SECTION 2 — DEBT RISK ENGINE
# -------------------------------------------------
st.header("🚨 Debt Sustainability Engine")

risk_score = 0
if final_debt_ratio > 95:
    risk_score += 60
elif final_debt_ratio > 85:
    risk_score += 40
elif final_debt_ratio > 75:
    risk_score += 20

if final_growth < 0:
    risk_score += 25
if final_inflation > 8:
    risk_score += 15

st.metric("Debt Crisis Probability Score (%)", risk_score)

heat_df = pd.DataFrame([debt_ratio_list])
fig_heat = px.imshow(heat_df, aspect="auto")
fig_heat.update_layout(template="plotly_dark", height=200)
st.plotly_chart(fig_heat, use_container_width=True)

# -------------------------------------------------
# SECTION 3 — RBI MONITOR
# -------------------------------------------------
st.header("🏦 RBI Inflation Monitoring")

if final_inflation > 6:
    st.error("RBI Alert: Tightening Likely")
elif final_inflation < 2:
    st.warning("RBI Alert: Demand Weakness")
else:
    st.success("Inflation Within Target Band")

# -------------------------------------------------
# SECTION 4 — AI FISCAL ADVISOR
# -------------------------------------------------
st.header("🤖 Fiscal Strategy Recommendation")

if objective == "Maximise Growth":
    if G < 50:
        st.info("Recommendation: Increase spending moderately.")
    else:
        st.info("Growth strong. Monitor debt levels.")
elif objective == "Debt Stability":
    if final_debt_ratio > 85:
        st.info("Recommendation: Reduce deficit via tax increase or spending cuts.")
    else:
        st.info("Debt trajectory manageable.")
elif objective == "Inflation Targeting":
    if final_inflation > 6:
        st.info("Recommendation: Reduce fiscal stimulus.")
    else:
        st.info("Inflation stable.")

# -------------------------------------------------
# SECTION 5 — TRAJECTORIES + ML FORECAST
# -------------------------------------------------
st.header("📈 GDP Projection + ML Forecast")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(y=gdp_list, name="Simulated GDP"))
fig1.add_trace(go.Scatter(
    y=list(gdp_list) + list(gdp_forecast),
    name="ML Forecast",
    line=dict(dash="dash")
))
fig1.update_layout(template="plotly_dark", height=350)
st.plotly_chart(fig1, use_container_width=True)

st.header("💰 Debt Trajectory")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(y=debt_list, name="Debt"))
fig2.update_layout(template="plotly_dark", height=350)
st.plotly_chart(fig2, use_container_width=True)
