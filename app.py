import streamlit as st
import requests

def fetch_worldbank(indicator, fallback):
    url = f"https://api.worldbank.org/v2/country/IND/indicator/{indicator}?format=json&per_page=5"
    response = requests.get(url)
    data = response.json()

    if len(data) > 1:
        for entry in data[1]:
            if entry["value"] is not None:
                return float(entry["value"])

    return fallback


gdp_growth_live = fetch_worldbank("NY.GDP.MKTP.KD.ZG")
inflation_live = fetch_worldbank("FP.CPI.TOTL.ZG")
debt_live = fetch_worldbank("GC.DOD.TOTL.GD.ZS")
exports_live = fetch_worldbank("NE.EXP.GNFS.ZS")
exchange_rate = st.sidebar.slider("INR/USD Exchange Rate", 60, 100, 83)

if exports_live is None:
    exports_live = 20.0

export_boost = (exchange_rate - 83) * 0.2
exports_effect = exports_live + export_boost

GDP += exports_effect * 0.1
from sklearn.linear_model import LinearRegression

def forecast_series(series):
    X = np.array(range(len(series))).reshape(-1,1)
    y = np.array(series)
    model = LinearRegression()
    model.fit(X, y)
    future = model.predict(np.array(range(len(series), len(series)+5)).reshape(-1,1))
    return future

gdp_forecast = forecast_series(gdp_list)
fig_ml = go.Figure()
fig_ml.add_trace(go.Scatter(y=gdp_list, name="Historical Projection"))
fig_ml.add_trace(go.Scatter(
    y=list(gdp_list) + list(gdp_forecast),
    name="ML Forecast",
    line=dict(dash="dash")
))
fig_ml.update_layout(template="plotly_dark")
st.plotly_chart(fig_ml)

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="India Fiscal Intelligence System", layout="wide")

st.markdown("""
<style>
body {background-color: #0e1117;}
.block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("🇮🇳 INDIA FISCAL INTELLIGENCE SYSTEM")
st.markdown("Strategic 10-Year Fiscal Command Platform")

# -------------------------------------------------
# OBJECTIVE SELECTION
# -------------------------------------------------
st.sidebar.header("Strategic Objective")

objective = st.sidebar.selectbox(
    "Choose Government Objective",
    ["Maximise Growth", "Debt Stability", "Inflation Targeting"]
)

# -------------------------------------------------
# SHOCK CONTROLS
# -------------------------------------------------
st.sidebar.header("Global Shock Module")

oil_shock = st.sidebar.checkbox("Oil Price Shock")
recession_shock = st.sidebar.checkbox("Global Recession")

# -------------------------------------------------
# POLICY CONTROLS
# -------------------------------------------------
st.sidebar.header("Fiscal Controls")

G = st.sidebar.slider("Government Spending", 10, 80, 35)
tax_rate = st.sidebar.slider("Tax Rate", 0.05, 0.4, 0.2)

# -------------------------------------------------
# BASE PARAMETERS (India-style)
# -------------------------------------------------
potential_gdp = 100
natural_growth = 6.5
inflation_target = 4
b = 0.7
multiplier = 1 / (1 - b)
initial_debt = 85      # closer to India debt ratio zone
interest_on_debt = 7
years = 10

# Shock effects
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

    GDP = GDP * (1 + adjusted_growth/100) + fiscal_impact
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
# SECTION 2 — DEBT RISK ANALYSIS
# -------------------------------------------------
st.header("🚨 Debt Sustainability Engine")

# Crisis probability (simple scoring logic)
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
st.header("🤖 Fiscal Strategy Recommendation Engine")

recommendation = ""

if objective == "Maximise Growth":
    if G < 50:
        recommendation = "Increase spending moderately to boost growth."
    else:
        recommendation = "Growth is strong. Monitor debt carefully."

elif objective == "Debt Stability":
    if final_debt_ratio > 85:
        recommendation = "Reduce deficit. Increase taxes or cut spending."
    else:
        recommendation = "Debt trajectory acceptable."

elif objective == "Inflation Targeting":
    if final_inflation > 6:
        recommendation = "Reduce fiscal stimulus to ease inflation."
    else:
        recommendation = "Inflation under control."

st.info(recommendation)

# -------------------------------------------------
# SECTION 5 — TRAJECTORIES
# -------------------------------------------------
st.header("📈 Economic Trajectories")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(y=gdp_list))
fig1.update_layout(template="plotly_dark", height=280)
st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(y=debt_list))
fig2.update_layout(template="plotly_dark", height=280)
st.plotly_chart(fig2, use_container_width=True)
