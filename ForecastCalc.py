"""
This script takes a set of observed simulated discharge data, and a set of monthly forecasts into the future for a given catchment. 
It computes forecast bands on the observed simulated discharge data based on quantiles estimated using the cunnane empirical quantile function.
It then applies those forecast bands to the forecasts (as accumulated monthly means).

Usage

Python ForecastCalc.py obs_dir forecast_dir output_dir

Where obs_dir and forecast_dir are directories containing csv files with observed simulated and forecast data in them. See the example_data for how these files should be formatted. 


V1 Gemma Nash/Ezra Kitson UKCEH 24072024
"""

##############################################
# Libraries
##############################################

import pandas as pd, os
from pathlib import Path
from scipy.stats.mstats import mquantiles
import argparse


##############################################
# Input 
##############################################
print("**************************************")
print("Input:")
print("Parsing arguments.")

parser = argparse.ArgumentParser(
                    prog='ForecastCalc PYTHON',
                    description='Calculates flow status based on daily flow timeseries for the HydroSOS portal',
                    epilog='Gemma N, Ezra K, UKCEH, 25057024')

parser.add_argument('obs_dir', help='directory containing obsserved simulated (obssim) discharge data as timeseries, should ONLY contain .csv daily flow timeseries, filenames should be formatted X_CATCHMENTID.csv see GitHub for examples.')        
parser.add_argument('forecast_dir', help='directory containing forecast discharge data for the next X months, should only contain .csv monthly flow forecasts, filenames should be formatted X_ENS_CATCHMENTID.csv, see GitHub for examples.')     
parser.add_argument('output_dir', help=
                    'directory files will be saved to. Four sub directories will be created in this directory forecastBand, forecasts, counts and percentiles') 
parser.add_argument('--obsDirStartingMonth', help='Starting month in the obsDir dataset (default january)') 



args = parser.parse_args()

forecast_directory = args.forecast_dir
status_directory = args.obs_dir
output_directory = args.output_dir

print('Making output directories.')

#make output subdirectories
Path(output_directory+'/accumulated/counts').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/accumulated/forecastBands').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/accumulated/forecasts').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/accumulated/percentiles').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/accumulated/status').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/accumulated/statusBands').mkdir(parents=True, exist_ok=True)

Path(output_directory+'/single/counts').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/single/forecastBands').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/single/forecasts').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/single/percentiles').mkdir(parents=True, exist_ok=True)

Path(output_directory+'/status/status').mkdir(parents=True, exist_ok=True)
Path(output_directory+'/status/statusBands').mkdir(parents=True, exist_ok=True)

#calculate the forecast month 
forecast_month = int(pd.read_csv(f"{forecast_directory}/{os.listdir(forecast_directory)[0]}").loc[0,'Date'].split('-')[1])
print(f"First forecast month set as {forecast_month}. \n")

#calculate which row to slice the obs sim data with
if args.obsDirStartingMonth:
    print(f"Obs Dir Starting month set as {int(args.obsDirStartingMonth)}.")
    obsSimSlice = forecast_month - int(args.obsDirStartingMonth)
    if obsSimSlice < 0: 
        obsSimSlice = 12 + obsSimSlice
    print(f"Obs sim slicing starts from row {obsSimSlice}")
else:
    print(f"Obs Dir Starting month set as january.")
    obsSimSlice = forecast_month -1
    print(f"Obs sim slicing starts from row {obsSimSlice}")


##############################################
# Functions 
##############################################

#get monthly average of obsSim column
def getStatus(df):
    monthlyMeans =  df.groupby(['year','month'], as_index=False)['Discharge'].mean()
    monthlyMeans['month'] = monthlyMeans['month'].apply(lambda x: '{0:0>2}'.format(x))
    monthlyMeans['date'] = monthlyMeans['year'].astype(str) + '-' + monthlyMeans['month'].astype(str)
    status = monthlyMeans[['date','Discharge']]
    return status


#get percentiles of monthly obsSim data to make the status climatology categories
def createStatusBands(df):
    bands = pd.DataFrame()
    monthlyMeans = df.groupby(['year','month'], as_index=False)['Discharge'].mean()
    pivotedMeans = monthlyMeans.pivot(index='month', columns='year', values='Discharge')
    bands['min'] = pivotedMeans.min(axis=1)
    bands['mean'] = pivotedMeans.mean(axis=1)
    bands['max'] = pivotedMeans.max(axis=1)
    bands['month'] = bands.index
    empirical_quantiles = mquantiles(pivotedMeans, prob=[.05,.13,.28,.72,.87,.95], alphap=.4, betap=.4, axis=1)
    bands['5%'] = empirical_quantiles[:,0]
    bands['13%'] = empirical_quantiles[:,1]
    bands['28%'] = empirical_quantiles[:,2]
    bands['72%'] = empirical_quantiles[:,3]
    bands['87%'] = empirical_quantiles[:,4]
    bands['95%'] = empirical_quantiles[:,5]
    return bands

#for all ENS columns, get monthly accumulated average
def getAccumulatedForecasts(df):
    accumulatedMonthlyMeans = pd.DataFrame()
    accumulatedMonthlyMeans['date'] = df['date']
    columns = df.columns.values
    ens_columns = list(filter(lambda k: 'ENS' in k, columns))
    for column in ens_columns:
        accumulatedMonthlyMeans[column] = df[column].expanding().mean()
    output_columns = ens_columns
    output_columns.insert(0,'date')
    accumulatedMonthlyMeans.columns = output_columns
    return accumulatedMonthlyMeans

#get percentiles of accumulated monthly Discharge data to make the forecast climatology categories
def createAccumulatedForecastBands(df):
    bands = pd.DataFrame()
    monthlyMeans = df.groupby(['year','month'], as_index=False)['Discharge'].mean()
    reshapedDF = pd.DataFrame()
    start = obsSimSlice
    ticker = obsSimSlice
    for i in range(start,len(monthlyMeans.index)):
        if (i + 1) % 12 == ticker:  # the modulo operation
            reshapedDF['Obs'+str(start)] = monthlyMeans['Discharge'].iloc[start:i+1].values.reshape(12)
            start = i + 1  # set start to next index
    accumulatedMean = pd.DataFrame()
    for column in reshapedDF:
        accumulatedMean[column] = reshapedDF[column].expanding().mean()
    bands['min'] = accumulatedMean.min(axis=1)
    bands['mean'] = accumulatedMean.mean(axis=1)
    bands['max'] = accumulatedMean.max(axis=1)
    #compute empirical quantiles 
    empirical_quantiles = mquantiles(accumulatedMean, prob=[.05,.13,.28,.72,.87,.95], alphap=.4, betap=.4, axis=1)
    bands['5%'] = empirical_quantiles[:,0]
    bands['13%'] = empirical_quantiles[:,1]
    bands['28%'] = empirical_quantiles[:,2]
    bands['72%'] = empirical_quantiles[:,3]
    bands['87%'] = empirical_quantiles[:,4]
    bands['95%'] = empirical_quantiles[:,5]
    bands['relative_month']=bands.index+1
    return bands

#get percentiles of single monthly Discharge data to make the forecast climatology categories
def createSingleForecastBands(df):
    bands = pd.DataFrame()
    monthlyMeans = df.groupby(['year','month'], as_index=False)['Discharge'].mean()
    reshapedDF = pd.DataFrame()
    start = obsSimSlice
    ticker = obsSimSlice
    for i in range(start,len(monthlyMeans.index)):
        if (i + 1) % 12 == ticker:  # the modulo operation
            reshapedDF['Obs'+str(start)] = monthlyMeans['Discharge'].iloc[start:i+1].values.reshape(12)
            start = i + 1  # set start to next index
    #row one of reshaped Df witll be the yearly values of forecast month for different years
    bands['min'] = reshapedDF.min(axis=1)
    bands['mean'] = reshapedDF.mean(axis=1)
    bands['max'] = reshapedDF.max(axis=1)
    #compute empirical quantiles 
    empirical_quantiles = mquantiles(reshapedDF, prob=[.05,.13,.28,.72,.87,.95], alphap=.4, betap=.4, axis=1)
    bands['5%'] = empirical_quantiles[:,0]
    bands['13%'] = empirical_quantiles[:,1]
    bands['28%'] = empirical_quantiles[:,2]
    bands['72%'] = empirical_quantiles[:,3]
    bands['87%'] = empirical_quantiles[:,4]
    bands['95%'] = empirical_quantiles[:,5]
    bands['relative_month']=bands.index+1
    return bands


#get the percentiles and min, mean and max, of the ENS columns for the HydroSOS percentages graphs
def getForecastPercentiles(forecasts):
    columns = forecasts.columns.values
    columns = list(filter(lambda k: 'ENS' in k, columns))
    arr = forecasts[columns]
    arrMin = arr.min(axis=1)
    arrMean = arr.mean(axis=1)
    arrMax = arr.max(axis=1)
    empirical_quantiles = mquantiles(arr, prob=[.13,.28,.72,.87], alphap=.4, betap=.4, axis=1)
    percentile13 = empirical_quantiles[:,0]
    percentile28 = empirical_quantiles[:,1]
    percentile72 = empirical_quantiles[:,2]
    percentile87 = empirical_quantiles[:,3]
    percentiles = pd.DataFrame({'date':forecasts['date'],'min':arrMin,'mean':arrMean,'max':arrMax,'13%':percentile13,'28%':percentile28,'72%':percentile72,'87%':percentile87})
    return percentiles

#count up how many of the ENS columns for a month fit into each of the forecast bands for the counts graphs
def getForecastCounts(percentiles, forecasts, bands): 
    forecasts.index = range(len(forecasts))
    columns = forecasts.columns.values
    Ens_data_cat = pd.DataFrame(columns=columns)
    Ens_data_cat.set_index(columns[0])
    columns = list(filter(lambda k: 'ENS' in k, columns))
    for idx, row in forecasts.iterrows():
        output = []
        output.append(row['date'])
        for column in columns:
            if (row[column] < bands.iloc[idx][percentiles[0]]):
                output.append(int(1))
            elif bands.iloc[idx][percentiles[0]] <= row[column] < bands.iloc[idx][percentiles[1]]:
                output.append(int(2))
            elif bands.iloc[idx][percentiles[1]] <= row[column] < bands.iloc[idx][percentiles[2]]:
                output.append(int(3))
            elif bands.iloc[idx][percentiles[2]] <= row[column] < bands.iloc[idx][percentiles[3]]:
                output.append(int(4))
            elif (row[column] >= bands.iloc[idx][percentiles[3]]):
                output.append(int(5))
        Ens_data_cat.loc[len(Ens_data_cat)] = output
    counts = pd.DataFrame(columns=['date','notLow','belNorm','norm','abNorm','notHigh'])
    for index, row in Ens_data_cat.iterrows():
        counts.loc[len(counts)] = [row[0],sum(row==1),sum(row==2),sum(row==3),sum(row==4),sum(row==5)]
    return counts


##############################################
# Main 
##############################################

print("Main:")

#get a set of all the catchment IDs to loop through later...
catchmentList = []
for filename in os.listdir(forecast_directory):
    if filename.endswith('.csv'): 
        filenameParts = filename.split('_')
        catchmentID = filenameParts[2]
        catchmentList.append(catchmentID)

catchmentIDs = set(catchmentList)


# for catchment in the set above...
idCounter = 1 
for id in catchmentIDs:
    cid = id.split('.csv')[0]
    print(f"Processing {id} ({idCounter}/{len(catchmentIDs)}).")
    idCounter += 1 
    # create a new dataframe to hold all the ENS runs as they're all separate atm
    fullDF = pd.DataFrame()
    # columns to export for full ens csv
    columns = ['date']
    # loop through the whole forecast folder
    for filename in os.listdir(forecast_directory):
        if filename.endswith('.csv'): 
            filenameParts = filename.split('_')
            catchmentID = filenameParts[2]
            # if the catchment id matches the filename
            if catchmentID == id: 
                # add the ENS to the columns for the export
                ENS = 'ENS'+filenameParts[1]
                columns.append(ENS)
                # open the forecast file and add it to the fullDF to export.
                with open(forecast_directory+'/'+filename, mode="r") as fr:
                    csvFile = pd.read_csv(fr, parse_dates=['Date'])
                    df = pd.DataFrame(csvFile)
                    df['date'] = pd.to_datetime(df['Date'])
                    df['year'] = df['date'].dt.year.astype(float)
                    df['month'] = df['date'].dt.month.astype(float)
                    df['year'] = df['date'].dt.year.astype(int)
                    df['month'] = df['date'].dt.month.astype(int)
                    fullDF['date'] = df['date']
                    fullDF['year'] = df['year']
                    fullDF['month'] = df['month']
                    fullDF[ENS] = df['Discharge'] # add the value for this ensemble member to the full df.
   
                
    #export the full forecast with all the ensemble members
    fullDF.reset_index()
    fullDF['month'] = fullDF['month'].astype(int).apply(lambda x: '{0:0>2}'.format(x))
    fullDF['date'] = fullDF['year'].astype(str) + '-' + fullDF['month'].astype(str)
    
    #once have the ENS all in one file, use it to create accumulated forecasts
    accumulated_forecasts = getAccumulatedForecasts(fullDF) #GOOD
    accumulated_forecasts.to_csv(output_directory +'/accumulated/forecasts/'+ cid +'_forecasts.csv', header=True, index=False, float_format='%.4f')
     
    #single forecasts is just fullDF minus year and month
    fullDF.to_csv(output_directory+'/single/forecasts/'+ cid +'_forecasts.csv', index=False, columns=columns)
    single_forecasts = fullDF.drop(columns=['year','month'])

    # no compute counts of accumulated and single forecasts
    status_files = os.listdir(status_directory)
    for f in status_files:
        #in status files, the first underscore split contains the catchment id
        if f.split('_')[1] == id:
            with open(f"{status_directory}/{f}", mode="r") as status_fr:
                statusDF = pd.read_csv(status_fr, parse_dates=['Date'])
                statusDF['date'] = pd.to_datetime(statusDF['Date'])
                statusDF['year'] = statusDF['date'].dt.year.astype(float)
                statusDF['month'] = statusDF['date'].dt.month.astype(float)
                statusDF['year'] = statusDF['date'].dt.year.astype(int)
                statusDF['month'] = statusDF['date'].dt.month.astype(int)
            #write the status data
            status = getStatus(statusDF)
            status.to_csv(output_directory +'/status/status/'+ cid +'_status.csv', header=True, index = False, float_format='%.4f', columns=['date','Discharge'])
            statusBands = createStatusBands(statusDF)
            statusBands.to_csv(output_directory+'/status/statusBands/'+ cid +'_bands.csv', index=False, float_format='%.4f')
            #write accumulated forecasts
            accumulatedForecastBands = createAccumulatedForecastBands(statusDF) #GOOD
            accumulatedForecastBands.to_csv(output_directory +'/accumulated/forecastBands/'+ cid +'_bands.csv', index=False, float_format='%.4f', columns =['relative_month', 'min', 'mean', 'max', '13%', '28%', '72%', '87%'])
            accumulatedForecastPercentiles = getForecastPercentiles(accumulated_forecasts) #GOOD
            accumulatedForecastPercentiles.to_csv(output_directory +'/accumulated/percentiles/'+ cid +'_percentiles.csv', header=True, index = False, float_format='%.4f')
            accumulatedCounts = getForecastCounts(['13%','28%','72%','87%'], accumulated_forecasts, accumulatedForecastBands)
            accumulatedCounts.to_csv(output_directory +'/accumulated/counts/'+ cid +'_counts.csv', index=False)
            #write single forecasts
            singleForecastBands = createSingleForecastBands(statusDF)
            singleForecastBands.to_csv(output_directory +'/single/forecastBands/'+ cid +'_bands.csv', index=False, float_format='%.4f', columns =['relative_month', 'min', 'mean', 'max', '13%', '28%', '72%', '87%'])
            singleForecastPercentiles = getForecastPercentiles(single_forecasts) #GOOD
            singleForecastPercentiles.to_csv(output_directory +'/single/percentiles/'+ cid +'_percentiles.csv', header=True, index = False, float_format='%.4f')
            singleCounts = getForecastCounts(['13%','28%','72%','87%'], single_forecasts, singleForecastBands)
            singleCounts.to_csv(output_directory +'/single/counts/'+ cid +'_counts.csv', index=False)
            
print("**************************************")
