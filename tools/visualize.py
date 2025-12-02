import os
import zipfile

import pandas as pd
from datetime import datetime
import xarray as xr
import netCDF4
import rasterio 
import rioxarray
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.pyplot as plt

def plot_data_on_map(daydata, title=None, cmap='coolwarm'):
    """
    Plot data for a variable for a day.

    Args:
        daydata (xarray.DataArray): Data for a specific day.

    Example:
    tas = ds['tasAdjust']  
    tas_day = tas.isel(time=0)
    plot_day(tas_day)
    """
    # Plot with Cartopy
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Set extent: roughly Europe
    ax.set_extent([-25, 40, 30, 72], crs=ccrs.PlateCarree())

    # Add background map features
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    # Plot the temperature
    im = daydata.plot(ax=ax, transform=ccrs.PlateCarree(),
                    cmap=cmap, 
                    add_colorbar=True)

    if title is not None:
        plt.title(title)
    plt.show()