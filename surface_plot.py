import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter
from scipy.interpolate import Rbf
from scipy.interpolate import griddata

df = pd.read_csv("/home/josiah/josiah_code/spy_surface_data.csv")

def plotiv(df, lower_iv, upper_iv, min_dte): 
    
    df = pd.read_csv("spy_surface_data.csv")
    df["expirationDate"] = pd.to_datetime(df["expirationDate"])
    today = pd.to_datetime("today")
    df["DTE"] = (df["expirationDate"] - today).dt.days

    df= df[
        (df["DTE"] >= min_dte)
        &(df["impliedVolatility"] > lower_iv) 
        &(df["impliedVolatility"] < upper_iv) 
    ].copy()
    
    if df.empty:
        return None

    x = df["strike"]
    y = df["DTE"]
    z = df["impliedVolatility"].values


    grid_x, grid_y = np.meshgrid(
    np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100)
    )
    grid_z = griddata((x, y), z, (grid_x, grid_y), method="linear")
    grid_z_filled = pd.DataFrame(grid_z).ffill(axis=0).bfill(axis=0).ffill(axis=1).bfill(axis=1).values
    grid_z_smoothed = gaussian_filter(grid_z_filled, sigma=1.2)

    fig = go.Figure(
        data=[
            go.Surface(
                x=grid_x,
                y=grid_y,
                z=grid_z_smoothed,
                colorscale="Viridis",
                colorbar_title="IV"
            )
        ]
    )

    fig.update_layout(
        title="Interactive 3D Volatility Surface",
        scene=dict(
            xaxis_title="Strike",
            yaxis_title="DTE",
            zaxis_title="Implied Volatility",
            camera=dict(eye=dict(x=-1.5, y=-1.5, z=0.8))
        ),
        height=700,
        margin=dict(l=20,r=20,b=20,t=50)
    )
    return fig

fig = plotiv(df, .15, 2, 30)

if fig:
    fig.show()