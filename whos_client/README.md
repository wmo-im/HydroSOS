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
    pip3 install -r requirements

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

    $ python3 om_ogc_timeseries_client.py --help
    Usage: om_ogc_timeseries_client.py [OPTIONS] BEGIN_POSITION END_POSITION

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

### Credits

Programa de Sistemas de Alerta Hidrológico

Laboratorio de Hidrología

Instituto Nacional del Agua

Argentina

2024-05-22

