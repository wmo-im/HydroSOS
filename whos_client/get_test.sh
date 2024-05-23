# output json to stdout
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m F426CC5C7D4A1563EE3B41E4F50FB4DE8568D3F2 -v B9240615C51DA438E9E02C9858887F1EE726EE2E 1990-01-01 2024-05-01
# output to json file
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m F426CC5C7D4A1563EE3B41E4F50FB4DE8568D3F2 -v B9240615C51DA438E9E02C9858887F1EE726EE2E 1990-01-01 2024-05-01 -o data.json
# output csv to stdout
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m F426CC5C7D4A1563EE3B41E4F50FB4DE8568D3F2 -v B9240615C51DA438E9E02C9858887F1EE726EE2E 1990-01-01 2024-05-01 -c
# output to csv file
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -m F426CC5C7D4A1563EE3B41E4F50FB4DE8568D3F2 -v B9240615C51DA438E9E02C9858887F1EE726EE2E 1990-01-01 2024-05-01 -o data.csv -c
# retrieve using timeseries id instead of site id + variable id
python3 om_ogc_timeseries_client.py -t whos-36e7d1a3-b61e-4ae0-aca4-60efe6f27361 -s F52452C81C0F06F1CAF659481D06817E9873AC91 1990-01-01 2024-05-01
