import requests 
import zipfile
import geopandas 
from io import BytesIO  
import argparse
import pandas 

parser = argparse.ArgumentParser(
                    prog='merge_hydrobasins',
                    description='Merges Hydrosheds level 4 hydrobasins into a single file.',
                    epilog='Ezra K, UKCEH10092024')

parser.add_argument("directoryPath", help="location to write/read hydrosheds shapefiles to")
parser.add_argument('--download', help="whether the data first needs to be downloaded, set to 1 if so")

args = parser.parse_args()

shapefileURLs = {"Africa":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_af_lev04_v1c.zip",
                 "Arctic":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_ar_lev04_v1c.zip",
                 "Asia":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_as_lev04_v1c.zip",
                 "Australasia":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_au_lev04_v1c.zip",
                 "Europe and the Middle East":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_eu_lev04_v1c.zip",
                 "Greenland":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_gr_lev04_v1c.zip",
                 "North and Central America":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_na_lev04_v1c.zip",
                 "South America":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_sa_lev04_v1c.zip",
                 "Siberia":"https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_si_lev04_v1c.zip"}

shapefileNames = {"Africa":"hybas_af_lev04_v1c.shp",
                 "Arctic":"hybas_ar_lev04_v1c.shp",
                 "Asia":"hybas_as_lev04_v1c.shp",
                 "Australasia":"hybas_au_lev04_v1c.shp",
                 "Europe and the Middle East":"hybas_eu_lev04_v1c.shp",
                 "Greenland":"hybas_gr_lev04_v1c.shp",
                 "North and Central America":"hybas_na_lev04_v1c.shp",
                 "South America":"hybas_sa_lev04_v1c.shp",
                 "Siberia":"hybas_si_lev04_v1c.shp"}


data = dict(keys=shapefileURLs.keys())

if args.download=="1":
    for key, value in zip(shapefileURLs.keys(),shapefileURLs.values()):
        print(f"Requesting {key} data.")
        r = requests.get(value, stream=True)
        print(f"Extracting {key} data.")
        z = zipfile.ZipFile(BytesIO(r.content))
        z.extractall(args.directoryPath)
    print("Download complete")
    print("")

mergedData = geopandas.GeoDataFrame()
for key, value in zip(shapefileNames.keys(),shapefileNames.values()):
    print(f"Merging {key} shapefile")
    mergedData = pandas.concat([mergedData,geopandas.read_file(f"{args.directoryPath}/{value}")])
    
mergedData.to_file(f"{args.directoryPath}/merged_hydrobasins_level04.shp")
print(f"merged shapefile written to {args.directoryPath}/merged_hydrobasins_level04.shp")