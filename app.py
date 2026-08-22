import streamlit as st
import pandas as pd
from surface_plot import plotiv
from option_chain_fetcher import fetch_option_chain 
from data_cleaner import clean_option_data, find_atm
from iv_root_finder import (
    black_scholes_EU_call,
    black_scholes_EU_put,
    bisection,
    sync_expiry_from_box,
    sync_expiry_from_slider,
    sync_rate_from_box,
    sync_rate_from_slider
)

st.set_page_config(page_title="Options Workbench", layout="wide")

if "chain_df" not in st.session_state:
    st.session_state["chain_df"] = None

st.title("Options Volatility Analysis Dashboard")

tab_fetch, tab_surface, tab_iv = st.tabs(
    ["Fetch Option Chain", "Volatility Surface", "IV Calculator"]
)

with tab_fetch:
    st.subheader("Fetch Live Option Chain")
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker_input = st.text_input("Ticker Symbol", value="SPY").upper()
    with col2:
        opt_type = st.segmented_control(
            "Option Type", options=["call", "put"], default="call"
        )
    
    if st.button("Fetch Option Chain", type="primary"):
        with st.spinner(f"Fetching {opt_type.upper()} chain for {ticker_input}..."):
            try:
                df = fetch_option_chain(ticker=ticker_input, option_type=opt_type)
                st.session_state["chain_df"] = df
                st.success(
                    f"Successfully fetched {len(df)} {opt_type.upper()} contacts for {ticker_input}. "
                )
            except Exception as e:
                st.error(f"Error executing fetch: {e}")

        st.divider()

    st.subheader("Upload Your Own Option Chain")
    uploaded_chain = st.file_uploader("Choose an option chain CSV", type=["csv"], key="fetch_tab_uploader") 

    if uploaded_chain is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_chain)
            st.session_state["chain_df"] = df_uploaded
            st.success(f"Loaded {len(df_uploaded)} rows from {uploaded_chain.name}.")
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
    
    if st.session_state["chain_df"] is not None:
        st.divider()
        st.dataFrame(st.session_state["chain_df"], use_container_width=True)


    if st.session_state["chain_df"] is not None:
        st.dataframe(st.session_state["chain_df"], use_container_width=True)
            


with tab_surface:
    st.sidebar.header("Surface Parameters")
    lower_iv = st.sidebar.slider("Min IV", 0.01, 0.50, 0.05)
    upper_iv = st.sidebar.slider("Max IV", 0.5, 3.00, 2.00)
    min_dte = st.sidebar.slider("Min DTE", 0.0, 30.0, 3.00)
    # HARD CODED CSV SURFACE DATA
    df_clean = pd.read_csv("spy_surface_data.csv")
    fig = plotiv(df_clean, lower_iv, upper_iv, min_dte)
    st.plotly_chart(fig, use_container_width=True )
    # if uploaded_file is not None:
    #     old_rows = len(raw_df)
    #     raw_df = pd.read_csv(uploaded_file)
    #     clean_df = clean_option_data(raw_df)
    #     st.success(f"Data cleaned successfully! ({len(raw_df)}) originally.  ({len(clean_df)}) rows remaining. ")
    #     fig = plotiv(df_clean, lower_iv, upper_iv, min_dte)
    #     if fig is not None:
    #         st.plotly_chart(fig, use_container_width=True)
    #     else:
    #         st.warning("No data points found matching current filter thresholds.")
    # else:
    #     st.info("Upload a CSV file in the sidebar to view the interactive 3D IV surface. ") 


with tab_iv:

    st.subheader("Black-Scholes Implied Volatility Calculator")
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