## WHOS data retrieval functionality for HydroSOS

### Purpose

To facilitate interoperable timeseries data retrieval from the WHOS (WMO Hydrological Observations System). 

### How to use

1. Install this module (see Installation)

2. Register into WHOS and save your access token

3. Explore WHOS portals and search engines to select the timeseries of interest

  - https://community.wmo.int/en/whos-portals
  - https://whos.geodab.eu/gs-service/om-api
  - https://alerta.ina.gob.ar/wmlclient/wml/
  - http://whos.geodab.eu/gs-service/search?view=whos-plata


4. Take note of the feature id (site) plus observedProperty, or the observationIdentifier

5. Use either a python script or notebook (see get_test.ipynb) or the command line interface to get the data (see get_test.sh) for a given time period

### Installation

    python3 -m venv .
    source bin/activate
    pip3 install .

### Output

Output format is either:
  - a JSON-serializable list of dicts:

        [
          {
            "date": "ISO format date string",
            "value": float
          },
          ...
        ]

  - or CSV:

        date,value
        string,float
        ...

### Command line interface
data
```text
Usage: om-api-client data [OPTIONS] BEGIN_POSITION END_POSITION

Options:
  -t, --token TEXT                WHOS access token
  -u, --url TEXT                  WHOS OM OGC timeseries API url
  -o, --output TEXT               Save result into this file (instead of print
                                  on stdout)
  -c, --csv                       Use CSV format for output (instead of JSON)
  -m, --monitoring_point TEXT     site identifier. It must be user together
                                  with --variable_name
  -v, --variable_name TEXT        variable identifier. It must be used
                                  together with --monitoring_point
  -s, --timeseries_identifier TEXT
                                  timeseries identifier. If set,
                                  --monitoring_point and --variable_name are
                                  ignored
  --help                          Show this message and exit.
```
metadata
```text
$ om-api-client metadata --help
Usage: om-api-client metadata [OPTIONS]

Options:
  -t, --token TEXT                WHOS access token
  -u, --url TEXT                  WHOS OM OGC timeseries API url
  -o, --output TEXT               Save result into this file (instead of print
                                  on stdout)
  -m, --monitoring_point TEXT     site (feature) identifier. It must be user
                                  together with --variable_name
  -v, --variable_name TEXT        variable identifier (=observedProperty). It
                                  must be used together with
                                  --monitoring_point
  -s, --timeseries_identifier TEXT
                                  timeseries identifier. If set,
                                  --monitoring_point and --variable_name are
                                  ignored
  -l, --limit INTEGER             pagination page size
  -h, --has_data                  return only observations with data
  -W, --west FLOAT                west longitude of bounding box
  -S, --south FLOAT               south latitude of bounding box
  -E, --east FLOAT                east longitude of bounding box
  -N, --north FLOAT               north latitude of bounding box
  -O, --ontology TEXT             The ontology to be used to expand the
                                  observed property search term (or URI) with
                                  additional terms from the ontology that are
                                  synonyms and associated to narrower
                                  concepts. Two ontologies are available: whos
                                  or his-central
  -V, --view TEXT                 Identifier of the data subset interesting
                                  for the user
  -T, --time_interpolation TEXT   The interpolation used on the time axis (for
                                  example, MAX, MIN, TOTAL, AVERAGE, MAX_PREC,
                                  MAX_SUCC, CONTINUOUS, ...)
  -i, --intended_observation_spacing TEXT
                                  The expected duration between individual
                                  observations, expressed as ISO8601 duration
                                  (e.g., P1D)
  -a, --aggregation_duration TEXT
                                  Time aggregation that has occurred to the
                                  value in the timeseries, expressed as
                                  ISO8601 duration (e.g., P1D)
  -f, --format TEXT               Response format (e.g. JSON or CSV)
  --help                          Show this message and exit.
```
features
```text
$ om-api-client features --help
Usage: om-api-client features [OPTIONS]

Options:
  -t, --token TEXT                WHOS access token
  -u, --url TEXT                  WHOS OM OGC timeseries API url
  -o, --output TEXT               Save result into this file (instead of print
                                  on stdout)
  -m, --monitoring_point TEXT     site (feature) identifier. It must be user
                                  together with --variable_name
  -v, --variable_name TEXT        variable identifier (=observedProperty). It
                                  must be used together with
                                  --monitoring_point
  -s, --timeseries_identifier TEXT
                                  timeseries identifier. If set,
                                  --monitoring_point and --variable_name are
                                  ignored
  -l, --limit INTEGER             pagination page size
  -W, --west FLOAT                west longitude of bounding box
  -S, --south FLOAT               south latitude of bounding box
  -E, --east FLOAT                east longitude of bounding box
  -N, --north FLOAT               north latitude of bounding box
  -O, --ontology TEXT             The ontology to be used to expand the
                                  observed property search term (or URI) with
                                  additional terms from the ontology that are
                                  synonyms and associated to narrower
                                  concepts. Two ontologies are available: whos
                                  or his-central
  -V, --view TEXT                 Identifier of the data subset interesting
                                  for the user
  -T, --time_interpolation TEXT   The interpolation used on the time axis (for
                                  example, MAX, MIN, TOTAL, AVERAGE, MAX_PREC,
                                  MAX_SUCC, CONTINUOUS, ...)
  -i, --intended_observation_spacing TEXT
                                  The expected duration between individual
                                  observations, expressed as ISO8601 duration
                                  (e.g., P1D)
  -a, --aggregation_duration TEXT
                                  Time aggregation that has occurred to the
                                  value in the timeseries, expressed as
                                  ISO8601 duration (e.g., P1D)
  -f, --format TEXT               Response format (e.g. JSON (raw), GeoJSON or
                                  CSV)
  --help                          Show this message and exit.
```
### Credits

Programa de Sistemas de Información y Alerta Hidrológico de la Cuenca del Plata

Laboratorio de Hidrología

Instituto Nacional del Agua

Argentina

2025-07-15

