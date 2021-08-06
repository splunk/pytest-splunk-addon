import os.path
import sys
import logging
import json
import argparse
from pytest_splunk_addon.helmut.manager.jobs import Jobs
from pytest_splunk_addon.helmut.splunk.cloud import CloudSplunk
from pytest_splunk_addon.standard_lib.addon_parser import AddonParser


LOGGER = logging.getLogger('cim_field_report')


def get_punct_by_eventtype(jobs, eventtypes):
    eventtypes_str = ",".join(['"{}"'.format(et) for et in eventtypes])
    query = 'search (index=*) eventtype IN ({}) | dedup punct,eventtype | table punct,eventtype'.format(eventtypes_str)
    print(query)
    try:
        max_time = 120
        job = jobs.create(query, auto_finalize_ec=120, max_time=max_time)
        job.wait(max_time)
        print(job.get_results().as_list)
        return [(v["eventtype"], v["punct"]) for v in job.get_results().as_list]
    except Exception as e:
        LOGGER.error("Errors when executing search!!! Error: {}".format(e))


def get_fieldsummary(jobs, eventtype, punct):
    query = 'search (index=*) eventtype="{}" punct="{}" | fieldsummary'.format(eventtype,
                                                                               punct.replace("\\", "\\\\").replace('"',
                                                                                                                   '\\"'))
    LOGGER.debug(query)
    try:
        max_time = 120
        job = jobs.create(query, auto_finalize_ec=120, max_time=max_time)
        job.wait(max_time)
        summary = job.get_results().as_list
    except Exception as e:
        LOGGER.error("Errors when executing search!!! Error: {}".format(e))

    try:
        for f in summary:
            f["values"] = json.loads(f["values"])
        return summary
    except Exception as e:
        LOGGER.error('Parameter "values" is not a json object: {}'.format(e))


def parse_args():
    parser = argparse.ArgumentParser(description='Python Script to test Splunk functionality')

    parser.add_argument('--splunk-web-scheme', dest='splunk_web_scheme', default='https', type=str,
                        help='Enable SSL (HTTPS) in Splunk Web? default is http.')
    parser.add_argument('--splunk-host', dest='splunk_host', default='127.0.0.1', type=str, help='Address of the '
                        'Splunk Server where search queries will be executed. Do not provide "http" '
                        'scheme in the host. Default is 127.0.0.1')
    parser.add_argument('--splunk-port', dest='splunk_port', default='8089', type=int,
                        help='Splunk Management port. default is 8089.')
    parser.add_argument('--splunk-user', dest='splunk_user', default='admin', type=str,
                        help='Splunk login user. The user should have search capabilities.')
    parser.add_argument('--splunk-password', dest='splunk_password', type=str, help='Password of the Splunk user')
    parser.add_argument('--splunk-app', dest='splunk_app', type=str, help='Path to Splunk app package. The package '
                        'should have the configuration files in the default folder.')

    return parser.parse_args()


def main():
    args = parse_args()

    splunk_cfg = {
        "splunkd_scheme": args.splunk_web_scheme,
        "splunkd_host": args.splunk_host,
        "splunkd_port": args.splunk_port,
        "username": args.splunk_user,
        "password": args.splunk_password
    }

    checkDir = parse_args()
    isDir = os.path.isdir(checkDir.splunk_app)
    isExist = os.path.exists(checkDir.splunk_app)
    if not isExist or not isDir:
        msg = 'There is no such Directory: {}'.format(checkDir.splunk_app)
        LOGGER.error(msg)
        sys.exit(msg)

    path = AddonParser(args.splunk_app)

    try:
        eventtypes = [eventtype for eventtype in path.eventtype_parser.eventtypes.sects]
        cloud_splunk = CloudSplunk(**splunk_cfg)
        conn = cloud_splunk.create_logged_in_connector()
        jobs = Jobs(conn)
        res = {}
        for eventtype, punct in get_punct_by_eventtype(jobs, eventtypes):
            print(eventtype, punct)
            if eventtype not in res:
                res[eventtype] = []

            res[eventtype].append(get_fieldsummary(jobs, eventtype, punct))

        with open("cim_field_report.json", "w") as f:
            json.dump(res, f, indent=4)

    except TimeoutError:
        msg = 'Wrong Splunk Host Address: {}'.format(args.splunk_host)
        LOGGER.error(msg)
        sys.exit(msg)
    except ValueError:
        msg = 'Wrong Splunk Scheme: {}'.format(args.splunk_web_scheme)
        LOGGER.error(msg)
        sys.exit(msg)
    except ConnectionRefusedError:
        msg = 'Wrong Splunk Port Number: {}'.format(args.splunk_port)
        LOGGER.error(msg)
        sys.exit(msg)
    except Exception as error:
        msg = 'Splunk Username or Password is wrong: {}'.format(error)
        LOGGER.error(msg)
        sys.exit(msg)


if __name__ == "__main__":
    main()
