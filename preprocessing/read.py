import xarray as xr
import pandas as pd

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
    
 
def read_nc_files(file_list):
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

    return ds


def read_labels(file_path):
    """
    Read labels from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pandas.DataFrame: DataFrame containing the labels.
    """
    df = pd.read_csv(file_path)
    
    return df


def align_data(ds, labels):
    pass