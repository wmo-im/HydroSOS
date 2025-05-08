"""
This script takes the combined output from ESP and reformats it into separate status (obsDir) and forecast (forecastDir) directories.
For forecasts, it also separates out individual ENS members into their own files. This means the output can directly be parsed by StatusCalc and ForecastCalc.
"""

import pandas as pd
import argparse
import os
from pathlib import Path
from datetime import date

parser = argparse.ArgumentParser(
                    prog='reformatESP',
                    description='Reformats ESP data so it can be run by the HydroSOS processing scripts',
                    epilog='Ezra K, UKCEH, 15082024')

parser.add_argument('forecast_date', help='forecast date, forecast date, should contain the date of the ESP forecast of interest, as YYYY-MM.')        
parser.add_argument('input_directory', help='input directory, should ONLY contain combined ESP model run data, see GitHub for examples.')        
parser.add_argument('output_directory', help='output directory, where files will be outputted to.')

args = parser.parse_args()

forecast_date = args.forecast_date
forecastMonth = forecast_date.split('-')[1]
forecastYear = forecast_date.split('-')[0]

if int(forecastMonth) < 10:
    filenamePart = f"{forecastYear}{int(forecastMonth)}" # if forecast month < 10, input files are at yyyym else yyyymm
else:
    filenamePart = f"{forecastYear}{forecastMonth}"

#make output subdirectories
Path(f"{args.output_directory}/forecastDir").mkdir(parents=True, exist_ok=True)
Path(f"{args.output_directory}/obsDir").mkdir(parents=True, exist_ok=True)

#list the files
files = os.listdir(args.input_directory)
for f in files:
    #check the file is a .csv
    if f.endswith('.csv'):
        #check the file is the right year
        if f.split('_')[2] == filenamePart:
            id = f.split('_')[0]
            data = pd.read_csv(f"{args.input_directory}/{f}")
            #rename date
            data.rename(columns={'DATE':'Date'}, inplace=True)
            # filter the data to just obsSim and write to obsDir
            status = data.filter(['Date','obsSim'])
            status = status[status['obsSim'].notnull()]
            status.rename(columns={'obsSim':'Discharge'}, inplace=True)
            status.to_csv(f"{args.output_directory}/obsDir/ESP_{id}.csv", index=False)
            # filter the data to just ENS members, and average by month (forecasts should be daily)
            data = data[data['obsSim'].isnull()]
            data['Date'] = pd.to_datetime(data['Date'])
            data['year'] = data['Date'].dt.year.astype(int)
            data['month'] = data['Date'].dt.month.astype(int)
            data = data.groupby(['year','month']).mean(numeric_only=True)
            data.reset_index(inplace=True)
            data['Date'] = pd.to_datetime({'year':data['year'], 'month':data['month'], 'day':1})
            #for the hydrosos script, the obs data needs to start in january 
            for col in data.columns:
                if 'ENS' in col:
                    forecast = data.filter(['Date',col])
                    forecast.rename(columns={col:'Discharge'}, inplace=True)
                    forecast.to_csv(f"{args.output_directory}/forecastDir/ESP_{col}_{id}.csv", index=False)

            
