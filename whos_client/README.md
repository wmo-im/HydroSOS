## WHOS data retrieval functionality for HydroSOS

### Purpose

To facilitate interoperable timeseries data retrieval from the WHOS (WMO Hydrological Observations System)

### How to use

1. Install this module (see Installation)

2. Register into WHOS and save your access token

3. Explore WHOS portals and search engines to select the stations and variables of interest

  - https://community.wmo.int/en/whos-portals
  - https://whos.geodab.eu/gs-service/timeseries-api/whos.html
  - https://alerta.ina.gob.ar/wmlclient/wml/
  - http://whos.geodab.eu/gs-service/search?view=whos-plata


4. Once you have the station (site) and variable identifiers, set the required initial and end dates

5. Use either a python script or notebook (see get_test.ipynb) or the command line interface to get the data (see get_test.sh)

### Installation

    python3 -m venv .
    source bin/activate
    pip3 install -r requirements

### Credits

Programa de Sistemas de Alerta Hidrológico

Laboratorio de Hidrología

Instituto Nacional del Agua

Argentina

2024-05-22

