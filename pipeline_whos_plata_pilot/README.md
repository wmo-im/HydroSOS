# HydroSOS - WHOS-Plata Data Pipeline Pilot
## Objective
To Pilot the generation of HydroSOS discharge status product using observations data published in the WHOS DAB for the La Plata Basin (whos-plata view).
## A. Procedure
### 0. Install and configure OM API Client
```bash
pip install om-api-client
```
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
Example of metadata file
```text
longitude,latitude,country,sourceId,identifier,name,id,author
-58.5583333333333,-28.995,Argentina,argentina-ina,argentina-ina:sat2:2832,Corriente - Paso Lucero,083988DC8C2E39D6E0C82B296A857F6A088B8028,
-57.6333333333333,-30.25,Argentina,argentina-ina,argentina-ina:alturas_prefe:74,Monte Caseros,0DF4C4284AA14E0A545C0F855B4F6FF558693CEE,
-59.1783333333333,-34.5894444444444,Argentina,argentina-ina,argentina-ina:sat2:2128,Lujan - Lujan,329BB00817E03FB6C1E86BF7625BA824692C9A95,
-59.2172222222222,-29.7572222222222,Argentina,argentina-ina,argentina-ina:sat2:2199,Corrientes - Los Laureles,33D8EF13796FA55AD42D54A54EF43D6DEB4CB529,
-59.1261111111111,-31.8016666666667,Argentina,argentina-ina,argentina-ina:sat2:2205,Gualeguay - Villaguay,3A2D53454064685F479B74B6C5B3EAA289DE5E00,
```
### 2. Retrieve timeseries observations
- For each selected timeseries observation, download data for the desired time period (i.e. 1990-01-01 - today) in CSV format, i.e. using [om-api-client](https://github.com/wmo-im/HydroSOS/tree/main/whos_client). 
- Save the results in 'data/raw' directory using the observation identifiers as filename
```bash
om-api-client batch 1990-01-01 2025-07-18 data/timeseries_identifiers.csv data/raw -c -r
```
Example of raw data file
```text
date,value
1990-01-01T02:00:00Z,733.0
1990-01-02T02:00:00Z,771.0
1990-01-03T02:00:00Z,733.0
1990-01-04T02:00:00Z,781.0
1990-01-05T02:00:00Z,771.0
1990-01-06T02:00:00Z,771.0
1990-01-07T02:00:00Z,1018.0
1990-01-08T02:00:00Z,1061.0
```
### 3. Regularize timeseries
- Compute daily means of downloaded timeseries using [regularize.py](https://github.com/wmo-im/HydroSOS/blob/main/whos_client/regularize.py). 
- Save the results in 'data/regularized' directory
```bash
python ../whos_client/regularize.py data/raw data/regularized
```
Example of regularized data file
```text
date,flow
01/01/1990,733.0
02/01/1990,771.0
03/01/1990,733.0
04/01/1990,781.0
05/01/1990,771.0
06/01/1990,771.0
07/01/1990,1018.0
08/01/1990,1061.0
```
### 4. Compute HydroSOS categorized status product
- Compute mean monthly values and assign percentile rank using [statuscalc.py](https://github.com/wmo-im/HydroSOS/blob/main/status/statuscalc.py).
- Save the results in 'data/status' directory as as cat_{input_file}.csv
```bash
python ../status/statuscalc.py data/regularized/ data/status/
```
Example of status file
```text
date,flowcat
1990-01-01,3
1990-02-01,3
1990-03-01,3
1990-04-01,3
1990-05-01,4
1990-06-01,5
```
## B. Alternative procedure (retrieve features)
### 0. Install and configure OM API Client
### 1. Retrieve features (monitoring points) where daily discharge is available for a given period
```bash
om-api-client features -f csv -o data/features.csv -a P1D -v discharge -O whos -F beginPosition=2025-01-01 -F endPosition=2025-07-22 -F provider=argentina-ina
```
### 2. For each feature in data/features.csv, retrieve daily discharge data
```bash
om-api-client batch 1990-01-01 2025-07-22 data/features.csv data/raw -I id -c -a P1D -v discharge -O whos -r -f
```
### 3. & 4. regularize and calculate status as in procedure A
## Example with provider DINAGUA
```bash
# 1. get features where recent daily average discharge is available
om-api-client features -F provider=uruguay-dinagua -v discharge -O whos -a P1D -T AVERAGE -f csv -o data/features_dinagua_daily_discharge_avg.csv -F beginPosition=2025-06-01 -F endPosition=202
5-07-23
# 2. For each feature retrieve daily average discharge data (short time span for test purposes, retrieval may be slow)
om-api-client batch 2024-06-01 2025-07-23 data/features_dinagua_daily_discharge_avg.csv data/raw/dinagua -v discharge -O whos -a P1D -T AVERAGE -I id -f -c
# 3. regularize
python ../whos_client/regularize.py data/raw/dinagua data/regularized/dinagua
# 4. statuscalc will produce no output because of missing long term average. Set a longer time span in step 2 for this to work.
python ../status/statuscalc.py data/regularized/dinagua/ data/status/dinagua/
```
