import requests
import xarray as xr
from io import BytesIO
import os

def data_download(url):
    if url == "":
        #url = "https://object.files.data.gouv.fr/meteofrance-drias/SocleM-Climat-2025/EMULATEUR/METROPOLE/ALPX-12/MPI-ESM1-2-LR/r1i1p1f1/CNRM-ALADIN63-emul-CNRM-UNET11-tP22/historical/day/prAdjust/version-hackathon-102025/prAdjust_FR-Metro_MPI-ESM1-2-LR_historical_r1i1p1f1_CNRM_CNRM-ALADIN63-emul-CNRM-UNET11-tP22_v1-r1_MF-CDFt-SAFRAN-1985-2014_day_18500101-20141231.nc"
        url = "https://object.files.data.gouv.fr/meteofrance-drias/SocleM-Climat-2025/CPRCM/METROPOLE/ALPX-3/CNRM-ESM2-1/r1i1p1f2/CNRM-AROME46t1/ssp370/day/tasAdjust/version-hackathon-102025/tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-SAFRAN-1991-2020_day_20150101-21001231.nc"
    
    filename = "./data_perso/" + os.path.basename(url)

    if not os.path.exists(filename):

        print("download_script.py : File not found, fetching data from online.")

        response = requests.get(url)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        print("download_script.py : File already exists.")

    print("download_script.py : File size: ", os.path.getsize(filename))
    print("download_script.py : Crrating dataset.")
    ds = xr.open_dataset(filename)

    return ds

#arr = ds.to_array().values
#print(type(arr))
#print(arr.shape)
