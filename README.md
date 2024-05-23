# Hydrological Status and Outlook System
Hydrological Status and Outlook System (HydroSOS)

## R Code
The R Code can calculate flow status categories for an individual flow station timeseries saved in a .csv file. See files in [example_data/input](./example_data/input) for how these timeseries files should look. 
To run the R code, edit lines 14,15,16, (possibly 27 & 79), 88,89 and then run the script inside an R environment. If you have multiple files, you will have to run the script separately for each one, changing the relevant lines as appropriate. 

## Python Code
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


## Excel 

```StatusCalc Excel.xlsx``` can be used instead of the Python/R code to produce the flow status categories. This requires monthly averages to be calculated prior to data entry into the spreadsheet. Note to ensure consistency with the scripts, months with less than 50 % data completeness should be left blank. To modify the 'startYear' and 'endYear' parameters for calculating the reference average flow, users should modify the formulae from ```B68:M68```.
The excel files currently only support monhtly timeseries data starting on 01/1965.  

## Tests
A jupyter notebook of tests which cross-verify the results of the Python and R code on four example datasets is provided. The Python/R outputs were also cross-verified against the excel outputs, on modified datasets (with timeseries starting in 1965).

## csv_to_json
A Python script that converts the csv outputs of the Python/R script to json files for use in the HydroSOS web portal is also provided. It can process multiple files in one go.

 It should be used as follows: 
``` python csv_to_json.py input_directory output_directory```

For example: 
```python csv_to_json.py ./example_data/output_Python ./example_data/output_json```

Where:
*  ```input_directory``` is the directory containing .csv status outputs from the python/R script with the name ```cat_stationID.csv```, this naming convention must be adhered to for the script to work. The script will attempt to parse every .csv file in this directory, so remove any .csv files you don't want to be processed. See files in [example_data/output_Python](./example_data/output_Python) for how these files should look.
* ```output_directory``` is the directory the processed .csv files will be written to. They will be named based on the dates of the data being processed. 

Last-updated: 23/05/2024 EK