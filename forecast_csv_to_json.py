#My vpn has been very slow so it disconnected before the whole Outlook ran, so the json files only output stations from when the python restarted. 
#This code enables the whole json outputs to be created if the Outlook doesn't run in one session.

import pandas as pd, json, os, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse 
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog='esp_to_json',
                    description='Convert csv forecasts (point data) to json files to display on the portal map.',
                    epilog='Gemma N, Ezra K, UKCEH, 12082024')

parser.add_argument('forecastStartDate', help='forecast start date, formatted as YYYY-MM')   
parser.add_argument('input_directory', help='input directory')   
parser.add_argument('output_directory', help='output directory')   

args = parser.parse_args()

forecastStartDate = args.forecastStartDate
forecastDate = datetime.strptime(forecastStartDate + '-01', "%Y-%m-%d")

hydroSOS_input_directory = args.input_directory
hydroSOS_output_directory = args.output_directory

Path(hydroSOS_output_directory).mkdir(parents=True, exist_ok=True)


# six months status data for HydroSOS 
hydroSOS_statusStartDate = forecastDate + relativedelta(months=-6)
hydroSOS_date = forecastStartDate.replace('-','')

hydroSOS_accumulated_forecastMonthsList = {}
hydroSOS_single_forecastMonthsList = {}

for x in range (0, 12):
    hydroSOS_accumulated_forecastMonthsList[(forecastDate + relativedelta(months=+x)).strftime("%Y-%m")] = []
    hydroSOS_single_forecastMonthsList[(forecastDate + relativedelta(months=+x)).strftime("%Y-%m")] = []


#HydroSOS status bands json export

hydroSOSstatusBandsList = {1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[],11:[],12:[]}

for file in os.listdir(hydroSOS_input_directory + '/status/statusBands/'):
    if file.endswith('.csv'):
        with open(hydroSOS_input_directory+'/status/statusBands/'+file, mode="r") as fr:
                df = pd.read_csv(fr, index_col=False)
                df['stationID'] = file.split('_')[0]
                for row in df.iterrows():
                    hydroSOSstatusBandsList[row[1]['month']].append({
                        'stationID':row[1]['stationID'], 
                        'min':row[1]['min'], \
                        'mean':row[1]['mean'], \
                        'max':row[1]['max'], \
                        '13%':row[1]['13%'], \
                        '28%':row[1]['28%'], \
                        '72%':row[1]['72%'], \
                        '87%':row[1]['87%']
                    })

for month1 in hydroSOSstatusBandsList:
         with open(hydroSOS_output_directory+ '/status/statusBands/'+ str(month1) +'.json','w') as fw1:
            fw1.seek(0)
            json.dump(hydroSOSstatusBandsList[month1],fw1)


#HydroSOS status json export

hydroSOS_statusMonthsList = {}
for x in range (1, 7):
    hydroSOS_statusMonthsList[(forecastDate + relativedelta(months=-x)).strftime("%Y%m")] = [] 
    
for file in os.listdir(hydroSOS_input_directory + '/status/status/'):
    if file.endswith('.csv'):
        with open(hydroSOS_input_directory+'/status/status/'+file, mode="r") as fr:
                df = pd.read_csv(fr, index_col=False, parse_dates=['date'])
                df = df[df['date']>hydroSOS_statusStartDate]
                df['year'] = df['date'].dt.year.astype(float)
                df['month'] = df['date'].dt.month.astype(float)
                df['year'] = df['date'].dt.year.astype(int)
                df['month'] = df['date'].dt.month.astype(int)
                df['month'] = df['month'].apply(lambda x: '{0:0>2}'.format(x))
                df['date'] = df['year'].astype(str) + '-' + df['month'].astype(str)
                df = df.groupby(['year','month'], as_index=False)['Discharge'].mean()
                df['stationID'] = file.split('_')[0]
                for row in df.iterrows():
                    hydroSOS_statusMonthsList[str(row[1]['year'])+''+str(row[1]['month'])].append({
                    'stationID':row[1]['stationID'], 
                    'value':row[1]['Discharge']})

for month6 in hydroSOS_statusMonthsList:
        with open(hydroSOS_output_directory +'/status/status/'+ str(month6) +'_status.json','w') as fw6:
            fw6.seek(0)
            json.dump(hydroSOS_statusMonthsList[month6],fw6)

#HydroSOS accumulated counts json export

for file in os.listdir(hydroSOS_input_directory + '/accumulated/counts/'):
    if file.endswith('.csv'):
        with open(hydroSOS_input_directory+'/accumulated/counts/'+file, mode="r") as fr:
                df = pd.read_csv(fr, index_col=False)
                df['stationID'] = file.split('_')[0]
                for row in df.iterrows():
                    hydroSOS_accumulated_forecastMonthsList[row[1]['date']].append({
                    'stationID':row[1]['stationID'], 
                    'low':(row[1]['notLow']+row[1]['belNorm']), \
                    'norm':row[1]['norm'], \
                    'high':(row[1]['abNorm']+row[1]['notHigh'])})


for month4 in hydroSOS_accumulated_forecastMonthsList:
         with open(hydroSOS_output_directory +'/accumulated/counts/'+ str(month4) +'_counts.json','w') as fw4:
            fw4.seek(0)
            json.dump(hydroSOS_accumulated_forecastMonthsList[month4],fw4)

#HydroSOS single counts json export

for file in os.listdir(hydroSOS_input_directory + '/single/counts/'):
    if file.endswith('.csv'):
        with open(hydroSOS_input_directory+'/single/counts/'+file, mode="r") as fr:
                df = pd.read_csv(fr, index_col=False)
                df['stationID'] = file.split('_')[0]
                for row in df.iterrows():
                    hydroSOS_single_forecastMonthsList[row[1]['date']].append({
                    'stationID':row[1]['stationID'], 
                    'low':(row[1]['notLow']+row[1]['belNorm']), \
                    'norm':row[1]['norm'], \
                    'high':(row[1]['abNorm']+row[1]['notHigh'])})


for month4 in hydroSOS_single_forecastMonthsList:
         with open(hydroSOS_output_directory +'/single/counts/'+ str(month4) +'_counts.json','w') as fw4:
            fw4.seek(0)
            json.dump(hydroSOS_single_forecastMonthsList[month4],fw4)

