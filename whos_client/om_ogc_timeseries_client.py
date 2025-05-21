import requests
from typing import List
import logging
from datetime import datetime
import click
import json
from pandas import DataFrame
import sys
import argparse

class OmOgcTimeseriesClient:

    url : str

    token : str

    timeseries_max : int

    timeseries_per_page : int

    view : str

    threshold_begin_date : str

    pagination_limit : int

    default_config : dict = {
        "url": 'https://gs-service-preproduction.geodab.eu/gs-service/services/essi', # 'https://whos.geodab.eu/gs-service/services/essi',
        "token": 'MY_TOKEN',
        "timeseries_max": 48000,
        "timeseries_per_page": 400,
        "view": 'whos-plata',
        "threshold_begin_date": None,
        "pagination_limit": 1000
    }

    def __init__(self, config : dict = None):
        for key, val in self.default_config.items():
            if config is not None and key in config:
               setattr(self, key, config[key])
            else:
               setattr(self, key, val)

    def getTimeseriesWithPagination(
            self,
            **kwargs
    ):
        members = []
        is_last = False
        resumption_token = None
        while not is_last:
            result = self.getTimeseries(**kwargs, resumptionToken=resumption_token)
            if "member" not in result:
                is_last = True
            else:
                members.extend(result["member"])
                if result["completed"]:
                    is_last = True
                else:
                    resumption_token = result["resumptionToken"]
        return {
            "member": members
        }

    def getTimeseries(
            self,
            feature : str = None,
            observationIdentifier : str = None,
            beginPosition : str = None,
            endPosition : str = None,
            limit : int = None,
            offset : int = None,
            useCache : bool = False,
            view : str = None,
            has_data : bool = False,
            profiler : str = "om-api",
            resumptionToken : str = None,
            west : float = None, 
            south : float = None, 
            east : float = None, 
            north : float = None,
            ontology : str = None,
            observedProperty : str = None,
            timeInterpolation : str = None,
            intendedObservationSpacing : str = None,
            aggregationDuration : str = None,
            includeData : bool = None,
            asynchDownload : bool = None,
            format : str = None) -> dict:

        profiler_path =  "timeseries-api/timeseries" if profiler == "timeseries-api" else "om-api/observations"        
        view = view if view is not None else self.view
        limit = limit if limit is not None else self.pagination_limit
        url = "%s/token/%s/view/%s/%s" % (self.url, self.token, view, profiler_path)
        logging.debug("url: %s" % url)
        params = {
                "monitoringPoint": feature,
                "timeseriesIdentifier": observationIdentifier,
                "beginPosition": beginPosition,
                "endPosition": endPosition,
                "limit": limit,
                "offset": offset,
                "useCache": useCache
            } if profiler == "timeseries-api" else {
                "feature": feature,
                "observationIdentifier": observationIdentifier,
                "beginPosition": beginPosition,
                "endPosition": endPosition,
                "east": east,
                "south": south,
                "west": west,
                "north": north,
                "observedProperty": observedProperty,
                "ontology": ontology,
                "timeInterpolation": timeInterpolation,
                "intendedObservationSpacing": intendedObservationSpacing,
                "aggregationDuration": aggregationDuration,
                "includeData": includeData,
                "asynchDownload": asynchDownload,
                "useCache": useCache,
                "limit": limit,
                "useCache": useCache,
                "resumptionToken": resumptionToken,
                "format": format
            } 
        response = requests.get(
            url,
            params)
        if response.status_code != 200:
            raise ValueError("request failed, status code: %s, message: %s" % (response.status_code, response.text))
        result = response.json()
        if has_data and "member" in result:
            result["member"] = self.filterByAvailability(result["member"],self.threshold_begin_date)
        return result

    def filterByAvailability(
            self,
            members : list,
            threshold_begin_date : str = None) -> list:
        if threshold_begin_date is not None:
            return [x for x in members if "phenomenonTime" in x and datetime.fromisoformat(x["phenomenonTime"]["end"]) >=  datetime.fromisoformat(threshold_begin_date)]
        else:
            return [x for x in members if "phenomenonTime" in x]

    def getData(
        self,
        beginPosition : str,
        endPosition : str,
        feature : str = None,
        observedProperty : str = None,
        observationIdentifier : str = None,
        view : str = None,
        timeInterpolation : str = None, # MAX, MIN, TOTAL, AVERAGE, MAX_PREC, MAX_SUCC, CONTINUOUS, ...
        intendedObservationSpacing : str = None, # ISO8601 i.e. P1D
        aggregationDuration : str = None, # ISO8601 i.e. P1D
        ontology : str = None,
        profiler : str = "om-api"
    ) -> List[dict]:        
        if observationIdentifier is None:
            if feature is None:
                raise TypeError("feature can't be None if timeseriesIdentifier is None")
            if observedProperty is None:
                raise TypeError("observedProperty can't be None if timeseriesIdentifier is None")
        view = view if view is not None else self.view
        
        # First, retrieves timeseries metadata for the monitoring point or timeseriesIdentifier
        if observationIdentifier is None:
            ts_metadata = self.getTimeseries(
                view = view, 
                feature = feature,
                observedProperty = observedProperty,
                timeInterpolation = timeInterpolation,
                intendedObservationSpacing = intendedObservationSpacing,
                aggregationDuration = aggregationDuration,
                ontology = ontology,
                profiler = profiler
            )
            if not len(ts_metadata["member"]):
                raise FileNotFoundError("Observations not found for  monitoringPoint: %s, observedProperty: %s" % (feature, observedProperty))
            if profiler == "timeseries-api":
                ts_matches = [x for x in ts_metadata["member"] if x["observedProperty"]["href"] == observedProperty]
                if len(ts_matches):
                    observationIdentifier = ts_matches[0]["id"]
                else:
                    raise FileNotFoundError("timeseries metadata not found for monitoringPoint: %s, observedProperty: %s" % (feature, observedProperty))
            else:
                if len(ts_metadata["member"]) > 1:
                    logging.warning("Matched %i observations, retrieving first match" % len(ts_metadata["member"]))
                observationIdentifier = ts_metadata["member"][0]["id"]
        else: 
            ts_metadata = self.getTimeseries(
                view = view,
                observationIdentifier = observationIdentifier,
                profiler = profiler
            )
            if not len(ts_metadata):
                raise ValueError("observation metadata not found for observationIdentifier: %s" % observationIdentifier)
            
        # Now that we have the timeseries identifier, retrieve data
        ts_data = self.getTimeseries(
            view = view,
            beginPosition = beginPosition,
            endPosition = endPosition,
            observationIdentifier = observationIdentifier,
            includeData = True,
            profiler = profiler
        )
        return [ 
            {
                "date": p["time"]["instant"],
                "value": p["value"]
            }
            for p in ts_data["member"][0]["result"]["points"]
        ]

def parse_first_arg():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "command",
        nargs="?",
        choices=["data", "metadata"],
        default="data",
        help="Command to run. Default is 'data'."
    )
    args, remaining_args = parser.parse_known_args()
    return args.command, remaining_args

@click.group()
def cli():
    pass

@cli.command()
@click.option('-t','--token', default=None, type=str, help='WHOS access token')
@click.option('-u','--url', default=None, type=str, help='WHOS OM OGC timeseries API url')
@click.option('-o','--output', default=None, type=str, help='Save result into this file (instead of print on stdout)')
@click.option('-c','--csv', is_flag=True, default=False, help='Use CSV format for output (instead of JSON)')
@click.option("-m","--monitoring_point",default=None,type=str,help="site identifier. It must be user together with --variable_name")
@click.option("-v","--variable_name",default=None,type=str,help="variable identifier. It must be used together with --monitoring_point")
@click.option("-s","--timeseries_identifier",default=None,type=str,help="timeseries identifier. If set, --monitoring_point and --variable_name are ignored")
@click.argument("begin_position")
@click.argument("end_position")
def data(token, url, output, csv, monitoring_point, variable_name, timeseries_identifier, begin_position, end_position):
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    client = OmOgcTimeseriesClient(config)
    data = client.getData(
        begin_position, 
        end_position,
        feature = monitoring_point, 
        observedProperty = variable_name, 
        observationIdentifier = timeseries_identifier
    )
    if output is not None:
        if csv:
            df = DataFrame(data)
            df.to_csv(open(output, "w"), index=False)
        else:
            json.dump(data, open(output, "w"), ensure_ascii=False)
    else:
        if csv:
            df = DataFrame(data)
            df.to_csv(sys.stdout, index=False)
        else:
            click.echo(json.dumps(data))

@cli.command()
@click.option('-t','--token', default=None, type=str, help='WHOS access token')
@click.option('-u','--url', default=None, type=str, help='WHOS OM OGC timeseries API url')
@click.option('-o','--output', default=None, type=str, help='Save result into this file (instead of print on stdout)')
@click.option("-m","--monitoring_point",default=None,type=str,help="site (feature) identifier. It must be user together with --variable_name")
@click.option("-v","--variable_name",default=None,type=str,help="variable identifier (=observedProperty). It must be used together with --monitoring_point")
@click.option("-s","--timeseries_identifier",default=None,type=str,help="timeseries identifier. If set, --monitoring_point and --variable_name are ignored")
@click.option("-l","--limit",default=None,type=int,help="pagination page size")
@click.option('-h','--has_data', is_flag=True, default=False, help='return only observations with data')
@click.option("-W","--west",default=None,type=float,help="west longitude of bounding box")
@click.option("-S","--south",default=None,type=float,help="south latitude of bounding box")
@click.option("-E","--east",default=None,type=float,help="east longitude of bounding box")
@click.option("-N","--north",default=None,type=float,help="north latitude of bounding box")
@click.option("-O","--ontology",default=None,type=str,help="The ontology to be used to expand the observed property search term (or URI) with additional terms from the ontology that are synonyms and associated to narrower concepts. Two ontologies are available: whos or his-central")
@click.option("-V","--view",default=None,type=str,help="Identifier of the data subset interesting for the user")
@click.option("-T","--time_interpolation",default=None,type=str,help="The interpolation used on the time axis (for example, MAX, MIN, TOTAL, AVERAGE, MAX_PREC, MAX_SUCC, CONTINUOUS, ...)")
@click.option("-i","--intended_observation_spacing",default=None,type=str,help="The expected duration between individual observations, expressed as ISO8601 duration (e.g., P1D)")
@click.option("-a","--aggregation_duration",default=None,type=str,help="Time aggregation that has occurred to the value in the timeseries, expressed as ISO8601 duration (e.g., P1D)")
@click.option("-f","--format",default=None,type=str,help="Response format (e.g. JSON or CSV)")
def metadata(token, url, output, monitoring_point, variable_name, timeseries_identifier, limit, has_data, west, south, east, north, ontology, view, time_interpolation, intended_observation_spacing, aggregation_duration, format):
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    client = OmOgcTimeseriesClient(config)
    data = client.getTimeseriesWithPagination(
        feature = monitoring_point, 
        observedProperty = variable_name, 
        observationIdentifier = timeseries_identifier,
        limit = limit,
        view = view,
        has_data = has_data, 
        west = west, 
        south = south, 
        east = east, 
        north = north, 
        ontology = ontology, 
        timeInterpolation = time_interpolation, 
        intendedObservationSpacing = intended_observation_spacing, 
        aggregationDuration = aggregation_duration, 
        format = format
    )
    if output is not None:
        json.dump(data, open(output, "w"), ensure_ascii=False)
    else:
        click.echo(json.dumps(data, ensure_ascii=False))

if __name__ == '__main__':
    command, remaining = parse_first_arg()
    sys.argv = [sys.argv[0], command] + remaining  # Reset sys.argv for click
    cli()
