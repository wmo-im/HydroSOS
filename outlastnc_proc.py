"""
This script converts status and forecast (single) netcdf files provided by OUTLAST into the counts.csv files and geotiffs needed to display the data on the portal. 

It requires three positional arguments

1. statusInput 
2. forecastInput
3. hydrobasins level 04 shapefile input
4. outputPath

It can take four positional arguments 
1.--statusStart YYYY-MM
2.--statusEnd YYYY-MM
3.--forecastStart YYYY-MM
4.--forecastEnd YYYY-MM

If you don't provide the positional arguments, the script will try and infer them from the nc file metadata.

"""

import argparse
import netCDF4 as nc
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from geocube.api.core import make_geocube
from functools import partial
from geocube.rasterize import rasterize_image
import rasterio

parser = argparse.ArgumentParser(
                    prog='Hydro SOS csv_to_json PYTHON',
                    description='Convert gridded forecast data (single and accumulated) to a single and accumulated monthly geotiff files.',
                    epilog='Ezra K, UKCEH, 15102024')

#positional
parser.add_argument('status_input', help='path to status .nc file')   
parser.add_argument('forecast_input', help='path to forecast .nc file')    
parser.add_argument('shapefile', help='path to the hydrosheds basin shapefile.')    
parser.add_argument('outputPath', help='path to where data will be saved.')

#optional 
parser.add_argument('--statusStart', help='YYYY-MM start of status data')   
parser.add_argument('--statusEnd', help='YYYY-MM +1 end of status data')   
parser.add_argument('--forecastStart', help='YYYY-MM start of forecast data')   
parser.add_argument('--forecastEnd', help='YYYY-MM +1 end of forecast data')   


#########################
# Setup 
#########################
args = parser.parse_args()

#make paths
print('making filepaths')
print()
Path(f'{args.outputPath}/counts/status/outlast/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/counts/status/hydrosos/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/counts/forecast/outlast/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/counts/forecast/hydrosos/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/geotiff/status/outlast/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/geotiff/status/hydrosos/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/geotiff/forecast/outlast/').mkdir(parents=True, exist_ok=True)
Path(f'{args.outputPath}/geotiff/forecast/hydrosos/').mkdir(parents=True, exist_ok=True)

gdf = gpd.read_file(args.shapefile, include_fields=['HYBAS_ID'])
gdf['HYBAS_ID'] = gdf['HYBAS_ID'].astype('int').fillna(0)

##############################
# Main
##############################

#process status data
fileName = args.status_input
data = nc.Dataset(fileName)

if args.statusStart and args.statusEnd: 
    print('using custom statusStart and end')
    status_daterange = pd.date_range(start=args.statusStart,end=args.statusEnd, freq='1M')
    status_daterange=status_daterange.strftime("%Y-%m")
else: 
    print('reading status daterange from file')
    start=pd.DatetimeIndex([data['time'].units.split('days since')[1]]) 
    end=pd.DatetimeIndex([data['time'].units.split('days since')[1]]) + pd.DateOffset(days=int(data['time'][-1]))+ pd.DateOffset(months=1)
    status_daterange = pd.date_range(start=start[0], end=end[0], freq='1M')
    status_daterange=status_daterange.strftime("%Y-%m")
print(f"{len(status_daterange)} months of status data.")
print()

print('making status count files')
print()
# make the status counts files
for idx in range(0,data.variables['spi_OUTLAST'].shape[1]):
    # make a dataframe for each hydrobasin
    status = pd.DataFrame(index=np.arange(0,len(status_daterange)))
    status['date'] = status_daterange
    # do the outlast classes
    # add one to the class so they span 1 - 11
    status['class'] = (data.variables['spi_OUTLAST'][:,idx]+1).filled(np.nan)
    status['class'] = status['class'].astype('Int64')
    status.to_csv(f"{args.outputPath}/counts/status/outlast/{str(data.variables['basin_id'][idx])}_outlast_counts.csv", index=False)
    # do the hydrosos classes
    status['class'] = (data.variables['spi_HydroSOS'][:,idx]+1).filled(np.nan)
    status['class'] = status['class'].astype('Int64')
    status.to_csv(f"{args.outputPath}/counts/status/hydrosos/{str(data.variables['basin_id'][idx])}_hydrosos_counts.csv", index=False)


print('making status geotiff files')
print()

# make the status geotiffs
for i in range(0,data.variables['spi_OUTLAST'].shape[0]):
    status = pd.DataFrame(columns = ['HYBAS_ID','class'])
    status['HYBAS_ID'] = data.variables['basin_id'][:]
    status['HYBAS_ID'] = abs(status['HYBAS_ID'])
    #OUTLAST
    #add one to the classes so they span 1 - 11
    status['class'] = (data.variables['spi_OUTLAST'][i,:]+1).filled(0)
    status['class'] = status['class'].astype(int)
    gdf_join = gdf.merge(status, left_on='HYBAS_ID', right_on='HYBAS_ID')
    #make geocube converts vector data to raster...
    #an 8 bit unsigned integer is enough to store all the data classes
    output_geotiff = f"{args.outputPath}/geotiff/status/outlast/{status_daterange[i]}_outlast.tiff"
    out_grid = make_geocube(
        vector_data=gdf_join,
        measurements=["class"],
        fill=0,
        resolution=(-0.05, 0.05), #if the resolution is greater than 0.05 it falls over as too big a dataset.
        rasterize_function=partial(rasterize_image, all_touched=True, dtype='int8')
    )
    #export the grid to a geotiff for the portal via mapserver (hydrosos_hydrobasins.map)
    out_grid.rio.to_raster(output_geotiff, driver="COG", tiled=True, windowed=True,  dtype=rasterio.uint8)

    #HYDROSOS
    #add one to the classes so they span 1 - 5
    status['class'] = (data.variables['spi_HydroSOS'][i,:]+1).filled(0)
    status['class'] = status['class'].astype(int)
    gdf_join = gdf.merge(status, left_on='HYBAS_ID', right_on='HYBAS_ID')
    #make geocube converts vector data to raster...
    output_geotiff = f"{args.outputPath}/geotiff/status/hydrosos/{status_daterange[i]}_hydrosos.tiff"
    out_grid = make_geocube(
        vector_data=gdf_join,
        measurements=["class"],
        fill=0,
        resolution=(-0.05, 0.05), #if the resolution is greater than 0.05 it falls over as too big a dataset.
        rasterize_function=partial(rasterize_image, all_touched=True, dtype='int8')
    )
    #export the grid to a geotiff for the portal via mapserver (hydrosos_hydrobasins.map)
    out_grid.rio.to_raster(output_geotiff, driver="COG", tiled=True, windowed=True,  dtype=rasterio.uint8)


#process forecast data
fileName = args.forecast_input
data = nc.Dataset(fileName)

if args.forecastStart and args.forecastEnd: 
    print('using custom forecastStart and end')
    forecast_daterange = pd.date_range(start=args.forecastStart,end=args.forecastEnd, freq='1M')
    forecast_daterange=forecast_daterange.strftime("%Y-%m")
else: 
    print('reading forecast daterange from file')
    start=pd.DatetimeIndex([data['time'].units.split('days since')[1]]) 
    end=pd.DatetimeIndex([data['time'].units.split('days since')[1]]) + pd.DateOffset(days=int(data['time'][-1]))+ pd.DateOffset(months=1)
    forecast_daterange = pd.date_range(start=start[0], end=end[0], freq='1M')
    forecast_daterange=forecast_daterange.strftime("%Y-%m")
print(f"{len(forecast_daterange)} months of forecast data.")
print()

print('making forecast count files')
print()
# make the forecast counts files
for idx in range(0,data.variables['spi_OUTLAST_cat0'].shape[1]):
    # make a dataframe for each hydrobasin
    forecast = pd.DataFrame(index=np.arange(0,len(forecast_daterange)))
    forecast['date'] = forecast_daterange
    # do the outlast classes
    # add one to the class so they span 1 - 12 
    for i in range(1,12):
        forecast[f'Cat_{i}'] = (data.variables[f'spi_OUTLAST_cat{i-1}'][:,idx]).filled(np.nan)
        forecast[f'Cat_{i}'] = forecast[f'Cat_{i}'].astype('Int64')
    forecast.to_csv(f"{args.outputPath}/counts/forecast/outlast/{str(data.variables['basin_id'][idx])}_outlast_counts.csv", index=False)

    # do the hydrosos classes
    forecast = pd.DataFrame(index=np.arange(0,len(forecast_daterange)))
    forecast['date'] = forecast_daterange
    # add one to the class so they span 1 - 5
    for i in range(1,6):
        forecast[f'Cat_{i}'] = (data.variables[f'spi_HydroSOS_cat{i-1}'][:,idx]).filled(np.nan)
        forecast[f'Cat_{i}'] = forecast[f'Cat_{i}'].astype('Int64')
    forecast.to_csv(f"{args.outputPath}/counts/forecast/hydrosos/{str(data.variables['basin_id'][idx])}_hydrosos_counts.csv", index=False)

print('making forecast geotiff files')
print()
#make the geotiff files
for i in range(0,data.variables['spi_OUTLAST_cat0'].shape[0]):
    forecast = pd.DataFrame(columns = ['HYBAS_ID','class'])
    forecast['HYBAS_ID'] = data.variables['basin_id'][:]
    forecast['HYBAS_ID'] = abs(forecast['HYBAS_ID'])
    #OUTLAST
    #add one to the classes so they span 1 - 11
    forecast['class'] = (data.variables['spi_OUTLAST_maj'][i,:]+1).filled(0)
    forecast['class'] = forecast['class'].astype('float')
    gdf_join = gdf.merge(forecast, left_on='HYBAS_ID', right_on='HYBAS_ID')
    #make geocube converts vector data to raster...
    #an 8 bit unsigned integer is enough to store all the data classes
    output_geotiff = f"{args.outputPath}/geotiff/forecast/outlast/{forecast_daterange[i]}_outlast.tiff"
    out_grid = make_geocube(
        vector_data=gdf_join,
        measurements=["class"],
        fill=0,
        resolution=(-0.05, 0.05), #if the resolution is greater than 0.05 it falls over as too big a dataset.
        rasterize_function=partial(rasterize_image, all_touched=True, dtype='int8')
    )
    #export the grid to a geotiff for the portal via mapserver (hydrosos_hydrobasins.map)
    out_grid.rio.to_raster(output_geotiff, driver="COG", tiled=True, windowed=True,  dtype=rasterio.uint8)

    #HYDROSOS
    #add one to the classes so they span 1 - 5
    forecast['class'] = (data.variables['spi_HydroSOS_maj'][i,:]+1).filled(0)
    forecast['class'] = forecast['class'].astype(int)
    gdf_join = gdf.merge(forecast, left_on='HYBAS_ID', right_on='HYBAS_ID')
    #make geocube converts vector data to raster...
    output_geotiff = f"{args.outputPath}/geotiff/forecast/hydrosos/{forecast_daterange[i]}_hydrosos.tiff"
    out_grid = make_geocube(
        vector_data=gdf_join,
        measurements=["class"],
        fill=0,
        resolution=(-0.05, 0.05), #if the resolution is greater than 0.05 it falls over as too big a dataset.
        rasterize_function=partial(rasterize_image, all_touched=True, dtype='int8')
    )
    #export the grid to a geotiff for the portal via mapserver (hydrosos_hydrobasins.map)
    out_grid.rio.to_raster(output_geotiff, driver="COG", tiled=True, windowed=True,  dtype=rasterio.uint8)

print('all done')