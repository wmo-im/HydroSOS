"""
BASED ON STATUSCALCV2.R BY KATIE FACER-CHILDS
EZRA KITSON  13-05-2024 
"""

import argparse
import pandas as pd
import numpy as np
import os

parser = argparse.ArgumentParser(
                    prog='StatusCalc v3 PYTHON',
                    description='Calculates flow status based on daily flow timeseries for the HydroSOS portal',
                    epilog='Katie F-C, Ezra K, UKCEH, 14052024')


parser.add_argument('input_directory', help='input directory, should ONLY contain .csv daily flow timeseries, see GitHub for examples.')        
parser.add_argument('output_directory', help='directory files will be saved to as cat_{input_file}.csv')     
parser.add_argument('--startYear', help='start of the year range that will be used to calculate the reference average.')
parser.add_argument('--endYear', help='end of the year range that will be used to calculate the reference average.')

args = parser.parse_args()

if args.startYear:
    stdStart=args.startYear
else: 
    print("No start year set, defaulting to 1991.")
    stdStart=1991

if args.endYear:
    stdEnd=args.endYear
else: 
    print("No end year set, defaulting to 2020.")
    stdEnd=2020

assert stdStart < stdEnd, "startYear must be greater than endYear"

#stationid="39001"
#input_directory="./example_data/input/"
#output_directory="./example_data/output_Python/"


for f in os.listdir(args.input_directory):

    if f.endswith('.csv'):
        print(f)
        flowdata = pd.read_csv(f"{args.input_directory}{f}")
        print(flowdata)
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

        """ STEP 2: CALCULATE MEAN MONTHLY FLOWS AS A PERCENTAGE OF AVERAGE """

        #calculate long term average
        LTA = groupBy[(groupBy['year'] >= 1991) & (groupBy['year'] <= 2020)].groupby(['month'])['mean_flow'].mean()

        #divide each month by this long term average
        for i in range(1,13):
            groupBy.loc[groupBy['month'] == i,'percentile_flow'] = groupBy['mean_flow'][groupBy['month'] == i]/LTA[i] * 100

        """ STEP 3: CALCULATE RANK PERCENTILES """
        # na values automatically set as rank na
        for i in range(1,13):
            groupBy.loc[groupBy['month'] == i, 'weibell_rank'] = groupBy.loc[groupBy['month'] == i, 'percentile_flow'].rank(na_option='keep')/(groupBy.loc[groupBy['month'] == i, 'percentile_flow'].count()+1)

        """ STEP 4: ASSIGN STATUS CATEGORIES """

        def flow_status(weibell_rank):
            status = pd.NA
            if weibell_rank <= 0.13:
                status = 1
            elif weibell_rank <= 0.28:
                status = 2
            elif weibell_rank <= 0.71999:
                status = 3
            elif weibell_rank <= 0.86999:
                status = 4
            elif weibell_rank <= 1:
                status = 5
            return status

        for i in groupBy.index:
            groupBy.loc[i,'flowcat'] = flow_status(groupBy.loc[i,'weibell_rank'])


        """ STEP 5: WRITE DATA """
        groupBy['date'] = pd.to_datetime(groupBy[['year', 'month']].assign(DAY=1))
        groupBy['date'] = groupBy['date'].dt.strftime('%Y-%m-%d')
        groupBy['flowcat'] = groupBy['flowcat'].astype('Int64')
        groupBy.sort_values(['year','month']).filter(['date','flowcat']).to_csv(f"{args.output_directory}cat_{f}", index=False)
        