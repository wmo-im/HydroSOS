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


## Tests
A jupyter notebook of tests which cross-verify the results of the Python and R code on four example datasets is provided. 


Last-updated: 15/05/2024 