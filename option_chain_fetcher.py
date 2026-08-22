import yfinance as yf
import pandas as pd

def fetch_option_chain(ticker: str, opt_type: str) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    expirations = stock.options
    all_options = []

    if opt_type.upper() == "CALL":
        for date in expirations:
            chain = stock.option_chain(date)
            calls = chain.calls.copy()
            calls["expirationDate"] = date
            all_options.append(calls)
        df= pd.concat(all_options, ignore_index=False)
    else:
        for date in expirations:
            chain = stock.option_chain(date)
            puts = chain.puts.copy()
            puts["expirationDate"] = date
            all_options.append(puts)
        df = pd.concat(all_options, ignore_index=False)

    output_filename = f"{ticker.lower()}_{opt_type.lower()}_options_live.csv"
    df.to_csv(output_filename, index=False)
    return df
option_chain_fetcher("AMD", "CALL")