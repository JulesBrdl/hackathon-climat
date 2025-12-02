import xarray as xr
import pandas as pd
import numpy as np

import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

# TODO change to EPSG:2154

def load_nc_file(file_path, varname):
    """Load a NetCDF file and return the dataset."""
    ds = xr.open_dataset(file_path, chunks={"time": 100})
    ds = ds.rio.write_crs("EPSG:27572") # Lambert Paris II

    if varname not in ds.data_vars:
        raise ValueError(f"Variable '{varname}' not found in the dataset.")
    var = ds[varname] 

    return var


def merge_datasets(ds_list):
    """Merge two xarray datasets along the time dimension."""
    base, base_name = ds_list[0]

    return xr.Dataset({**{base_name: base}, **{name: data.rio.reproject_match(base) for data, name in ds_list[1:]}})
    
 
def read_nc_files(file_list, start_date = np.datetime64('2005-01-01')):
    """
    Read NetCDF files from the specified directory and return merged dataset.

    Args:
        file_list (list of tuples): List of tuples with structure (file_path, varname).

    Returns:
        xarray.Dataset: Merged dataset containing all variables.

    Example:
    path = '../data/'
    prfile = 'prAdjust_FR-Metro_MPI-ESM1-2-LR_historical_r1i1p1f1_CNRM_CNRM-ALADIN63-emul-CNRM-UNET11-tP22_v1-r1_MF-CDFt-SAFRAN-1985-2014_day_18500101-20141231.nc'
    tasfile = 'tasAdjust_FR-Metro_MPI-ESM1-2-LR_historical_r1i1p1f1_CNRM_CNRM-ALADIN63-emul-CNRM-UNET11-tP22_v1-r1_MF-CDFt-ANASTASIA-SAFRAN-1985-2014_day_18500101-20141231.nc'
    ds = read_nc_files([(path+prfile, 'prAdjust'), (path+tasfile, 'tasAdjust')])
    """
    dslist = []
    for file_path, varname in file_list:
        dslist.append((load_nc_file(file_path, varname), varname))

    ds = merge_datasets(dslist)
    ds = ds.sel(time=slice(start_date, None))

    return ds


def read_labels(file_path):
    """
    Read labels from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing the labels with geometry.
    """
    df = pd.read_csv(file_path)
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry).set_crs("EPSG:4326")  # WGS84
    gdf["Date"] = gdf["Date de première alerte"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
    gdf["Date"] = gdf["Date"].dt.date

    return gdf.to_crs("EPSG:27572")  # Convert to Lambert Paris II


def align_data(ds, gdf_labels):
    # iteratively create mask per time step
    masked_slices = []
    for t in ds.time:
        current_date = pd.to_datetime(t.values).date()
        
        ds_slice = ds["prAdjust"].sel(time=t)
        
        daily_geom = gdf_labels[gdf_labels['Date'] == current_date]
        
        if not daily_geom.empty:
            temp_ones = xr.ones_like(ds_slice, dtype=np.int8)
            temp_ones = temp_ones.rio.write_crs("EPSG:27572")
            
            # TODO add buffer (with proper crs)
            mask_slice = temp_ones.rio.clip(
                daily_geom.geometry, 
                all_touched=True, 
                drop=False 
            )
            mask_slice = mask_slice.fillna(0)
        else:
            mask_slice = xr.zeros_like(ds_slice)

        mask_slice = mask_slice.rio.write_crs("EPSG:27572")
        masked_slices.append(mask_slice) 
    
    masks = xr.concat(masked_slices, dim="time")
    masks.name = 'fire'
    masks.attrs['long_name'] = 'Spatiotemporal Mask (1=Inside Geometry, 0=Outside/No Event)'

    ds['fire'] = masks

    return ds