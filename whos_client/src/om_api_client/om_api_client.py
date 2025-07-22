import requests
from typing import List, Callable, Literal, Union, Any, Sequence
import logging
from datetime import datetime, timedelta
import click
import json
from pandas import DataFrame, read_csv, to_datetime, concat
import sys
import argparse
import os
from pathlib import Path
import yaml
from typing import List, TypedDict

class PointGeometry(TypedDict):
    type : Literal["Point"]
    coordinates : List[float]

class OMFeatureParameter(TypedDict):
    name : str
    value : str

class OMRelatedParty(TypedDict):
    organisationName : str
    role : str
    URL : str

class OMFeature(TypedDict):
    shape : PointGeometry
    parameter : List[OMFeatureParameter]
    name : str
    id : str
    relatedParty : List[OMRelatedParty]

class OMFeaturesResult(TypedDict):
    results: List[OMFeature]

class PointFeature(TypedDict):
    geometry : PointGeometry
    properties : dict

class GeoJSONPointsCollection(TypedDict):
    type : Literal["FeatureCollection"]
    features : List[PointFeature]

class OMObservedProperty(TypedDict):
    href : str
    title : str

class OMPhenomenonTime(TypedDict):
    end : str
    begin : str

class OMFeatureOfInterest(TypedDict):
    href : str

class OMInterpolationType(TypedDict):
    href : str
    title : str

class OMObservationDefaultPointMetadata(TypedDict, total=False):
    uom : str
    aggregationDuration : str
    interpolationType : OMInterpolationType

class OMObservationResult(TypedDict):
    metadata : dict
    defaultPointMetadata : OMObservationDefaultPointMetadata

class OMTime(TypedDict):
    instant : str 

class OMObservationPoint(TypedDict):
    shape : PointGeometry
    time : OMTime
    value : Union[int, float]

class OMObservation(TypedDict):
    parameter : List[OMFeatureParameter]
    observedProperty : OMObservedProperty
    phenomenonTime : OMPhenomenonTime
    featureOfInterest : OMFeatureOfInterest
    id : str
    type : Literal["TimeSeriesObservation"]
    result : OMObservationResult
    points : List[OMObservationPoint]

class OMObservationCollection(TypedDict):
  id : Literal["observation collection"]
  member : List[OMObservation]

class OmApiClientConfig(TypedDict):
    url : str
    token : str
    view : str
    threshold_begin_date : Union[str, None]
    page_size : int

class OMResultPoint(TypedDict):
    date : str
    value : float

class OmApiClient:

    url : str

    token : str

    timeseries_max : int

    timeseries_per_page : int

    view : str

    threshold_begin_date : str

    page_size : int

    last_url : str

    last_params : dict

    default_config : OmApiClientConfig = {
        "url": 'https://gs-service-preproduction.geodab.eu/gs-service/services/essi', # 'https://whos.geodab.eu/gs-service/services/essi',
        "token": 'MY_TOKEN',
        "view": 'whos-plata',
        "threshold_begin_date": None,
        "page_size": 1000
    }

    config_path = os.path.join(Path.home(),".om-api-client.yml")

    def write_config(self, file_path : str = config_path, overwrite : bool = False, raise_if_exists : bool = False):
        if os.path.exists(file_path) and overwrite is False:
            if raise_if_exists:
                raise ValueError("Config file already exists")
        else:
            yaml.dump(self.default_config, open(file_path,"w"), default_flow_style=False)
            print("Default config file created: %s" % file_path)        

    def read_config(self, file_path : str = config_path) -> OmApiClientConfig:
        if not os.path.exists(file_path):
            try:
                self.write_config(file_path)
            except FileNotFoundError as e:
                print(str(e))
                raise FileNotFoundError("File not found and can't be created: %s" % file_path)
        config = yaml.load(open(file_path, "r"),Loader=yaml.CLoader)
        return config

    def __init__(self, config : Union[OmApiClientConfig,None] = None):
        saved_config = self.read_config()
        for key, val in self.default_config.items():
            if config is not None and key in config:
                setattr(self, key, config[key])
            elif key in saved_config:
                setattr(self, key, saved_config[key])
            else:
                setattr(self, key, val)

    def getFeatures(
            self,
            feature : Union[str,None] = None,
            observationIdentifier : Union[str,None] = None,
            beginPosition : Union[str,None] = None,
            endPosition : Union[str,None] = None,
            west : Union[float,None] = None, 
            south : Union[float,None] = None, 
            east : Union[float,None] = None, 
            north : Union[float,None] = None,
            spatialRelation : Union[str,None] = None,
            predefinedLayer : Union[str,None] = None,
            observedProperty : Union[str,None] = None,
            ontology : Union[str,None] = None,
            timeInterpolation : Union[str,None] = None,
            intendedObservationSpacing : Union[str,None] = None,
            aggregationDuration : Union[str,None] = None,
            country : Union[str,None] = None,
            provider : Union[str,None] = None,
            resumptionToken : Union[str,None] = None,
            limit : Union[int,None] = None,
            offset : Union[int,None] = None,
            view : Union[str,None] = None,
            profiler : str = "om-api") -> dict:

        profiler_path =  "timeseries-api/monitoring-points" if profiler == "timeseries-api" else "om-api/features"        
        view = view if view is not None else self.view
        limit = limit if limit is not None else self.page_size
        url = "%s/token/%s/view/%s/%s" % (self.url, self.token, view, profiler_path)
        logging.debug("url: %s" % url)
        params = {
                "east": east,
                "south": south,
                "west": west,
                "north": north,
                "country": country,
                "provider": provider,
                "offset": offset,
                "limit": limit
            } if profiler == "timeseries-api" else {
                "feature": feature,
                "observationIdentifier": observationIdentifier,
                "beginPosition": beginPosition,
                "endPosition": endPosition,
                "west": west,
                "south": south,
                "east": east,
                "north": north,
                "spatialRelation": spatialRelation,
                "predefinedLayer": predefinedLayer,
                "observedProperty": observedProperty,
                "ontology": ontology,
                "timeInterpolation": timeInterpolation,
                "intendedObservationSpacing": intendedObservationSpacing,
                "aggregationDuration": aggregationDuration,
                "country": country,
                "provider": provider,
                "resumptionToken": resumptionToken,
                "limit": limit
            } 
        response = requests.get(
            url,
            params)
        if response.status_code != 200:
            raise ValueError("request failed, status code: %s, message: %s" % (response.status_code, response.text))
        result = response.json()
        return result

    def getWithPagination(
            self,
            method : Callable,
            result_list_property : str,
            **kwargs
    ):
        results = []
        is_last = False
        resumption_token = None
        while not is_last:
            kwargs_ = {**kwargs, "resumptionToken": resumption_token}
            result = method(**kwargs_)
            if result_list_property not in result:
                is_last = True
            else:
                results.extend(result[result_list_property])
                if result["completed"]:
                    is_last = True
                else:
                    resumption_token = result["resumptionToken"]
        return {
            result_list_property: results
        }

    def getFeaturesWithPagination(
            self,
            **kwargs
    ):
        return self.getWithPagination(
            self.getFeatures, 
            "results",
            **kwargs
        )

    def getTimeseriesWithPagination(
            self,
            **kwargs
    ):
        return self.getWithPagination(
            self.getTimeseries, 
            "member",
            **kwargs
        )

    # def getTimeseriesWithPagination(
    #         self,
    #         **kwargs
    # ):
    #     members = []
    #     is_last = False
    #     resumption_token = None
    #     while not is_last:
    #         result = self.getTimeseries(**kwargs, resumptionToken=resumption_token)
    #         if "member" not in result:
    #             is_last = True
    #         else:
    #             members.extend(result["member"])
    #             if result["completed"]:
    #                 is_last = True
    #             else:
    #                 resumption_token = result["resumptionToken"]
    #     return {
    #         "member": members
    #     }

    def getTimeseries(
            self,
            feature : Union[str,None] = None,
            observationIdentifier : Union[str,None] = None,
            beginPosition : Union[str,None] = None,
            endPosition : Union[str,None] = None,
            limit : Union[int,None] = None,
            offset : Union[int,None] = None,
            useCache : bool = False,
            view : Union[str,None] = None,
            has_data : bool = False,
            profiler : str = "om-api",
            resumptionToken : Union[str,None] = None,
            west : Union[float,None] = None, 
            south : Union[float,None] = None, 
            east : Union[float,None] = None, 
            north : Union[float,None] = None,
            ontology : Union[str,None] = None,
            observedProperty : Union[str,None] = None,
            timeInterpolation : Union[str,None] = None,
            intendedObservationSpacing : Union[str,None] = None,
            country: Union[str,None] = None,
            provider: Union[str,None] = None,
            aggregationDuration : Union[str,None] = None,
            includeData : Union[bool,None] = None,
            asynchDownload : Union[bool,None] = None,
            format : Union[str,None] = None) -> dict:

        profiler_path =  "timeseries-api/timeseries" if profiler == "timeseries-api" else "om-api/observations"        
        view = view if view is not None else self.view
        limit = limit if limit is not None else self.page_size
        url = "%s/token/%s/view/%s/%s" % (self.url, self.token, view, profiler_path)
        logging.debug("url: %s" % url)
        self.last_url = url
        params : dict[str, Any] 
        if profiler == "timeseries-api":
            params = {
                "monitoringPoint": feature,
                "timeseriesIdentifier": observationIdentifier,
                "beginPosition": beginPosition,
                "endPosition": endPosition,
                "limit": limit,
                "offset": offset,
                "useCache": useCache
            }
        else:
            params = {
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
                "country": country,
                "provider": provider,
                "includeData": includeData,
                "asynchDownload": asynchDownload,
                "useCache": useCache,
                "limit": limit,
                "useCache": useCache,
                "resumptionToken": resumptionToken,
                "format": format
            } 
        self.last_params = params
        response = requests.get(
            url,
            params)
        if response.status_code != 200:
            raise ValueError("request failed, status code: %s, message: %s" % (response.status_code, response.text))
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logging.error("JSONDecodeError. Invalid response: %s" % response.text)
            raise e
        if has_data and "member" in result:
            result["member"] = self.filterByAvailability(result["member"],self.threshold_begin_date)
        return result

    def filterByAvailability(
            self,
            members : list,
            threshold_begin_date : Union[str,None] = None) -> list:
        if threshold_begin_date is not None:
            return [x for x in members if "phenomenonTime" in x and datetime.fromisoformat(x["phenomenonTime"]["end"]) >=  datetime.fromisoformat(threshold_begin_date)]
        else:
            return [x for x in members if "phenomenonTime" in x]
        
    def getDataBatch(
        self,
        beginPosition : str,
        endPosition : str,
        observationIdentifiers : Union[DataFrame, str] = None,
        output_directory : str = None,
        id_column : str = "ObservationId",
        format : str = "json",
        recursive : bool = False,
        featureIdentifiers : Union[DataFrame, str] = None,
        **kwargs
        ) -> Union[DataFrame, None]:
        """Retrieves data for each of the provided observation or feature identifiers. If output_directory is not set, returns DataFrame with the columns "date", "value" and "observationId"
        
        Args:
            beginPosition (str): Begin of time period
            endPosition (str): End of time period
            observationIdentifiers (Union[DataFrame, str], optional): DataFrame where one column has the identifiers. If str, path to .csv file. If not set, featureIdentifiers must be set
            output_directory (str, optional): If set, path where to save each timeseries as a separate file
            id_column (str, default="ObservationId"): Name of the column of observationIdentifiers that contains the observation identifiers
            format (str, default="json"): Desired output format: options: json (default), csv (works with output_directory)
            recursive (bool, default=False): If True, download data recursively until endPosition is reached,
            featureIdentifiers (Union[DataFrame, str], optional): DataFrame where one column has the identifiers. If str, path to .csv file. If not set, observationIdentifiers must be set
            **kwargs: Additional keyword arguments to pass to the retrieve method
        """

        retrieve_method = self.getDataRecursively if recursive else self.getData
        identifiers : DataFrame
        use_feature_id = False
        if observationIdentifiers is not None:
            if type(observationIdentifiers) == str:
                if not os.path.exists(observationIdentifiers):
                    raise ValueError("observationIdentifiers file not found")
                identifiers = read_csv(open(observationIdentifiers,"r", encoding="utf-8"))
        elif featureIdentifiers is not None:
            use_feature_id = True
            if type(featureIdentifiers) == str:
                if not os.path.exists(featureIdentifiers):
                    raise ValueError("featureIdentifiers file not found")
                identifiers = read_csv(open(featureIdentifiers,"r", encoding="utf-8"))
        else:
            raise ValueError("Either observationIdentifiers or featureIdentifiers must be set")
        if id_column not in identifiers:
            raise ValueError("Column %s missing in %s data frame" % ("featureIdentifiers" if use_feature_id else "observationIdentifiers",id_column))
        df_list : List[DataFrame] = []
        for identifier in identifiers[id_column]:
            args = {
                **kwargs
            }
            if use_feature_id:
                args["feature"] = identifier
                id_column_name = "feature"
            else:
                args["observationIdentifier"] = identifier
                id_column_name = "ObservationId"
            data = retrieve_method(
                beginPosition = beginPosition,
                endPosition = endPosition,
                **args
            )
            if output_directory is not None:
                if not os.path.isdir(output_directory):
                    raise ValueError("%s is not a directory" % output_directory)
                if format.lower() == "csv":
                    df = DataFrame(data)
                    output = os.path.join(output_directory, "%s.csv" % identifier)
                    df.to_csv(open(output, "w"), index=False)
                else:
                    output = os.path.join(output_directory, "%s.json" % identifier)
                    json.dump(data, open(output, "w"), ensure_ascii=False)
            else:
                df = DataFrame(data)
                df[id_column_name] = identifier
                df_list.append(df)
        if output_directory is None:
            return concat(df_list)

    def getDataRecursively(
        self,
        beginPosition : str,
        endPosition : str,
        **kwargs
    ) -> List[OMResultPoint]:
        # parse beginPosition endPosition
        begin_datetime = to_datetime(beginPosition, utc=True)
        end_datetime = to_datetime(endPosition, utc=True)
        results : List[OMResultPoint] = []
        while begin_datetime < end_datetime:
            try:
                data = self.getData(beginPosition=begin_datetime.isoformat(),endPosition=endPosition, **kwargs)
            except ValueError as e:
                logging.error("Data retrieval failed. url: %s, params: %s" % (self.last_url, json.dumps(self.last_params)))
                break
            if not len(data):
                break
            results.extend(data)
            # find last date
            df = DataFrame(data)
            begin_datetime = to_datetime(df["date"], utc=True).max() + timedelta(seconds=1)
        return results

    def getData(
        self,
        beginPosition : str,
        endPosition : str,
        feature : Union[str,None] = None,
        observedProperty : Union[str,None] = None,
        observationIdentifier : Union[str,None] = None,
        view : Union[str,None] = None,
        timeInterpolation : Union[str,None] = None, # MAX, MIN, TOTAL, AVERAGE, MAX_PREC, MAX_SUCC, CONTINUOUS, ...
        intendedObservationSpacing : Union[str,None] = None, # ISO8601 i.e. P1D
        aggregationDuration : Union[str,None] = None, # ISO8601 i.e. P1D
        ontology : Union[str,None] = None,
        profiler : str = "om-api"
    ) -> List[OMResultPoint]:        
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
                profiler = profiler,
                limit = 1
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
        if not len(ts_data["member"]):
            raise ValueError("Couldn't find data for the specified timeseries observation and time period")
        return [ 
            {
                "date": p["time"]["instant"],
                "value": p["value"]
            }
            for p in ts_data["member"][0]["result"]["points"]
        ]

def flattenTimeseriesMetadata(md : dict):
    sourceId = None
    for p in md["parameter"]:
        if p["name"] == "sourceId":
            sourceId = p["value"]
    uom = None
    interpolationType = None
    aggregationDuration = None
    if "defaultPointMetadata" in md["result"]:
        if "uom" in md["result"]["defaultPointMetadata"]:
            uom = md["result"]["defaultPointMetadata"]["uom"]
        if "interpolationType" in md["result"]["defaultPointMetadata"]:
            interpolationType = md["result"]["defaultPointMetadata"]["interpolationType"]["title"]
        if "aggregationDuration" in md["result"]["defaultPointMetadata"]:
            aggregationDuration = md["result"]["defaultPointMetadata"]["aggregationDuration"]

    return {
        "sourceId": sourceId,
        "observedProperty": md["observedProperty"]["title"],
        "beginDate": md["phenomenonTime"]["begin"],
        "endDate": md["phenomenonTime"]["end"],
        "featureId": md["featureOfInterest"]["href"],
        "ObservationId": md["id"],
        "uom": uom,
        "interpolationType": interpolationType,
        "aggregationDuration": aggregationDuration
    }

def flattenFeature(feature : OMFeature):
    country = None
    sourceId = None
    identifier = None
    for p in feature["parameter"]:
        if p["name"] == "country":
            country = p["value"]
        elif p["name"] == "sourceId":
            sourceId = p["value"]
        elif p["name"] == "identifier":
            identifier = p["value"]
    author = None
    for r in feature["relatedParty"]:
        if r["role"] == "author":
            author = r["organisationName"]
    return {
        "longitude": feature["shape"]["coordinates"][0],
        "latitude": feature["shape"]["coordinates"][1],
        "country": country,
        "sourceId": sourceId,
        "identifier": identifier,
        "name": feature["name"],
        "id": feature["id"],
        "author": author
    }

def resultsToDataFrame(
    flatten_function : Callable, 
    # results_list_property : Literal["member", "results"], 
    results : Sequence[Union[OMObservation | OMFeature]]
    ) -> DataFrame:
    return DataFrame([flatten_function(item) for item in results])

def timeseriesMetadataToDataFrame(ts_metadata : dict) -> DataFrame:
    return resultsToDataFrame(flattenTimeseriesMetadata, ts_metadata["member"])

def featuresToDataFrame(features_result : OMFeaturesResult) -> DataFrame:
    return resultsToDataFrame(flattenFeature, features_result["results"])

def featureToGeoJSON(feature : OMFeature) -> PointFeature: 
    return {
        "geometry": feature["shape"],
        "properties": flattenFeature(feature)
    }

def featuresToGeoJSON(features_result : OMFeaturesResult) -> GeoJSONPointsCollection:
    return {
        "type": "FeatureCollection",
        "features": [featureToGeoJSON(feature) for feature in features_result["results"]]
    }
# def timeseriesMetadataToDataFrame(ts_metadata : dict) -> DataFrame:
#     return DataFrame([flattenTimeseriesMetadata(md) for md in ts_metadata["member"]])

OBSERVATION_VALID_FILTERS = {
    "country": str,
    "provider": str
}

FEATURE_VALID_FILTERS = {
    "beginPosition": str,
    "endPosition": str,
    "spatialRelation": str,
    "predefinedLayer": str,
    "country": str,
    "provider": str
}

class KeyValueType(click.ParamType):
    name = "key=value"

    valid_filters : dict

    def __init__(self, valid_filters):
        super().__init__()
        self.valid_filters = valid_filters

    def convert(self, value, param, ctx):
        if "=" not in value:
            self.fail(f"Invalid format: '{value}'. Use key=value.", param, ctx)

        key, val = value.split("=", 1)

        if key not in self.valid_filters:
            self.fail(f"Invalid key: '{key}'. Allowed keys: {', '.join(self.valid_filters)}", param, ctx)

        try:
            casted = self.valid_filters[key](val)
        except Exception as e:
            self.fail(f"Failed to convert value for key '{key}': {e}", param, ctx)

        return key, casted

observation_filter_value_type = KeyValueType(OBSERVATION_VALID_FILTERS)
feature_filter_value_type = KeyValueType(FEATURE_VALID_FILTERS)


def parse_first_arg():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "command",
        nargs="?",
        choices=["data", "batch", "metadata", "features","init"],
        default="data",
        help="Command to run. Default is 'data'."
    )
    args, remaining_args = parser.parse_known_args()
    return args.command, remaining_args

@click.group()
def cli():
    pass

@cli.command(help="Retrieve timeseries data sequentially for all identifiers found in provided csv file\n\nBEGIN_POSITION: Begin date YYYY-MM-DD\n\nEND_POSITION: End date YYYY-MM-DD\n\nIDENTIFIERS: csv file containing timeseries identifiers (or feature identifiers if -f option is set)\n\nOUTPUT: Save results into this directory")
@click.option('-t','--token', default=None, type=str, help='WHOS access token')
@click.option('-u','--url', default=None, type=str, help='WHOS OM OGC timeseries API url')
@click.option('-c','--csv', is_flag=True, default=False, help='Use CSV format for output (instead of JSON)')
@click.option('-I','--id_column', default="ObservationId", type=str, help='Column of timeseries_identifiers containing the ids')
@click.option('-d','--debug', is_flag=True, help='Log debug messages')
@click.option('-r','--recursive', is_flag=True, help='Get data recursively until endPosition is reached. The API has a is a limit of 5000 records per request')
@click.option('-f','--use_feature_id', is_flag=True, help='Retrieve data using feature ids instead of timeseries observation ids. Only first observation match for each feature will be retrieved.')
@click.option("-v","--variable_name",default=None,type=str,help="variable identifier. Effective only when used together with -f, --use_feature_id")
@click.option("-a","--aggregation_duration",default=None,type=str,help="Time aggregation that has occurred to the value in the timeseries, expressed as ISO8601 duration (e.g., P1D). Effective only when used together with -f, --use_feature_id")
@click.option("-O","--ontology",default=None,type=str,help="The ontology to be used to expand the observed property search term (or URI) with additional terms from the ontology that are synonyms and associated to narrower concepts. Two ontologies are available: whos or his-central. Effective only when used together with -f, --use_feature_id")
@click.option("-T","--time_interpolation",default=None,type=str,help="The interpolation used on the time axis (for example, MAX, MIN, TOTAL, AVERAGE, MAX_PREC, MAX_SUCC, CONTINUOUS, ...). Effective only when used together with -f, --use_feature_id")
@click.option("-i","--intended_observation_spacing",default=None,type=str,help="The expected duration between individual observations, expressed as ISO8601 duration (e.g., P1D). Effective only when used together with -f, --use_feature_id")
@click.argument("begin_position", type=str)
@click.argument("end_position", type=str)
@click.argument("identifiers", type=str)
@click.argument("output", type=str)
def batch(token, url, csv, id_column, begin_position, end_position,  identifiers, output, debug, recursive, use_feature_id, variable_name, aggregation_duration, ontology, time_interpolation, intended_observation_spacing):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    client = OmApiClient(config)
    args = {
        "output_directory": output,
        "id_column": id_column,
        "format": "csv" if csv else "json",
        "recursive": recursive,
        "observedProperty": variable_name, 
        "aggregationDuration": aggregation_duration,
        "ontology": ontology, 
        "timeInterpolation": time_interpolation, 
        "intendedObservationSpacing": intended_observation_spacing
    }
    if use_feature_id:
        args["featureIdentifiers"] = identifiers
    else:
        args["observationIdentifiers"] = identifiers
    client.getDataBatch(
        beginPosition=begin_position,
        endPosition=end_position,        
        **args
    )
    
@cli.command()
@click.option('-t','--token', default=None, type=str, help='WHOS access token')
@click.option('-u','--url', default=None, type=str, help='WHOS OM OGC timeseries API url')
@click.option('-o','--output', default=None, type=str, help='Save result into this file (instead of print on stdout)')
@click.option('-c','--csv', is_flag=True, default=False, help='Use CSV format for output (instead of JSON)')
@click.option("-m","--monitoring_point",default=None,type=str,help="site identifier. It must be user together with --variable_name")
@click.option("-v","--variable_name",default=None,type=str,help="variable identifier. It must be used together with --monitoring_point")
@click.option("-s","--timeseries_identifier",default=None,type=str,help="timeseries identifier. If set, --monitoring_point and --variable_name are ignored")
@click.option("-a","--aggregation_duration",default=None,type=str,help="Time aggregation that has occurred to the value in the timeseries, expressed as ISO8601 duration (e.g., P1D)")
@click.option('-d','--debug', is_flag=True, help='Log debug messages')
@click.option('-r','--recursive', is_flag=True, help='Get data recursively until endPosition is reached. The API has a is a limit of 5000 records per request')
@click.argument("begin_position")
@click.argument("end_position")
def data(token, url, output, csv, monitoring_point, variable_name, timeseries_identifier, aggregation_duration, begin_position, end_position, debug, recursive):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    client = OmApiClient(config)
    retrieve_method = client.getDataRecursively if recursive else client.getData
    data = retrieve_method(
        begin_position, 
        end_position,
        feature = monitoring_point, 
        observedProperty = variable_name, 
        observationIdentifier = timeseries_identifier,
        aggregationDuration=aggregation_duration
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
@click.option("-F","--filter", type=observation_filter_value_type, multiple=True, help="Set additional filters as key=value. Valid keys: %s" % ", ".join(OBSERVATION_VALID_FILTERS.keys()))
@click.option("-1", "--first_page_only",is_flag=True,help="Retrieve only first page.")
@click.option("-r", "--resumption_token", type=str, default=None, help="Retrieve next page using the provided resumption token")
@click.option('-d','--debug', is_flag=True, help='Log debug messages')
def metadata(token, url, output, monitoring_point, variable_name, timeseries_identifier, limit, has_data, west, south, east, north, ontology, view, time_interpolation, intended_observation_spacing, aggregation_duration, filter, format, first_page_only, resumption_token, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    parsed_filter = {k: v for k, v in filter} if filter is not None else None
    client = OmApiClient(config)
    retrieve_method = client.getTimeseries if first_page_only or resumption_token is not None else client.getTimeseriesWithPagination
    data = retrieve_method(
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
        resumptionToken = resumption_token,
        **parsed_filter
    )
    if output is not None:
        if format is not None and format == "csv":
            df = timeseriesMetadataToDataFrame(data)
            df.to_csv(open(output, "w"), index=False)
        else:
            json.dump(data, open(output, "w"), ensure_ascii=False)
    else:
        if format is not None and format == "csv":
            df = timeseriesMetadataToDataFrame(data)
            click.echo(df.to_csv(index=False))
        else:
            click.echo(json.dumps(data, ensure_ascii=False))

@cli.command()
@click.option('-t','--token', default=None, type=str, help='WHOS access token')
@click.option('-u','--url', default=None, type=str, help='WHOS OM OGC timeseries API url')
@click.option('-o','--output', default=None, type=str, help='Save result into this file (instead of print on stdout)')
@click.option("-m","--monitoring_point",default=None,type=str,help="site (feature) identifier. It must be user together with --variable_name")
@click.option("-v","--variable_name",default=None,type=str,help="variable identifier (=observedProperty). It must be used together with --monitoring_point")
@click.option("-s","--timeseries_identifier",default=None,type=str,help="timeseries identifier. If set, --monitoring_point and --variable_name are ignored")
@click.option("-l","--limit",default=None,type=int,help="pagination page size")
@click.option("-W","--west",default=None,type=float,help="west longitude of bounding box")
@click.option("-S","--south",default=None,type=float,help="south latitude of bounding box")
@click.option("-E","--east",default=None,type=float,help="east longitude of bounding box")
@click.option("-N","--north",default=None,type=float,help="north latitude of bounding box")
@click.option("-O","--ontology",default=None,type=str,help="The ontology to be used to expand the observed property search term (or URI) with additional terms from the ontology that are synonyms and associated to narrower concepts. Two ontologies are available: whos or his-central")
@click.option("-V","--view",default=None,type=str,help="Identifier of the data subset interesting for the user")
@click.option("-T","--time_interpolation",default=None,type=str,help="The interpolation used on the time axis (for example, MAX, MIN, TOTAL, AVERAGE, MAX_PREC, MAX_SUCC, CONTINUOUS, ...)")
@click.option("-i","--intended_observation_spacing",default=None,type=str,help="The expected duration between individual observations, expressed as ISO8601 duration (e.g., P1D)")
@click.option("-a","--aggregation_duration",default=None,type=str,help="Time aggregation that has occurred to the value in the timeseries, expressed as ISO8601 duration (e.g., P1D)")
@click.option("-F","--filter", type=feature_filter_value_type, multiple=True, help="Set additional filters as key=value. Valid keys: %s" % ", ".join(FEATURE_VALID_FILTERS.keys()))
@click.option("-f","--format",default="json",type=str,help="Response format (e.g. JSON (raw), GeoJSON or CSV)")
@click.option("-1", "--first_page_only", is_flag=True, help="Retrieve only first page.")
@click.option("-r", "--resumption_token", type=str, default=None, help="Retrieve next page using the provided resumption token")
@click.option('-d','--debug', is_flag=True, help='Log debug messages')
def features(token, url, output, monitoring_point, variable_name, timeseries_identifier, limit, west, south, east, north, ontology, view, time_interpolation, intended_observation_spacing, aggregation_duration, filter, format, first_page_only, resumption_token, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    config = {}
    if token is not None:
        config["token"] = token
    if url is not None:
        config["token"] = token
    parsed_filter = {k: v for k, v in filter} if filter is not None else None
    client = OmApiClient(config)
    retrieve_method = client.getFeatures if first_page_only or resumption_token is not None else client.getFeaturesWithPagination
    features = retrieve_method(
        feature = monitoring_point, 
        observedProperty = variable_name, 
        observationIdentifier = timeseries_identifier,
        limit = limit,
        view = view,
        west = west, 
        south = south, 
        east = east, 
        north = north, 
        ontology = ontology, 
        timeInterpolation = time_interpolation, 
        intendedObservationSpacing = intended_observation_spacing, 
        aggregationDuration = aggregation_duration,
        resumptionToken = resumption_token,
        **parsed_filter
    )
    if output is not None:
        if format.lower() == "csv":
            df = featuresToDataFrame(features)
            df.to_csv(open(output, "w"), index=False)
        elif format.lower() == "geojson":
            json.dump(featuresToGeoJSON(features), open(output, "w"), ensure_ascii=False)
        else:
            json.dump(features, open(output, "w"), ensure_ascii=False)
    else:
        if format.lower() == "csv":
            df = featuresToDataFrame(features)
            click.echo(df.to_csv(index=False))
        elif format.lower() == "geojson":
            click.echo(json.dumps(featuresToGeoJSON(features), ensure_ascii=False))
        else:
            click.echo(json.dumps(features, ensure_ascii=False))

@cli.command()
def init():
    client = OmApiClient()
    logging.info("om-api-client config file created at %s" % client.config_path)    

if __name__ == '__main__':
    command, remaining = parse_first_arg()
    sys.argv = [sys.argv[0], command] + remaining  # Reset sys.argv for click
    cli()
