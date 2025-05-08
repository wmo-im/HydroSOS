# Hydrological Status and Outlook System

Hydrological Status and Outlook System (HydroSOS). This repository contains code to facilitate common categorisation of status and forecast data for integration into the HydroSOS portal.
Use the flowchart below to identify the scripts appropriate for your data. 

If your data is ***status*** run ```status/statuscalc.py``` followed by ```status/status_to_json.py``` for ***station data*** or ```status/status_to_geotiff.py``` for ***hydrobasin data***.

If your data is ***forecast*** run ```forecast/forecastcalc.py``` followed by ```forecast/forecast_to_json.py``` for ***station data*** or ```forecast/forecast_to_geotiff.py``` for ***hydrobasin data***.

On the HydroSOS web portal, the monthly flow category .csv files for each station (produced by statuscalc.py/forecastcalc.py) are displayed in timeseries graphs, whereas the .json/.geotiff files for each month are visualised on the map. 


![Code flowchart](flowchart.png)

## Status  

### ```status/statuscalc.py```
This Python code is run from the terminal. It requires Python 3 and the ```pandas``` and ```numpy``` libraries. 
The Python code can process multiple files in one go. 

It should be used as follows:


``` python statuscalc.py input_directory output_directory --startYear --endYear ```

For example: 

``` python statuscalc.py ./example_data/status/input/ ./example_data/status/output_Python/ --startYear 1990 --endYear 2020 ```


Where:
*  ```input_directory``` is the directory containing the .csv flow timeseries to be processed. The script will attempt to parse every .csv file in this directory, so remove any .csv files you don't want to be processed. See files in [example_data/status/input](./example_data/status/input) for how these files should look.
* ```output_directory``` is the directory the processed .csv files will be written to. They will have the same name as files in the input_directory but with ```cat_``` appended to the start of the name.
* ```--startYear``` an optional argument, which year to use as the start range to calculate the reference average flow. Each monthly flow is divided by this reference average before calculating percentile rank and flow status.
* ```--endYear``` an optional argument, which year to use as the end range to calculate the reference average flow. Each monthly flow is divided by this reference average before calculating percentile rank and flow status. 

#### ```status/statuscalc.R```
The R Code can calculate flow status categories for an individual flow station timeseries saved in a .csv file. To run the R code, edit lines 14,15,16, (possibly 27 & 79), 88,89 and then run the script inside an R environment. If you have multiple files, you will have to run the script separately for each one, changing the relevant lines as appropriate. 

#### ```status/statuscalc.xlsx```

```statuscalc.xlsx``` can be used instead of the Python/R code to produce the flow status categories. This requires monthly averages to be calculated prior to data entry into the spreadsheet. Note to ensure consistency with the scripts, months with less than 50 % data completeness should be left blank. To modify the 'startYear' and 'endYear' parameters for calculating the reference average flow, users should modify the formulae from ```B68:M68```.
The excel files currently only support monhtly timeseries data starting on 01/1965. Excel file created by Mr. José Pablo Cantillano, Costa Rican Institute of Electricity. 

#### ```tests```
A jupyter notebook of tests which cross-verify the results of the Python and R code on four example datasets is provided. The Python/R outputs were also cross-verified against the excel outputs, on modified datasets (with timeseries starting in 1965).

### ```status/status_to_json.py```
A Python script that converts the csv outputs of the StatusCalc Python/R script to json files for use in the HydroSOS web portal is also provided. It can process multiple files in one go.

 It should be used as follows: 
``` python status_to_json.py input_directory output_directory```

For example: 
```python status_to_json.py ./example_data/status/output_Python ./example_data/status/output_json```

Where:
*  ```input_directory``` is the directory containing .csv status outputs from the python/R script with the name ```cat_stationID.csv```, this naming convention must be adhered to for the script to work. The script will attempt to parse every .csv file in this directory, so remove any .csv files you don't want to be processed. See files in [example_data/status/output_Python](./example_data/status/output_Python) for how these files should look.
* ```output_directory``` is the directory the processed .csv files will be written to. They will be named based on the dates of the data being processed. 



### ```status/status_to_geotiff.py```
A python script that converts the csv outputs of the statuscalc script into geotiff.

## Forecast

### ```forecast/forecastcalc.py```

This repository contains Python code to convert monthly flow forecast data into categories. This can be done using the ```forecastcalc.py``` script which should be run as follows: 

``` python forecastcalc.py obs_dir forecast_dir output_dir --obsDirStartingMonth```

Where:

* ```obs_dir``` contains ONLY .csv files of historic status (observed simulated) data, as daily time series. Filenames should be formatted X_CATCHMENTID.csv
* ``forecast_dir`` contains ONLY .csv files of forecast data for different ensemble members. Filenames should be formatted X_ENS_CATCHMENTID.csv
* ```output_dir``` is the name of the directory to output processed files to.
* ```--obsDirStartingMonth``` starting month in the ObsDir dataset (default january).

This script will calculate the categories (same as those in StatusCalc) that the forecasts belong to, based on both single and accumulated forecasts (results are saved into different subdirectories of output_dir).

Example: 

```python forecastcalc.py example_data/forecast/input/obs_dir example_data/forecast/input/forecast_dir  example_data/forecast/output/```

### ```forecast/forecast_to_json.py```

A Python script that converts the csv outputs of the forecastcalc.py script to json files for use in the HydroSOS web portal is also provided. It can process multiple files in one go.

### ```forecast/forecast_to_geotiff.py```

The ```counts.csv``` file produced by forecastcalc.py should be further processed into a .geotiff for visualisation on the portal map. This can be done using ```forecast_csv_to_geotiff.py``` which is run as follows:

```python forecast_to_geotiff.py input_dir output_dir shapefile forecast_start_date --forecast_length```

Where:
*  ```input_dir``` is the ```counts``` directory produced by ```ForecastCalc.py``` that contains the forecast category counts for different months
* ```output_dir``` is where the geotiffs are written
* ```shapefile``` is a path to the shapefile that defines the polygons corresponding to the forecast ID boundaries that will be drawn in the geotiff
*  ```forecast_start_date``` is the first forecast date formatted ```YYYY-MM``` 
*  ```--forecast_length``` is the number of months forecasts were made for (default 6).

Example: 

```python forecast_to_geotiff.py example_data/output_forecast/accumulated/ example_data/forecast/output/output_geotiff/ example_data/basins.shp 2024-02 --forecastLength 6```

Info:

The HydroBasins shapefile can be downloaded here: https://www.hydrosheds.org/products/hydrobasins#downloads, note each continental shapefile will need to be merged to create a global shapefile. Download of merging of the Hydrosheds Hydrobasins data can be done using ```other/merge_hydrobasins.py```. 

## Other

### ```other/merge_hydrobasins.py```

The Python script ```other/merge_hydrobasins.py``` provided in this repo will download and merge level 04 Hydrosheds Hydrobasins (from the link above) and merge them a single shapefile. 

It should be run as follows:

```python merge_hydrobasins.py directoryPath --download 1```

Where: 

* ```directoryPath``` is a path to where the shapefiles should be written to/read from.
* ```--download``` is an optional argument, if it is set to ```1``` (default 0) the shapefiles will be downloaded to ```directoryPath```, else it is assumed the directory already contains the shapefiles to be merged.

Info:

This script will write a shapefile called ```merged_hydrobasins_level04.shp``` to ```directoryPath```. 

## To do: 

* create ```status/status_to_geotiff.py```
* create ```forecast/forecast_to_json.py```

Last-updated: 08/05/2024 EK
