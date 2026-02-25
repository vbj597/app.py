import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Model Parameters ---
a = 50
b = 0.6
c = 100
d = 20
natural_unemployment = 5
potential_gdp = 1000

st.title("National Economy Simulator")

st.sidebar.header("Policy Controls")

G = st.sidebar.slider("Government Spending", 100, 500, 200)
tax_rate = st.sidebar.slider("Tax Rate", 0.1, 0.5, 0.2)
interest_rate = st.sidebar.slider("Interest Rate (%)", 0.0, 10.0, 5.0)

def calculate_gdp(G, t, r):
    T = t * potential_gdp
    C = a + b * (potential_gdp - T)
    I = c - d * (r/100)
    return C + I + G

GDP = calculate_gdp(G, tax_rate, interest_rate)

inflation = 0.02 * (GDP - potential_gdp)
gdp_growth = (GDP - potential_gdp)/potential_gdp * 100
unemployment = natural_unemployment - 0.3 * gdp_growth

st.metric("GDP", round(GDP,2))
st.metric("Inflation", round(inflation,2))
st.metric("Unemployment", round(unemployment,2))

fig, ax = plt.subplots()
ax.bar(["GDP", "Potential GDP"], [GDP, potential_gdp])
st.pyplot(fig)
