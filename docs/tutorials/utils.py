"""Utilities for the tutorials."""
import os
import zipfile

import requests

BICYCLE_PARAMETERS_ZIP_URL = (
    "https://github.com/moorepants/BicycleParameters/archive/refs/heads/master.zip")
TUTORIALS_DIR = os.path.dirname(__file__)


def download_parametrization_data(data_dir: str = None) -> None:
    """Download the bicycle and rider data from the BicycleParameters repository."""
    if data_dir is None:
        data_dir = os.path.join(TUTORIALS_DIR, "data")
    if os.path.exists(os.path.join(TUTORIALS_DIR, "data")):
        raise FileExistsError("The data folder already exists.")
    # Download the zip file.
    zip_file = os.path.join(os.path.dirname(__file__), "bicycle_parameters.zip")
    with open(zip_file, "wb") as f:
        f.write(requests.get(BICYCLE_PARAMETERS_ZIP_URL).content)
    # Obtain the data folder from the zip file.
    with zipfile.ZipFile(zip_file, "r") as f:
        for file in f.namelist():
            if file.startswith("BicycleParameters-master/data/"):
                f.extract(file, TUTORIALS_DIR)
    # Remove the zip file.
    os.remove(zip_file)
    # Rename the data folder.
    os.rename(os.path.join(TUTORIALS_DIR, "BicycleParameters-master/data/"), data_dir)
    # Remove the BicycleParameters-master folder.
    os.rmdir(os.path.join(TUTORIALS_DIR, "BicycleParameters-master"))
