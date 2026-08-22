import pandas as pd
import numpy as np
import os

base_name = os.path.splitext(os.path.basename())

def find_atm(df):
    match = df[df["inTheMoney"] == False]
    
    if not match.empty:
        first_row = match.iloc[0]
        value = first_row["strike"]
        return value 
    else:
        return 0 

def clean_option_data(file_path):
    columns_order = [
        "strike",
        "impliedVolatility",
    ]

    df = pd.read_csv(file_path)
    atm = find_atm(df)

    df = pd.read_csv(df)
    df["volume"] = df["volume"].fillna(0)
    df = df[df["volume"] != 0]
    df = df[(df["ask"]) - df["bid"] <= .05]
    df = df[df["strike"] > atm] 
    selected_columns = ["expirationDate", "strike", "impliedVolatility"] 
    df_subset = df[selected_columns]
    base_path, ext = os.path.splitext(file_path)
    output_filename = f"{base_path}_surface{ext}"

    df_subset.to_csv(output_filename, index=False)