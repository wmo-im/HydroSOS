# HydroSOS - WHOS-Plata Data Pipeline Pilot
## Objective
To Pilot the generation of HydroSOS discharge status product using observations data published in the WHOS DAB for the La Plata Basin (whos-plata view).
## Procedure
### 1. Discover timeseries observations
Search for discharge timeseries observations suitable for the status product
- Expore WHOS metadata using any of the available client tools, i.e.:
  - https://community.wmo.int/en/whos-portals
  - https://whos.geodab.eu/gs-service/om-api
  - https://alerta.ina.gob.ar/wmlclient/wml/
  - https://whos.geodab.eu/gs-service/whos/search
  - https://pypi.org/project/om-api-client/
- Some useful search filters:
  - view: whos-plata
  - country: ARG, BRA, etc.
  - provider: argentina-ina, brazil-ana, etc.
  - observedProperty: discharge
  - ontology: whos
  - aggregationDuration: P1D
- Save observation identifiers together with other metadata in a CSV file ('data/timeseries_identifiers.csv')
```bash
om-api-client metadata -F provider=argentina-ina -v discharge -O whos -a P1D -o data/timeseries_identifiers.csv -f csv
```
### 2. Retrieve timeseries observations
- For each selected timeseries observation, download data for the desired time period (i.e. 1990-01-01 - today) in CSV format, i.e. using [om-api-client](https://github.com/wmo-im/HydroSOS/tree/main/whos_client). 
- Save the results in 'data/raw' directory using the observation identifiers as filename
```bash
om-api-client batch 1990-01-01 2025-07-18 data/timeseries_identifiers.csv data/raw -c -r
```
### 3. Regularize timeseries
- Compute daily means of downloaded timeseries using [regularize.py](https://github.com/wmo-im/HydroSOS/blob/main/whos_client/regularize.py). 
- Save the results in 'data/regularized' directory
```bash
python ../whos_client/regularize.py data/raw data/regularized
```
### 4. Compute HydroSOS categorized status product
- Compute mean monthly values and assign percentile rank using [statuscalc.py](https://github.com/wmo-im/HydroSOS/blob/main/status/statuscalc.py).
- Save the results in 'data/status' directory as as cat_{input_file}.csv
```bash
python ../status/statuscalc.py data/regularized/ data/status/
```