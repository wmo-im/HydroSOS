# retrieve data using feature id + variable id + aggregation duration (-m + -v + -a)
# output json to stdout
om-api-client data -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge -a P1M 1990-01-01 2024-05-01 
# output to json file
om-api-client data -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge -a P1M -o /tmp/data.json 1990-01-01 2024-05-01 
# output csv to stdout
om-api-client data -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge -a P1M -c 1990-01-01 2024-05-01 
# output to csv file
om-api-client data -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge -a P1M -o /tmp/data.csv -c 1990-01-01 2024-05-01
# retrieve using timeseries observation id (-s)
om-api-client data -s 18EB307E3D1C45D3A2842D710A41001AB5083041 1990-01-01 2024-05-01
# retrieve metadata
om-api-client metadata -l 50 -v Discharge -o /tmp/whos_metadata.json
# retrieve features
om-api-client features -l 50 -v Discharge -o /tmp/whos_features.json
# retrieve features as csv
om-api-client features -l 50 -v Discharge -o /tmp/whos_features.csv -f csv
# retrieve features as geojson
om-api-client features -l 50 -v Discharge -o /tmp/whos_features.geojson -f geojson