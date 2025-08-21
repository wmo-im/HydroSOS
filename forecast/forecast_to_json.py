# import required packages
import pandas as pd, os, argparse
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog='Hydro SOS forecast_to_json PYTHON',
                    description='Convert categorgised statiforecaston (point data) monthly status.csv to a single monthly json file.',
                    epilog='Ezra K, UKCEH, 03062024')


parser.add_argument('input_directory', help='input directory, should ONLY contain .csv monthly categorised status (point data) files, see GitHub for examples.')   
parser.add_argument('output_directory', help='directory files will be saved to as {date}.json')     

args = parser.parse_args()
allFilesDF = pd.DataFrame()

# read the CSV files in the data directory
for index, filename in enumerate(os.listdir(args.input_directory)):
        with open(args.input_directory+'/'+filename, mode="r") as fr:
            if filename.endswith('.csv'):
                df = pd.read_csv(fr)
                filename = os.path.splitext(str(filename))[0] #remove file extenstion
                stationID = filename.split('_')[0] #remove _counts
                df['stationID'] = stationID
                allFilesDF = pd.concat([allFilesDF,df])

allFilesDF['date'] = pd.to_datetime(allFilesDF['date'])
allFilesDF = allFilesDF.sort_values(by='date', ascending=True)
allFilesDF.drop_duplicates(inplace=True)
allFilesDF.set_index(['date'], inplace=True)

Path(args.output_directory+'/json_output').mkdir(parents=True, exist_ok=True)
for date in allFilesDF.index:
    #this happens if there is only one record
    if type(allFilesDF.loc[date]) == pd.core.series.Series:
        pd.DataFrame(allFilesDF.loc[date]).T.to_json(f"{args.output_directory}/json_output/{date.strftime('%Y-%m')}.json", orient = 'records')
    else: 
        allFilesDF.loc[date].to_json(f"{args.output_directory}/json_output/{date.strftime('%Y-%m')}.json", orient = 'records')