import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# INDIA BASELINE PARAMETERS
# -------------------------

potential_gdp = 100
natural_unemployment = 6
inflation_target = 4

# Behavioral parameters
a = 20      # autonomous consumption
b = 0.7     # MPC (India higher consumption economy)
c = 15      # autonomous investment
d = 25      # interest sensitivity
k = 0.4     # inflation sensitivity

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(page_title="India Macro Simulator", layout="wide")
st.title("🇮🇳 India National Economy Simulator")

st.markdown("Adjust fiscal and monetary policy to see macroeconomic impact.")

# -------------------------
# POLICY CONTROLS
# -------------------------

col1, col2, col3 = st.columns(3)

with col1:
    G = st.slider("Government Spending (Index)", 10, 60, 30)

with col2:
    tax_rate = st.slider("Tax Rate", 0.05, 0.4, 0.2)

with col3:
    interest_rate = st.slider("RBI Interest Rate (%)", 2.0, 10.0, 6.5)

# -------------------------
# MODEL
# -------------------------

def calculate_gdp(G, t, r):
    T = t * potential_gdp
    C = a + b * (potential_gdp - T)
    I = c - d * (r/100)
    return C + I + G

GDP = calculate_gdp(G, tax_rate, interest_rate)

inflation = inflation_target + k * (GDP - potential_gdp)/potential_gdp * 10
gdp_growth = (GDP - potential_gdp)/potential_gdp * 100
unemployment = natural_unemployment - 0.25 * gdp_growth

# -------------------------
# DISPLAY METRICS
# -------------------------

col4, col5, col6 = st.columns(3)

col4.metric("GDP Index", round(GDP,2))
col5.metric("Inflation (%)", round(inflation,2))
col6.metric("Unemployment (%)", round(unemployment,2))

# -------------------------
# ECONOMIC TEMPERATURE
# -------------------------

if GDP > potential_gdp + 5:
    st.warning("⚠️ Economy Overheating")
elif GDP < potential_gdp - 5:
    st.error("❄️ Economic Slowdown")
else:
    st.success("✅ Economy Stable")

# -------------------------
# GRAPH
# -------------------------

fig, ax = plt.subplots()
ax.bar(["GDP", "Potential GDP"], [GDP, potential_gdp])
ax.set_title("India GDP vs Potential")
st.pyplot(fig)
