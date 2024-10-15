"""
This script converts counts.csv files to geotiffs.
"""

import pandas as pd, argparse, os
import geopandas as gpd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from geocube.api.core import make_geocube
from functools import partial
from geocube.rasterize import rasterize_image
import rasterio
from pathlib import Path


###############################################
### SETUP 
###############################################

parser = argparse.ArgumentParser(
                    prog='Hydro SOS csv_to_json PYTHON',
                    description='Convert gridded forecast data (single and accumulated) to a single and accumulated monthly geotiff files.',
                    epilog='Gemma N, Ezra K, UKCEH, 01082024')


parser.add_argument('input_dir', help='input directory, should be set as the output directory of ForecastCalc.py.')   
parser.add_argument('output_dir', help='directory files will be saved to as {date}.json.')    
parser.add_argument('shapefile', help='path to the hydrosheds basin shapefile.')    
parser.add_argument('forecast_start_date', help='Date YYYY-MM of the first forecast.')
parser.add_argument('--forecast_length', help='length of the forecast (in months, default 6)')


args = parser.parse_args()
input_directory = args.input_dir
output_directory = args.output_dir

Path(output_directory).mkdir(parents=True, exist_ok=True)

shapefile = args.shapefile
forecastDate = datetime.strptime(args.forecast_start_date + '-01', "%Y-%m-%d")

if args.forecast_length:
    forecastLength=int(args.forecast_length)
else: 
    print("No forecast length set, defaulting to 6 months.")
    forecastLength=6


 # convert hydrobasins shapefile to geodataframe
gdf = gpd.read_file(args.shapefile, include_fields=['HYBAS_ID'])
gdf['HYBAS_ID'] = gdf['HYBAS_ID'].astype('int').fillna(0)

columns=[]
for x in range (0, forecastLength+1):
    date = (forecastDate + relativedelta(months=+x)).strftime("%Y-%m")
    columns.append(date)

#empty dataframe to append to
smhi_counts_df = pd.DataFrame(columns=columns) 


################################################
### MAIN
################################################

#ONE GEOTIFF FOR EACH MONTH WITH A NUMBER FROM 1 TO 5 FOR EACH HYDRABAS ID
#THIS SCRIPT OUTPUTS 6 GEOTIFFS EACH NAMED WITH MONTH
#GEOTIFFS ARE GLOBAL
#ADD A PARAMTTER FOR NUMBER OF MONTHS OF FORECAST (DEFAULT 6)
#THIS IS GRIDDED


#loop through the pre-generated counts files 
for file in os.listdir(input_directory + '/counts/'):
    if file.endswith('.csv'):
        #open the file
        with open(input_directory+'/counts/'+file, mode="r") as fr:
                df = pd.read_csv(fr, index_col=False)
                # Find the column with the maximum value in each row
                max_column = df.idxmax(axis=1, numeric_only=True)
                df['HYBAS_ID'] = file.split('_')[0]
                # Map column names to their corresponding index numbers
                column_mapping = {'notLow': 1, 'belNorm': 2, 'norm': 3, 'abNorm': 4, 'notHigh': 5}
                # Create the new column with the index of the column with the greatest number
                df['value'] = max_column.map(column_mapping).fillna(0)
                # pivot the df to add to the smhi_counts_df as extra column per date
                df2 = df.pivot_table(index='HYBAS_ID', columns='date', values='value')
                smhi_counts_df = pd.concat([smhi_counts_df, df2])

smhi_counts_df=smhi_counts_df.reset_index()
smhi_counts_df['HYBAS_ID'] = smhi_counts_df['index'].fillna(0).astype('int')
#output each forecat month separately 
for x in range (0, forecastLength+1):
    date = (forecastDate + relativedelta(months=+x)).strftime("%Y-%m")
    smhi_counts_df[date] = smhi_counts_df[date].fillna(0).astype('int')
    print(smhi_counts_df)
    output_df = smhi_counts_df.loc[:,['HYBAS_ID',date]]
    print(output_df)

    # Specify output GeoTIFF file path
    output_geotiff = f"{output_directory}{date}_counts.tif"
    #make all the counts values integers and fill all the missing values with -999 

    #merge the hydrobasins with the counts_df
    gdf_join = gdf.merge(output_df, left_on='HYBAS_ID', right_on='HYBAS_ID')

    #make geocube converts vector data to raster...
    out_grid = make_geocube(
        vector_data=gdf_join,
        measurements=[date],
        fill=0,
        resolution=(-0.05, 0.05), #if the resolution is greater than 0.05 it falls over as too big a dataset.
        rasterize_function=partial(rasterize_image, all_touched=True, dtype='int8')
    )

    #export the grid to a geotiff for the portal via mapserver (hydrosos_hydrobasins.map)
    out_grid.rio.to_raster(output_geotiff, driver="COG", tiled=True, windowed=True,  dtype=rasterio.uint8)