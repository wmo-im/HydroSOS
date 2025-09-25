"""
BASED ON STATUSCALCV2.R BY KATIE FACER-CHILDS
EZRA KITSON  25-09-2025
"""

import argparse
import pandas as pd
import numpy as np
import os
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog='StatusCalc v3 PYTHON',
                    description='Calculates status based on daily timeseries for the HydroSOS portal',
                    epilog='Katie F-C, Ezra K, UKCEH, 14052024')


parser.add_argument('input_directory', help='input directory, should ONLY contain .csv daily timeseries, see GitHub for examples.')        
parser.add_argument('output_directory', help='directory files will be saved to as cat_{input_file}.csv')     
parser.add_argument('--startYear', help='start of the year range that will be used to calculate the reference average.')
parser.add_argument('--endYear', help='end of the year range that will be used to calculate the reference average.')
parser.add_argument('--debugging', help='print debugging')

args = parser.parse_args()

if args.startYear:
    stdStart=int(args.startYear)
else: 
    print("No start year set, defaulting to 1991.")
    stdStart=1991

if args.endYear:
    stdEnd=int(args.endYear)
else: 
    print("No end year set, defaulting to 2020.")
    stdEnd=2020

assert stdStart < stdEnd, "startYear must be greater than endYear"

#stationid="39001"
#input_directory="./example_data/input/"
#output_directory="./example_data/output_Python/"

Path(args.output_directory).mkdir(parents=True, exist_ok=True)
Path(f"{args.output_directory}/statusBands").mkdir(parents=True, exist_ok=True)

for f in os.listdir(args.input_directory):

    if f.endswith('.csv'):
        print(f)
        flowdata = pd.read_csv(f"{args.input_directory}{f}")
        flowdata.columns = ['date','flow']
        flowdata['date'] = pd.to_datetime(flowdata['date'], format="%d/%m/%Y")

        #check dates are sequential
        diff = pd.date_range(start = flowdata['date'].min(), end = flowdata['date'].max() ).difference(flowdata['date'])
        if len(diff) > 0:
            flowdata.set_index('date', inplace=True)
            for md in diff: 
                flowdata.loc[md,'flow'] = pd.NA
            flowdata.reset_index(inplace=True)

        #month and year column
        flowdata['month'] = flowdata['date'].dt.month
        flowdata['year'] = flowdata['date'].dt.year

        #check whether or not there is enough data? 
        print(f"There are {flowdata['year'].max() - flowdata['year'].min()} years of data in this file.")
        print(f"There are {sum(flowdata['flow'].isnull())} missing data points, which is {np.round(sum(flowdata['flow'].isnull())/len(flowdata) * 100,4)}% of the total data")

        """ STEP 1: CALCULATE MEAN MONTHLY FLOWS """

        #calculate percentage completeness for each year/month
        groupBy = (flowdata.groupby(['month','year']).count()['flow']/flowdata.groupby(['month','year']).count()['date']) * 100
        groupBy = pd.DataFrame(groupBy)
        groupBy.rename(columns={0:'monthly%'}, inplace=True)
        #calculate mean flows for each year/month
        groupBy['mean_flow'] = flowdata.groupby(['month','year'])['flow'].mean()
        #set the mean flow to NAN if there is less than 50 % data
        groupBy.loc[groupBy['monthly%'] < 50,'mean_flow'] = pd.NA
        groupBy.reset_index(inplace=True)

        """ STEP 2: CALCULATE MEAN MONTHLY FLOWS AS A PERCENTAGE OF AVERAGE REFERENCE PERIOD """

        #calculate long term average
        LTA = groupBy[(groupBy['year'] >= stdStart) & (groupBy['year'] <= stdEnd)].groupby(['month'])['mean_flow'].mean()

        #divide each month by this long term average
        skip_file = False
        for i in range(1,13):
            if i not in LTA.index:
                print("ERROR: Month %i missing in Long Term Average for file %s. Skipping file" % (i,f))
                skip_file = True
                break
            groupBy.loc[groupBy['month'] == i,'percentile_flow'] = groupBy['mean_flow'][groupBy['month'] == i]/LTA[i] * 100

        if skip_file:
            continue

        """ STEP 3: CALCULATE RANK PERCENTILES OF REFERENCE PERIOD """

        refBy = groupBy[(groupBy['year'] >= stdStart) & (groupBy['year'] <= stdEnd)]

        # na values automatically set as rank na
        for i in range(1,13):
            refBy.loc[refBy['month'] == i, 'weibell_rank'] = refBy.loc[refBy['month'] == i, 'percentile_flow'].rank(na_option='keep')/(refBy.loc[refBy['month'] == i, 'percentile_flow'].count()+1)

        targetRanks = {0.10,0.25,0.75,0.9}
        thresholdDict = {}

        for i in range(1,13):
            ranks = np.array(refBy.loc[refBy['month'] == i, 'weibell_rank'])
            percentiles = np.array(refBy.loc[refBy['month'] == i, 'percentile_flow'])
            for j in targetRanks:
                #find the closest rank to the target ranks above and below
                lower_vals = ranks[ranks <= j]
                higher_vals = ranks[ranks >= j]
                closest_higher = np.min(higher_vals) if higher_vals.size > 0 else False
                closest_lower = np.max(lower_vals) if lower_vals.size > 0 else False
                closest_higher_idx = np.where(ranks == closest_higher)[0][0] if closest_higher else False
                closest_lower_idx = np.where(ranks == closest_lower)[0][0] if closest_lower else False
                #find the percentile values matching to the closet rank
                higher_percentile = percentiles[closest_higher_idx] if closest_higher_idx else False
                lower_percentile = percentiles[closest_lower_idx] if closest_lower_idx else False
                #use a linear interpolation to get the percentile value of the target rank based on these two values
                # this occurs if the target rank perfectly matches an observed rank
                if higher_percentile == lower_percentile:
                    interpolated_percentile = lower_percentile
                # this occurs if no observed ranks were higher than the target rank, in which case set as the lower percentile
                elif higher_percentile == False:
                    interpolated_percentile = lower_percentile
                # this occurs if no observed ranks were lower than the target rank, in which case set as the higher percentile
                elif lower_percentile == False:
                    interpolated_percentile = higher_percentile
                # otherwise linearly interpolate the percentile value from the closest higher and lower 
                else:
                    interpolated_percentile = lower_percentile + ((j - closest_lower) / (closest_higher - closest_lower)) * (higher_percentile - lower_percentile) 
                if args.debugging: 
                    print(f"Month : {i}")
                    print(f"Percentiles in ref: {percentiles}")
                    print(f"Ranks in ref: {ranks}")
                    print(f"Target rank: {j}")
                    print(f"Closest lower rank: {closest_lower}")
                    print(f"Closest  higher rank: {closest_higher}")
                    print(f"Closest lower percentile: {lower_percentile}")
                    print(f"Closest higher percentile: {higher_percentile}")
                    print(f"Interpolated percentile: {interpolated_percentile}")
                #add this to the threshold dictionary
                thresholdDict[i,j] = interpolated_percentile
                #add min, mean and max to thresholdDict to 
                thresholdDict[i,'max'] = np.nanmax(percentiles)
                thresholdDict[i,'median'] = np.nanmedian(percentiles)
                thresholdDict[i,'min'] = np.nanmin(percentiles)

        """ STEP 4: ASSIGN STATUS CATEGORIES """

        def flow_status(percentile, month, thresholdDict):
            status = pd.NA
            if percentile <= thresholdDict[month,0.1]:
                status = 1
            elif percentile <= thresholdDict[month,0.25]:
                status = 2
            elif percentile <= thresholdDict[month,0.75]:
                status = 3
            elif percentile <= thresholdDict[month,0.9]:
                status = 4
            elif percentile > thresholdDict[month,0.9]:
                status = 5
            return status

        for i in groupBy.index:
            groupBy.loc[i,'category'] = flow_status(percentile=groupBy.loc[i,'percentile_flow'],month=groupBy.loc[i,'month'],thresholdDict=thresholdDict)


        """ STEP 5: WRITE DATA """
        groupBy['date'] = pd.to_datetime(groupBy[['year', 'month']].assign(DAY=1))
        groupBy['date'] = groupBy['date'].dt.strftime('%Y-%m-%d')
        groupBy['category'] = groupBy['category'].astype('Int64')
        groupBy.sort_values(['year','month']).filter(['date','category']).to_csv(f"{args.output_directory}cat_{f}", index=False)
        forecastBands = pd.DataFrame.from_dict(pd.Series(thresholdDict).unstack())
        forecastBands.to_csv(f"{args.output_directory}/statusBands/{f.split('.')[0]}_bands.csv")
       




        
