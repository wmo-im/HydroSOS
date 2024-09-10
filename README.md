# Hydrological Status and Outlook System

Hydrological Status and Outlook System (HydroSOS). This repository contains code to facilitate common categorisation of status and forecast data for integration into the HydroSOS portal.

## Status  

This repository contains Python/R/Excel code to convert daily flow timeseries data into monthly flow status categories saved in .csv files. These .csv files should then be further processed into monthly .json files using the ```csv_to_json.py``` script. On the HydroSOS web portal, the monthly flow category .csv files for each station are displayed in timeseries graphs, whereas the .json files for each month are visualised on the map. 

### R Code
The R Code can calculate flow status categories for an individual flow station timeseries saved in a .csv file. See files in [example_data/input](./example_data/input) for how these timeseries files should look. 
To run the R code, edit lines 14,15,16, (possibly 27 & 79), 88,89 and then run the script inside an R environment. If you have multiple files, you will have to run the script separately for each one, changing the relevant lines as appropriate. 

### Python Code
Unlike the R Code, the Python code is run from the terminal. It requires Python 3 and the ```pandas``` and ```numpy``` libraries. 
The Python code can process multiple files in one go. 

It should be used as follows:


``` python StatusCalcV3.py input_directory output_directory --startYear --endYear ```

For example: 

``` python StatusCalcV3.py ./example_data/input/ ./example_data/output_Python/ --startYear 1990 --endYear 2020 ```


Where:
*  ```input_directory``` is the directory containing the .csv flow timeseries to be processed. The script will attempt to parse every .csv file in this directory, so remove any .csv files you don't want to be processed. See files in [example_data/input](./example_data/input) for how these files should look.
* ```output_directory``` is the directory the processed .csv files will be written to. They will have the same name as files in the input_directory but with ```cat_``` appended to the start of the name.
* ```--startYear``` an optional argument, which year to use as the start range to calculate the reference average flow. Each monthly flow is divided by this reference average before calculating percentile rank and flow status.
* ```--endYear``` an optional argument, which year to use as the end range to calculate the reference average flow. Each monthly flow is divided by this reference average before calculating percentile rank and flow status. 


### Excel 

```StatusCalc Excel.xlsx``` can be used instead of the Python/R code to produce the flow status categories. This requires monthly averages to be calculated prior to data entry into the spreadsheet. Note to ensure consistency with the scripts, months with less than 50 % data completeness should be left blank. To modify the 'startYear' and 'endYear' parameters for calculating the reference average flow, users should modify the formulae from ```B68:M68```.
The excel files currently only support monhtly timeseries data starting on 01/1965. Excel file created by Mr. José Pablo Cantillano, Costa Rican Institute of Electricity. 

### Tests
A jupyter notebook of tests which cross-verify the results of the Python and R code on four example datasets is provided. The Python/R outputs were also cross-verified against the excel outputs, on modified datasets (with timeseries starting in 1965).

### status_csv_to_json
A Python script that converts the csv outputs of the StatusCalc Python/R script to json files for use in the HydroSOS web portal is also provided. It can process multiple files in one go.

 It should be used as follows: 
``` python status_csv_to_json.py input_directory output_directory```

For example: 
```python status_csv_to_json.py ./example_data/output_Python ./example_data/output_json```

Where:
*  ```input_directory``` is the directory containing .csv status outputs from the python/R script with the name ```cat_stationID.csv```, this naming convention must be adhered to for the script to work. The script will attempt to parse every .csv file in this directory, so remove any .csv files you don't want to be processed. See files in [example_data/output_Python](./example_data/output_Python) for how these files should look.
* ```output_directory``` is the directory the processed .csv files will be written to. They will be named based on the dates of the data being processed. 

## Forecast

This repository contains Python code to convert monthly flow forecast data into categories. This can be done using the ```ForecastCalc.py``` script which should be run as follows: 

``` python ForecastCalc.py obs_dir forecast_dir output_dir --obsDirStartingMonth```

Where:

* ```obs_dir``` contains ONLY .csv files of historic status (observed simulated) data, as daily time series. Filenames should be formatted X_CATCHMENTID.csv
* ``forecast_dir`` contains ONLY .csv files of forecast data for different ensemble members. Filenames should be formatted X_ENS_CATCHMENTID.csv
* ```output_dir``` is the name of the directory to output processed files to.
* ```--obsDirStartingMonth``` starting month in the ObsDir dataset (default january).

This script will calculate the categories (same as those in StatusCalc) that the forecasts belong to, based on both single and accumulated forecasts (results are saved into different subdirectories of output_dir).

Example: 

```python ForecastCalc.py example_data/obs_dir example_data/forecast_dir  example_data/output_forecast```

## forecast_csv_to_geotiff.py

The ```counts.csv``` file produced by ForecastCalc.py should be further processed into a .geotiff for visualisation on the portal map. This can be done using ```forecast_csv_to_geotiff.py``` which is run as follows:

```python forecast_csv_to_geotiff.py input_dir output_dir shapefile forecast_start_date --forecastLength```

Where ```input_dir``` is the ```counts``` directory produced by ```ForecastCalc.py``` that contains the forecast category counts for different months, ```output_dir``` is where the geotiffs are written, ```shapefile``` is a path to the shapefile that defines the polygons corresponding to the forecast ID boundaries that will be drawn in the geotiff, forecast_start_date is the first forecast date formatted ```YYYY-MM``` and forecast_length is the number of months forecasts were made for (default 6).

Example: 

```python forecast_csv_to_geotiff.py example_data/output_forecast/accumulated/counts example_data/output_geotiff example_data/basins.shp 2024-04 --forecastLength 6```

Info:

The HydroBasins shapefile can be downloaded here: https://www.hydrosheds.org/products/hydrobasins#downloads, note each continental shapefile will need to be merged to create a global shapefile. 


Last-updated: 10/09/2024 EK