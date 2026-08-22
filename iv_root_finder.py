from scipy.stats import norm
import pandas as pd
import numpy
import math
import streamlit as st
import yfinance as yf


def black_scholes_EU_call(S, X, t, b, r, sigma):
    d1 = ((math.log(S/X)) + ((b + (sigma**2)/2))*t)/(sigma * (t**.5))
    d2 = d1 - sigma * (t**.5)
    # print((d1))
    # print(d2)
    call_price = S * math.e**((b-r)*t) * norm.cdf(d1) - X * math.e**(-r*t) * norm.cdf(d2)
    # call_vega = S * math.exp((b-r)*t) * norm.pdf(d1) * math.sqrt(t)
    
    return call_price 


def black_scholes_EU_put(S, X, t, b, r, sigma):
    d1 = ((math.log(S/X)) + ((b + (sigma**2)/2))*t)/(sigma * (t**.5))
    d2 = d1 - sigma * (t**.5)
    # print((d1))
    # print(d2)
    put_price = X * math.e**(-r * t) * norm.cdf(-d2) - S * math.e**((b-r)*t) * norm.cdf(-d1)
    # call_vega = S * math.exp((b-r)*t) * norm.pdf(d1) * math.sqrt(t)
    return put_price


class Option:
    def __init__(self, price, vega):
        self.price = price
        self.vega = vega


# def newton_roots(float: price, float: S, float: X, float: t, float: r) -> float: sigma:


def bisection(opt_type: str, P: float, S: float, X: float, t: float, r: float, b: float, sigma=.1, tolerance=1e-5) -> float:
    high_sigma = sigma    
    low_sigma = 1e-5
    if opt_type == "call":
        while black_scholes_EU_call(S,X,t,b,r, high_sigma) < P:
            high_sigma = high_sigma*2

        while high_sigma - low_sigma > tolerance:
            mid_sigma = (high_sigma + low_sigma)/2
            theoretical_price = black_scholes_EU_call(S,X,t,b,r, mid_sigma)
            if theoretical_price < P:
                low_sigma = mid_sigma
            else:
                high_sigma = mid_sigma
    
    elif opt_type == "put":
        while black_scholes_EU_put(S,X,t,b,r, high_sigma) < P:
            high_sigma = high_sigma*2
        
        while high_sigma - low_sigma > tolerance:
            mid_sigma = (high_sigma + low_sigma)/2
            theoretical_price = black_scholes_EU_put(S,X,t,b,r, mid_sigma)
            if theoretical_price < P:
                low_sigma = mid_sigma
            else:
                high_sigma = mid_sigma

    return (high_sigma + low_sigma)/2 


def sync_expiry_from_slider():
    st.session_state.expiry_days = st.session_state.expiry_slider
    st.session_state.expiry_box = st.session_state.expiry_slider 

def sync_expiry_from_box():
    st.session_state.expiry_days = st.session_state.expiry_box
    st.session_state.expiry_slider = st.session_state.expiry_box

def sync_rate_from_slider():
    st.session_state.rate = st.session_state.rate_slider
    st.session_state.rate_box = st.session_state.rate_slider

def sync_rate_from_box():
    st.session_state.rate = st.session_state.rate_box
    st.session_state.rate_slider = st.session_state.rate_box


# # Test Sample Data
# #---
# spot = 100 
# exercise = 100
# time = 1 
# interest_rate = .05
# variation = interest_rate
# iv = 0.2
# option_price = black_scholes_EU_call(spot, exercise, time, variation, interest_rate, iv)
# option1 = Option(0,0)
# option1.price = black_scholes_EU_call(spot, exercise, time, variation, interest_rate, iv)
# #---
st.title("Black-Scholes Implied Volatility Calculator")
st.markdown("Input parameters on sidebar to calculate implied volatility of European Call or Put.")
st.sidebar.header("Model Inputs")
price = st.sidebar.number_input("Option Price ($P$)", value=0.0, step=.01)
spot = st.sidebar.number_input("Underlying Spot Price ($S$)", value=100.0, step=.01)
strike = st.sidebar.number_input("Strike/Exercise Price ($X$)", value=100.0, step=.01)

if "expiry_days" not in st.session_state:
    st.session_state.expiry_days = 38
if "rate" not in st.session_state:
    st.session_state.rate = 0.05

col_a, col_b = st.sidebar.columns([3,1])
with col_a:
    st.slider(
        "Days to Expiration", min_value=1, max_value=365, value=st.session_state.expiry_days, key="expiry_slider", on_change=sync_expiry_from_slider
    )
with col_b:
    st.number_input(
        "Days", min_value=1, max_value=365, value=st.session_state.expiry_days, key="expiry_box",
        step=1, on_change=sync_expiry_from_box, label_visibility="collapsed"
    )

col_c, col_d = st.sidebar.columns([3,1])
with col_c:
    st.slider(
        "Risk-Free Interest Rate", min_value=0.0, max_value=.15, value=st.session_state.rate, key="rate_slider", step=.001,
        on_change=sync_rate_from_slider
    )
with col_d:
    st.number_input(
        "Rate", min_value=0.0, max_value=.15, value=st.session_state.rate, key="rate_box",
        step=.001, format="%.4f", on_change=sync_rate_from_box, label_visibility="collapsed"
    )
expiry_days = st.session_state.expiry_days
rate = st.session_state.rate
time = expiry_days/365.0

# expiry_days = st.sidebar.slider("Days to Expiration", min_value=1, max_value=365, value=38)
# rate = st.sidebar.slider("Risk-Free Interest Rate", min_value=0.0, max_value=.15, value=0.05, step=.001)
opt_type = st.sidebar.segmented_control(
    "Option Type", options=["call", "put"], default="call"
)

if st.button("Calculate Implied Volatility"):
    try:
        iv = bisection(opt_type, price, spot, strike, time, rate, rate) 
        col1, col2 = st.columns(2)
        col1.metric(label="Theoretical Call Implied Volatility", value=f"{iv: .4f}")
        col2.metric(label="Time to Expiry (Years)", value=f"{time: .4f}")
    except Exception as e:
        st.error(f"Execution Error: {e}")

# option_price = 4.6 
# exercise = 74 
# spot = 73.8 
# time = .104 
# interest_rate = .038 
# variation = interest_rate
# print(black_scholes_eu_call(spot, exercise, time, variation, interest_rate, .4747))
# print(f"your implied volatility based on your inputs: {bisection(option_price, spot, exercise, time, interest_rate, variation)} option price={option_price}, strike price={exercise}, underlying price={spot}, time={time}, interest rate={interest_rate} ")

# try:
#     option_price = float(input("Option Price up to 2 decimals: "))
#     exercise = float(input("Strike Price up to 2 decimals: "))
#     spot = float(input("Underlying Spot Price to 2 decimals: "))
#     time = float(input("Input option Time to expiration up to 2 decimals: "))
#     interest_rate = float(input("Interest rate up to 2 decimals: "))
#     variation = interest_rate
#     print(f"Your Implied Volatility based on your inputs: {bisection(option_price, spot, exercise, time, interest_rate, variation)} Option Price={option_price}, Strike Price={exercise}, Underlying Price={spot}, Time={time}, Interest Rate={interest_rate} ")
# except ValueError as e:
#     print(f"Input Error: A value you entered was incorrect. ({e})")
# # print(option1.price)

