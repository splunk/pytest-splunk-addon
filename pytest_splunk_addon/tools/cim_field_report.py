import os.path
import sys
import logging
import json
import argparse
import re
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pytest_splunk_addon.helmut.manager.jobs import Jobs
from pytest_splunk_addon.helmut.splunk.cloud import CloudSplunk
from pytest_splunk_addon.standard_lib.addon_parser import AddonParser

from splunklib import binding

LOGGER = logging.getLogger('cim_field_report')
LOGGER.setLevel('ERROR')

PSA_DATA_MODELS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "standard_lib", "data_models"))


def get_gonfig():
    parser = argparse.ArgumentParser(description='Python Script to test Splunk functionality')

    parser.add_argument('--splunk-index', dest='splunk_index', default='*', type=str,
                        help='Splunk index to be used as a source for the report. Default is *')
    parser.add_argument('--splunk-web-scheme', dest='splunk_web_scheme', default='https', type=str, choices=['http', 'https'],
                        help='Splunk connection schema https or http, default is https.')
    parser.add_argument('--splunk-host', dest='splunk_host', default='127.0.0.1', type=str, help='Address of the '
                        'Splunk REST API server host to connect. Default is 127.0.0.1')
    parser.add_argument('--splunk-port', dest='splunk_port', default='8089', type=int,
                        help='Splunk Management port. default is 8089.')
    parser.add_argument('--splunk-user', dest='splunk_user', default='admin', type=str,
                        help='Splunk login user. The user should have search capabilities.')
    parser.add_argument('--splunk-password', dest='splunk_password', type=str, help='Password of the Splunk user')
    parser.add_argument('--splunk-app', dest='splunk_app', type=str, help='Path to Splunk app package. The package '
                        'should have the configuration files in the default folder.')
    parser.add_argument('--splunk-report-file', dest='splunk_report_file', default='cim_field_report.json', type=str,
                        help='Output file for cim field report. Default is: cim_field_report.json')
    parser.add_argument('--splunk-max-time', dest='splunk_max_time', default='120', type=int,
                        help='Search query execution time out in seconds. Default is: 120')
    parser.add_argument('--log-level', dest='log_level', default='ERROR', type=str, choices=['CRITICAL', 'ERROR', 'WARNING' 'INFO', 'DEBUG'],
                        help='Logging level used by the tool')

    args =  parser.parse_args()

    if not os.path.exists(args.splunk_app) or not os.path.isdir(args.splunk_app):
        msg = 'There is no such directory: {}'.format(args.splunk_app)
        LOGGER.error(msg)
        sys.exit(msg)

    return args

def get_punct_by_eventtype(jobs, eventtypes, config):
    eventtypes_str = ",".join(['"{}"'.format(et) for et in eventtypes])
    query = 'search (index="{}") eventtype IN ({}) | dedup punct,eventtype | table punct,eventtype'.format(config.splunk_index, eventtypes_str)
    LOGGER.debug(query)
    try:
        job = jobs.create(query, auto_finalize_ec=120, max_time=config.splunk_max_time)
        job.wait(config.splunk_max_time)
        LOGGER.debug(job.get_results().as_list)
        return [(v["eventtype"], v["punct"]) for v in job.get_results().as_list]
    except Exception as e:
        LOGGER.error("Errors when executing search!!! Error: {}".format(e))


def get_fieldsummary(jobs, eventtype, punct, config):
    query_templ = 'search (index="{}") eventtype="{}" punct="{}" | fieldsummary'
    query = query_templ.format(config.splunk_index, eventtype, punct.replace("\\", "\\\\").replace('"','\\"'))
    LOGGER.debug(query)
    try:
        job = jobs.create(query, auto_finalize_ec=120, max_time=config.splunk_max_time)
        job.wait(config.splunk_max_time)
        summary = job.get_results().as_list
    except Exception as e:
        LOGGER.error("Errors executing search: {}".format(e))

    try:
        for f in summary:
            f["values"] = json.loads(f["values"])
        return summary
    except Exception as e:
        LOGGER.warn('Parameter "values" is not a json object: {}'.format(e))


def get_cim_fields_summary(jobs, eventtype, eventtypes, cim_summary, sourcetypes, config):
    for data_set in eventtypes[eventtype]:
        data_set_name = ":".join(data_set["name"])
        fields = ",".join(data_set["fields"])
        query = 'search (index="{}") eventtype="{}" | table sourcetype,{}'.format(config.splunk_index, eventtype, fields)
        LOGGER.debug(query)
        try:
            job = jobs.create(query, auto_finalize_ec=120, max_time=config.splunk_max_time)
            job.wait(config.splunk_max_time)
            events = job.get_results().as_list            
        except Exception as e:
            LOGGER.error("Errors when executing search!!! Error: {}".format(e))

        for event in events:
            if data_set_name not in cim_summary:
                cim_summary[data_set_name] = {}
            
            if eventtype not in cim_summary[data_set_name]:
                cim_summary[data_set_name][eventtype] = []

            sourcetypes.add(event.pop("sourcetype", None))
            found_fields = sorted(event.keys())
            for record in cim_summary[data_set_name][eventtype]:
                if record["fields"] == found_fields:
                    record["count"] += 1
                    break
            else:
                cim_summary[data_set_name][eventtype].append({
                    "fields": found_fields,
                    "count": 1
                })


def read_ta_meta(config):
    app_manifest = os.path.join(config.splunk_app, "app.manifest")
    with open(app_manifest) as f:
        manifest = json.load(f)

    ta_id_info = manifest.get("info", {}).get("id", {})
    return {k:v for k,v in ta_id_info.items() if k in ["name", "version"]}

def build_report(jobs, eventtypes, config):
    cim_summary = {}
    fieldsummary = {}
    sourcetypes = set()
    punct_by_eventtype = get_punct_by_eventtype(jobs, eventtypes, config)
    if not punct_by_eventtype:
        sys.exit("No punct by eventtype found")

    for eventtype, punct in punct_by_eventtype:
        LOGGER.info("{}, {}".format(eventtype, punct))

        if eventtype not in fieldsummary:
            get_cim_fields_summary(jobs, eventtype, eventtypes, cim_summary, sourcetypes, config)

        if eventtype not in fieldsummary:
            fieldsummary[eventtype] = {
                "models": [":".join(ds["name"]) for ds in eventtypes[eventtype]],
                "summary": []
            }

        fieldsummary[eventtype]["summary"].append(get_fieldsummary(jobs, eventtype, punct, config))

    summary = {
        "ta_name": read_ta_meta(config),
        "sourcetypes": list(sourcetypes),
        "cimsummary": cim_summary,
        "fieldsummary": fieldsummary
    }
    with open(config.splunk_report_file, "w") as f:
        json.dump(summary, f, indent=4)


def collect_dataset_info(obj, data_model_name, parent_data_set=None, parent_fields=set()):
    if "tag=" not in obj.get("search_constraints", ""):
        return []
    
    info = {
        "name": (data_model_name, obj.get("name")),
        "tags": set(obj.get("tags")[0]),
        "parent": (data_model_name, parent_data_set),
        "fields": parent_fields | {f["name"] for f in obj.get("fields", {})}
    }

    res = [info]
    for child_dataset in obj.get("child_dataset", []):
        child_info = collect_dataset_info(child_dataset, data_model_name, obj.get("name"), info["fields"])
        res.extend(child_info)
    
    return res


def load_data_models(dms_path):    
    data_sets = []
    for file_name in glob.glob(os.path.join(dms_path, "*.json")):
        with open(file_name) as f:
            model = json.load(f)
            model_name = model.get("model_name")  
            if not model_name:
                continue    
            for obj in model.get("objects", []):
                data_sets.extend(collect_dataset_info(obj, model_name))
    return data_sets


def find_dataset_by_tags(data_sets, tags):
    res = []
    for data_set in data_sets:
        if data_set["tags"].issubset(tags):
            res.append(data_set)
    return res


def get_addon_eventtypes(addon_path, data_sets):
    parser = AddonParser(addon_path)

    eventtypes = {eventtype: None for eventtype in parser.eventtype_parser.eventtypes.sects}

    stanza_pattern = re.compile("eventtype\s*=\s*(\w+)")
    for stanza, section in parser.tags_parser.tags.sects.items():
        match = stanza_pattern.match(stanza)
        if match and match.groups():
            eventtype = match.groups()[0]
            if eventtype in eventtypes:
                tags = [key for key, option in section.options.items() 
                            if option.value.strip() == "enabled"]
                eventtypes[eventtype] = find_dataset_by_tags(data_sets, tags)
    
    return eventtypes


def main():
    config = get_gonfig()
    LOGGER.setLevel(config.log_level)

    splunk_cfg = {
        "splunkd_scheme": config.splunk_web_scheme,
        "splunkd_host": config.splunk_host,
        "splunkd_port": config.splunk_port,
        "username": config.splunk_user,
        "password": config.splunk_password
    }

    try:
        data_models = load_data_models(PSA_DATA_MODELS_PATH)
        eventtypes = get_addon_eventtypes(config.splunk_app, data_models)

        cloud_splunk = CloudSplunk(**splunk_cfg)
        conn = cloud_splunk.create_logged_in_connector()
        jobs = Jobs(conn)
        
        build_report(jobs, eventtypes, config)

    except TimeoutError as error:
        msg = 'Wrong Splunk Host Address: {}, {}'.format(config.splunk_host, error)
        LOGGER.error(msg)
        sys.exit(msg)
    except ValueError as error:
        msg = 'Wrong Splunk Scheme: {}, {}'.format(config.splunk_web_scheme, error)
        LOGGER.error(msg)
        sys.exit(msg)
    except ConnectionRefusedError as error:
        msg = 'Wrong Splunk Port Number: {}, {}'.format(config.splunk_port, error)
        LOGGER.error(msg)
        sys.exit(msg)
    except binding.AuthenticationError as error:
        msg = 'Splunk Username or Password is not correct: {}'.format(error)
        LOGGER.error(msg)
        sys.exit(msg)
    except Exception as error:
        msg = 'Unexpected exception {}: {}'.format(type(error), error)
        LOGGER.error(msg)
        sys.exit(msg)


if __name__ == "__main__":
    main()
