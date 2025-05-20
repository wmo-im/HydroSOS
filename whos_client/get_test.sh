# output json to stdout
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge 1990-01-01 2024-05-01
# output to json file
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge 1990-01-01 2024-05-01 -o data.json
# output csv to stdout
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge 1990-01-01 2024-05-01 -c
# output to csv file
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m FAAC49BA633EFF325BE5D2BA81BE14574A268ABA -v Discharge 1990-01-01 2024-05-01 -o data.csv -c
# retrieve using timeseries id instead of site id + variable id
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -s 18EB307E3D1C45D3A2842D710A41001AB5083041 1990-01-01 2024-05-01
