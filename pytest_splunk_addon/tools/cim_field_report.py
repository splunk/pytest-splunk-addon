#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os.path
import sys
import logging
import json
import argparse
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pytest_splunk_addon.helmut.manager.jobs import Jobs
from pytest_splunk_addon.helmut.splunk.cloud import CloudSplunk
from pytest_splunk_addon.standard_lib.addon_parser import AddonParser

from splunklib import binding

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.ERROR,
)

LOGGER = logging.getLogger("cim-field-report")


def get_config():
    """Defines and collects and validates script command arguments
    Additionally
        set log level for script logging,
        calls sys.exit if --splunk-app folder does not exist

    Returns
    -------
    argparse.Namespace
        the populated namespace.
    """

    parser = argparse.ArgumentParser(
        description="Python Script to test Splunk functionality"
    )

    parser.add_argument(
        "--splunk-index",
        dest="splunk_index",
        default="*",
        type=str,
        help="Splunk index to be used as a source for the report. Default is *",
    )
    parser.add_argument(
        "--splunk-web-scheme",
        dest="splunk_web_scheme",
        default="https",
        type=str,
        choices=["http", "https"],
        help="Splunk connection schema https or http, default is https.",
    )
    parser.add_argument(
        "--splunk-host",
        dest="splunk_host",
        default="127.0.0.1",
        type=str,
        help="Address of the "
        "Splunk REST API server host to connect. Default is 127.0.0.1",
    )
    parser.add_argument(
        "--splunk-port",
        dest="splunk_port",
        default="8089",
        type=int,
        help="Splunk Management port. default is 8089.",
    )
    parser.add_argument(
        "--splunk-user",
        dest="splunk_user",
        default="admin",
        type=str,
        help="Splunk login user. The user should have search capabilities.",
    )
    parser.add_argument(
        "--splunk-password",
        dest="splunk_password",
        type=str,
        required=True,
        help="Password of the Splunk user",
    )
    parser.add_argument(
        "--splunk-app",
        dest="splunk_app",
        type=str,
        required=True,
        help="Path to Splunk app package. The package "
        "should have the configuration files in the default folder.",
    )
    parser.add_argument(
        "--splunk-report-file",
        dest="splunk_report_file",
        default="cim_field_report.json",
        type=str,
        help="Output file for cim field report. Default is: cim_field_report.json",
    )
    parser.add_argument(
        "--splunk-max-time",
        dest="splunk_max_time",
        default="120",
        type=int,
        help="Search query execution time out in seconds. Default is: 120",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default="ERROR",
        type=str,
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging level used by the tool",
    )

    args = parser.parse_args()
    LOGGER.setLevel(args.log_level)

    if not os.path.exists(args.splunk_app) or not os.path.isdir(args.splunk_app):
        msg = "There is no such directory: {}".format(args.splunk_app)
        LOGGER.error(msg)
        sys.exit(msg)

    return args


def collect_job_results(job, acc, fn):
    """Collects all job results by requesting pages of 1000 items

    Parameters
    ----------
    job : pytest_splunk_addon.helmut.manager.jobs.job
        Finished job ready to collect results
    acc : any
        An accumulator object that collects job results
    fn : function
        External function that receives accumulator object and job results one by one.
        This function controls how results are transformed and accumulated

    Returns
    -------
    any
        The accumulator object passes as argument acc
    """

    offset, count = 0, 1000
    while True:
        records = job.get_results(offset=offset, count=count).as_list
        LOGGER.debug(
            f"Read fields: offset: {offset}, count: {count}, found: {len(records)}"
        )
        fn(acc, records)
        offset += count
        if len(records) < count:
            break

    return acc


def collect_punct_and_eventtype(data, records):
    """Accumulator function to be used with collect_job_results.

    Accumulates punct and eventtype values, used in get_punct_by_eventtype

    Parameters
    ----------
    data : [set(), {}]
        Accumulator object to be updated (see collect_job_results acc argument)
    records : list
        SPL job result entries (result of job.get_results(...).as_list)
    """

    for record in records:
        eventtype = record["eventtype"]
        punct = record["punct"]
        if isinstance(eventtype, list):
            for entry in eventtype:
                new_val = (entry, punct)
                if new_val not in data:
                    data.append(new_val)
        else:
            new_val = (eventtype, punct)
            if new_val not in data:
                data.append(new_val)


def get_punct_by_eventtype(jobs, eventtypes, config):
    """Runs SPL request to collect all unique  eventtype+punct pairs from splunk instance

    Parameters
    ----------
    jobs : pytest_splunk_addon.helmut.manager.jobs.Jobs
        Jobs object capable to create a new splunk search job
    eventtypes : list
        List of splunk eventtypes names taken from TA configurations
    config : dict
        configuration settings mainly collected from command arguments

    Returns
    -------
    list
        list of tuples of 2 elements, representing collected unique pairs of eventtype+punct
    None
        if exception taks places during splunk search request
    """

    start = time.time()
    eventtypes_str = ",".join(['"{}"'.format(et) for et in eventtypes])
    query = 'search (index="{}") eventtype IN ({}) | dedup punct,eventtype | table punct,eventtype'.format(
        config.splunk_index, eventtypes_str
    )
    LOGGER.debug(query)
    try:
        job = jobs.create(query, auto_finalize_ec=120, max_time=config.splunk_max_time)
        job.wait(config.splunk_max_time)
        result = collect_job_results(job, [], collect_punct_and_eventtype)
        LOGGER.info(
            "Time taken to collect eventtype & punct combinations: {} s".format(
                time.time() - start
            )
        )
        return result
    except Exception as e:
        LOGGER.error("Errors when executing search!!! Error: {}".format(e))
        LOGGER.debug(traceback.format_exc())


def get_field_names(jobs, eventtypes, config):
    """Runs SPL request to collect all field names from events with specific eventtypes

    Parameters
    ----------
    jobs : pytest_splunk_addon.helmut.manager.jobs.Jobs
        Jobs object capable to create a new splunk search job
    eventtypes : list
        List of splunk eventtypes names taken from TA configurations
    config : dict
        configuration settings mainly collected from command arguments

    Returns
    -------
    list
        collected field names
    None
        if exception taks places during splunk search request
    """

    start = time.time()
    eventtypes_str = ",".join(['"{}"'.format(et) for et in eventtypes])
    query = 'search (index="{}") eventtype IN ({}) | fieldsummary'.format(
        config.splunk_index, eventtypes_str
    )
    LOGGER.debug(query)
    try:
        job = jobs.create(query, auto_finalize_ec=120, max_time=config.splunk_max_time)
        job.wait(config.splunk_max_time)
        result = collect_job_results(
            job, [], lambda acc, recs: acc.extend([v["field"] for v in recs])
        )
        LOGGER.info(
            "Time taken to collect field names: {} s".format(time.time() - start)
        )
        return result
    except Exception as e:
        LOGGER.error("Errors when executing search!!! Error: {}".format(e))
        LOGGER.debug(traceback.format_exc())


def update_summary(data, records):
    """Accumulator function to be used with collect_job_results.

    Parameters
    ----------
    data : [set(), {}]
        Accumulator object to be updated (see collect_job_results acc argument)
    records : list
        SPL job result entries (result of job.get_results(...).as_list)
    """

    sourcetypes, summary = data
    for entry in records:
        if "sourcetype" in entry:
            sourcetypes.add(entry.pop("sourcetype"))

        field_set = frozenset(entry.keys())
        if field_set in summary:
            summary[field_set] += 1
        else:
            summary[field_set] = 1


def get_fieldsummary(jobs, punct_by_eventtype, config):
    """Runs SPL request to extract events for specific punct+eventtype values combinations.
    Builds fieldsummary information for each collected event group

    Parameters
    ----------
    jobs : pytest_splunk_addon.helmut.manager.jobs.Jobs
        Jobs object capable to create a new splunk search job
    punct_by_eventtype : list
        List of tuples of 2 elements, representing collected unique pairs of eventtype+punct
    config : dict
        configuration settings mainly collected from command arguments

    Returns
    -------
    dict
        dict key - eventtype, dict value - a list of fields summaries per punct
    """
    start = time.time()

    result = {}
    for eventtype, punct in punct_by_eventtype:
        result[eventtype] = []
        query_templ = 'search (index="{}") eventtype="{}" punct="{}" | fieldsummary'
        query = query_templ.format(
            config.splunk_index,
            eventtype,
            punct.replace("\\", "\\\\").replace('"', '\\"'),
        )
        LOGGER.debug(query)
        try:
            job = jobs.create(
                query, auto_finalize_ec=120, max_time=config.splunk_max_time
            )
            job.wait(config.splunk_max_time)
            summary = collect_job_results(job, [], lambda acc, recs: acc.extend(recs))
        except Exception as e:
            LOGGER.error("Errors executing search: {}".format(e))
            LOGGER.debug(traceback.format_exc())

        try:
            for f in summary:
                f["values"] = json.loads(f["values"])
            result[eventtype].append(summary)
        except Exception as e:
            LOGGER.warn('Parameter "values" is not a json object: {}'.format(e))
            LOGGER.debug(traceback.format_exc())

    LOGGER.info("Time taken to build fieldsummary: {}".format(time.time() - start))
    return result


def get_fieldsreport(jobs, eventtypes, fields, config):
    """Runs SPL requests to prepare unique lists of extracted fields for each eventtype

    Parameters
    ----------
    jobs : pytest_splunk_addon.helmut.manager.jobs.Jobs
        Jobs object capable to create a new splunk search job
    eventtypes : list
        List of splunk eventtypes names taken from TA configurations
    fields : list
        List of expected field names
    config : dict
        configuration settings mainly collected from command arguments

    Returns
    -------
    (dict, set)
        Returns 2 values - extracted field lists per eventtype and set of unique sourcetypes collected in SPL requests
    """

    start = time.time()
    report, sourcetypes = {}, set()
    field_list = ",".join(['"{}"'.format(f) for f in fields])
    for eventtype, tags in eventtypes.items():
        query = 'search (index="{}") eventtype="{}" | table sourcetype,{}'.format(
            config.splunk_index, eventtype, field_list
        )
        try:
            job = jobs.create(
                query, auto_finalize_ec=120, max_time=config.splunk_max_time
            )
            job.wait(config.splunk_max_time)
            et_sourcetypes, et_summary = collect_job_results(
                job, [set(), {}], update_summary
            )
            sourcetypes = sourcetypes.union(et_sourcetypes)
            report[eventtype] = {
                "tags": tags,
                "sourcetypes": list(et_sourcetypes),
                "summary": [
                    {"fields": sorted(list(k)), "count": v}
                    for k, v in et_summary.items()
                ],
            }
        except Exception as e:
            LOGGER.error("Errors when executing search!!! Error: {}".format(e))
            LOGGER.debug(traceback.format_exc())

    LOGGER.info(
        "Time taken to build fields extractions section: {} s".format(
            time.time() - start
        )
    )
    return report, sourcetypes


def read_ta_meta(config):
    """Extracts TA's name and version from TA app.manifest file

    Parameters
    ----------
    config : dict
        configuration settings mainly collected from command arguments,
        required to locate TA configuration files

    Returns
    -------
    dict
        {
            "name": "<TA's name>",
            "version": "<TA's version>"
        }
    """

    app_manifest = os.path.join(config.splunk_app, "app.manifest")
    with open(app_manifest) as f:
        manifest = json.load(f)

    ta_id_info = manifest.get("info", {}).get("id", {})
    return {k: v for k, v in ta_id_info.items() if k in ["name", "version"]}


def build_report(jobs, eventtypes, config):
    """Puts together all report sections (ta_name (meta), sourcetypes,
    fieldsreport, fieldsummary), saves report to file

    Parameters
    ----------
    jobs : pytest_splunk_addon.helmut.manager.jobs.Jobs
        Jobs object capable to create a new splunk search job
    eventtypes : list
        List of splunk eventtypes names taken from TA configurations
    config : dict
        configuration settings mainly collected from command arguments
    """

    start = time.time()

    fields = get_field_names(jobs, eventtypes, config)
    if fields:
        fieldsreport, sourcetypes = get_fieldsreport(jobs, eventtypes, fields, config)
    else:
        fieldsreport, sourcetypes = "No field extractions discovered", []

    punct_by_eventtype = get_punct_by_eventtype(jobs, eventtypes, config)
    if punct_by_eventtype:
        fieldsummary = get_fieldsummary(jobs, punct_by_eventtype, config)
    else:
        fieldsummary = "No punct by eventtype combinations discovered"

    summary = {
        "ta_name": read_ta_meta(config),
        "sourcetypes": list(sourcetypes),
        "fieldsreport": fieldsreport,
        "fieldsummary": fieldsummary,
    }

    with open(config.splunk_report_file, "w") as f:
        json.dump(summary, f, indent=4)

    LOGGER.info("Total time taken to generate report: {} s".format(time.time() - start))


def get_addon_eventtypes(addon_path):
    """Extracts TA specific eventtypes from the TA's conf files

    Parameters
    ----------
    addon_path : str
        path to TA package folder

    Returns
    -------
    list
        Eventtypes defined in the TA conf
    """

    parser = AddonParser(addon_path)

    eventtypes = {
        eventtype["stanza"]: []
        for eventtype in parser.eventtype_parser.get_eventtypes()
    }

    for item in parser.tags_parser.get_tags():
        stanza, tag, enabled = item["stanza"], item["tag"], item["enabled"]
        parts = [s.strip().strip('"') for s in stanza.split("=", 1)]
        if len(parts) > 1 and parts[0] == "eventtype":
            eventtype = parts[1]
            if enabled and eventtype in eventtypes and tag not in eventtypes[eventtype]:
                eventtypes[eventtype].append(tag)

    LOGGER.debug(eventtypes)
    return eventtypes


def main():
    """Main script method and entry point"""

    config = get_config()

    splunk_cfg = {
        "splunkd_scheme": config.splunk_web_scheme,
        "splunkd_host": config.splunk_host,
        "splunkd_port": config.splunk_port,
        "username": config.splunk_user,
        "password": config.splunk_password,
    }

    try:
        eventtypes = get_addon_eventtypes(config.splunk_app)

        cloud_splunk = CloudSplunk(**splunk_cfg)
        conn = cloud_splunk.create_logged_in_connector()
        jobs = Jobs(conn)

        build_report(jobs, eventtypes, config)

    except (TimeoutError, ConnectionRefusedError) as error:
        msg = "Failed to connect Splunk instance {}://{}:{}, make sure you provided correct connection information. {}".format(
            config.splunk_web_scheme, config.splunk_host, config.splunk_port, error
        )
        LOGGER.error(msg)
        sys.exit(msg)
    except binding.AuthenticationError as error:
        msg = "Authentication to Splunk instance has failed, make sure you provided correct Splunk credentials. {}".format(
            error
        )
        LOGGER.error(msg)
        sys.exit(msg)
    except Exception as error:
        msg = "Unexpected exception: {}".format(error)
        LOGGER.error(msg)
        LOGGER.debug(traceback.format_exc())
        sys.exit(msg)


if __name__ == "__main__":
    main()
