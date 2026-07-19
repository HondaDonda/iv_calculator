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

class Option:
    def __init__(self, price, vega):
        self.price = price
        self.vega = vega



# def newton_roots(float: price, float: S, float: X, float: t, float: r) -> float: sigma:

def bisection(P: float, S: float, X: float, t: float, r: float, b: float, sigma=.1, tolerance=1e-5) -> float:
    high_sigma = sigma    
    low_sigma = 1e-5
    while black_scholes_EU_call(S,X,t,b,r, high_sigma) < P:
        print(f"Volatility: {high_sigma} | Option Price:{black_scholes_EU_call(S,X,t,b,r, high_sigma)}")
        high_sigma = high_sigma*2

    while high_sigma - low_sigma > tolerance:
        mid_sigma= (high_sigma + low_sigma)/2
        theoretical_price = black_scholes_EU_call(S,X,t,b,r, mid_sigma)
        if theoretical_price < P:
            low_sigma = mid_sigma
        else:
            high_sigma = mid_sigma
    print(f"Price of option.{black_scholes_EU_call(S,X,t,b,r,(high_sigma + low_sigma)/2)}: ") 
    print(f"high + low sigma = {high_sigma + low_sigma} ")
    return (high_sigma + low_sigma)/2

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
st.markdown("Input parameters on sidebar to calculate implied volatility of European Call.")
st.sidebar.header("Model Inputs")
price = st.sidebar.number_input("Option Price ($S$)", value=0.0, step=.01)
spot = st.sidebar.number_input("Underlying Spot Price ($S$)", value=100.0, step=.01)
strike = st.sidebar.number_input("Strike/Exercise Price ($X$)", value=100.0, step=.01)
expiry_days = st.sidebar.slider("Days to Expiration", min_value=1, max_value=365, value=38)
rate = st.sidebar.slider("Risk-Free Interest Rate", min_value=0.0, max_value=.15, value=0.05, step=.001)


time = expiry_days/365.0


if st.button("Calculate Implied Volatility"):
    try:
        iv = bisection(price, spot, strike, time, rate, rate) 
        col1, col2 = st.columns(2)
        col1.metric(label="Theoretical Call Implied Volatility", value=f"{iv: .2f}")
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

