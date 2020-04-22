import base64
from contextlib import contextmanager
import json
import logging
import os
import shutil
import requests
import sys

from requests.exceptions import HTTPError
from subprocess import Popen, PIPE
from threading import Timer
try:
    from urllib.request import quote
except ImportError:
    from urllib import quote

from splunk.util import normalizeBoolean
from splunk.rest import simpleRequest
from splunk.clilib.cli_common import getConfKeyValue
from splunk.clilib.bundle_paths import make_splunkhome_path

sys.path.append(make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "lib"]))
from splunk_sa_cim.log import setup_logger
from splunk_sa_cim.modaction_queue import ModularActionQutils, ModularActionQueueBR
from splunk_sa_cim.modinput import JsonModularInput, Field

# Python 2+3 basestring
try:
    basestring
except NameError:
    basestring = str


class RelayModAction(JsonModularInput):
    QUEUE_REALM = "cam_queue"
    ACTION_NAMESPACE = "Splunk_SA_CIM"
    SEARCH_INFO_FILENAME = "info.csv"

    def __init__(self, logger):
        self.logger = logger

        scheme_args = {
            'title': "Modular Action Relay",
            'description': "Relay modaction from remote splunk search head.",
            'use_external_validation': "true",
            'streaming_mode': "json",
            'use_single_instance': "false"
        }

        args = [
            Field("uri", "Remote Search Head URI", "Search head.", required_on_create=True,
                  required_on_edit=False),
            Field("description", "Description", "Description of the remote Splunk instance.", required_on_create=True,
                  required_on_edit=False),
            Field("username", "API Key Username", "Username for your API key, must be unique.", required_on_create=True,
                  required_on_edit=False),
            Field("verify", "Verify", "Need to verify certificates between worker and Search Head?",
                  required_on_create=False, required_on_edit=False),
            Field("client_cert", "Client Certificate", "Filename of client certificate for verification.",
                  required_on_create=False, required_on_edit=False)
        ]

        super(RelayModAction, self).__init__(scheme_args, args)

    def normalize_time(self, timestr):
        try:
            if not isinstance(timestr, int):
                if timestr.isdigit():
                    return int(timestr)
                elif timestr.endswith('s'):
                    return int(timestr[:-1])
                elif timestr.endswith('m'):
                    return int(timestr[:-1]) * 60
                elif timestr.endswith('h'):
                    return int(timestr[:-1]) * 3600
                elif timestr.endswith('d'):
                    return int(timestr[:-1]) * 86400
                else:
                    return None
            return timestr
        except ValueError:
            return None

    def get_password(self, realm, username, session_key):
        """
        Get password for the user in given realm
        """
        namespace = quote(self.ACTION_NAMESPACE, safe='')
        key = quote("%s:%s:" % (realm, username), safe='')
        uri = '/servicesNS/nobody/%s/storage/passwords/%s' % (namespace, key)
        getargs = {'output_mode': 'json'}
        try:
            unused_r, c = simpleRequest(uri, getargs=getargs, sessionKey=session_key, raiseAllErrors=True)
            return json.loads(c)['entry'][0]['content']['clear_password']
        except Exception as e:
            self.logger.error("Failed to get credential for %s:%s: %s", realm, username, e)
            return None

    def request(self, uri, method, worker, password, verify, cert, params='', data=''):
        headers = {
            'X-API-ID': worker,
            'X-API-KEY': password
        }
        if method == 'get':
            return requests.get(uri, params=params, headers=headers, verify=verify, cert=cert)
        elif method == 'post':
            return requests.post(uri, data=data, headers=headers, verify=verify, cert=cert)

    def get_actions(self, target, worker, password, verify, client_cert=''):
        """
        Get a queue of actions of specified worker
        """
        uri = "%s/services/alerts/modaction_queue/peek" % target
        r = self.request(uri, 'get', worker, password, verify, client_cert, params={'output_mode': 'json'})
        if r.status_code != requests.codes.ok:
            self.logger.error("Failed to get actions for %s: %s", worker, r.text)
            return []
        self.logger.info("Successfully retrieved actions for %s", worker)
        return r.json()

    def get_local_alert_actions(self, session_key):
        getargs = {
            'output_mode': 'json',
            'search': 'is_custom=1 AND payload_format=json',
            'count': 0
        }
        try:
            unused_r, c = simpleRequest('alerts/alert_actions', getargs=getargs, sessionKey=session_key, raiseAllErrors=True)
        except Exception as e:
            self.logger.error("Failed to get local alert actions: %s", e)
            return {}

        local_alert_actions = {}
        for action in json.loads(c)['entry']:
            # check if the action supports worker, if yes, add to the return dictionary
            name = action['name']
            content = action['content']
            try:
                _cam = json.loads(content['param._cam'])
                if normalizeBoolean(_cam['supports_workers']):
                    local_alert_actions[name] = action
            except Exception:
                continue

        return local_alert_actions

    @contextmanager
    def ensure_local_dispatch_dir(self, stanza, sid, mode=0o755):
        """
        Ensure an emulated local dispatch directory for a given stanza exists
        under checkpoint_dir for the duration of the enclosing code block.
        """
        destdir = os.path.join(self.checkpoint_dir, stanza, sid)
        if not os.path.isdir(destdir):
            os.makedirs(destdir, mode)

        try:
            yield destdir
        finally:
            try:
                shutil.rmtree(os.path.realpath(destdir))
            except Exception as e:
                self.logger.error("Unable to cleanup search results directory: %s", e)

    def fetch_results(self, target, key, destdir, file_name, worker, password, verify, client_cert=''):
        dest = os.path.join(destdir, file_name)
        uri = "%s/services/alerts/modaction_queue/peek/%s" % (target, key)
        r = self.request(uri, 'get', worker, password, verify, client_cert)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        self.logger.info("Successfully fetched results_file content for action with key %s for worker %s", key, worker)
        try:
            # write-binary usage intentional here
            with open(dest, "wb") as f:
                f.write(base64.b64decode(r.text))
            return dest
        except (OSError, IOError) as e:
            self.logger.error("Failed to save results file: %s", e)
            return None

    def save_search_info(self, b64info, destdir):
        if not isinstance(b64info, basestring):
            return

        dest = os.path.join(destdir, self.SEARCH_INFO_FILENAME)
        try:
            # write-binary usage intentional here
            with open(dest, "wb") as f:
                f.write(base64.b64decode(b64info))
        except (OSError, IOError) as e:
            self.logger.error("Failed to save info file: %s", e)
        return dest

    def dequeue(self, target, key, worker, password, verify, client_cert=''):
        uri = "%s/services/alerts/modaction_queue/dequeue" % target
        r = self.request(uri, 'post', worker, password, verify, client_cert, data=json.dumps([key]))
        if r.status_code != requests.codes.ok:
            self.logger.error("Exception when updating cam queue: %s", r.text)
        self.logger.info("Successfully dequeued action with key %s for worker %s", key, worker)
        return r

    def get_action_payload(self, settings):
        payload = json.loads(settings)
        payload['configuration'].pop('_cam_workers', None)
        if 'sid' not in payload:
            raise ValueError("Missing sid")
        if 'results_file' not in payload:
            raise ValueError("Missing results file")
        return payload

    def run_action(self, cmd, settings, maxtime):
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        def kill():
            self.logger.error("modaction killed due to timeout %s seconds", maxtime)
            p.kill()

        timer = Timer(maxtime, kill)
        try:
            timer.start()
            out, err = p.communicate(
                input=json.dumps(settings).encode('utf-8'))
        finally:
            timer.cancel()
        self.logger.info("action output: %s", out)
        self.logger.info("action err: %s", err)
        return p.returncode

    def normalize_cert_path(self, filename):
        if filename in ['', '..', None] or os.path.basename(filename) != filename:
            return ''
        return make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "auth", filename])

    def normalize_verify(self, verify):
        normalized = normalizeBoolean(verify)
        if normalized in [True, False]:
            return normalized
        if normalized is None or normalized.strip() == '':
            return False
        return self.normalize_cert_path(verify)

    def validate_action(self, action_name, alert_actions):
        alert_action = alert_actions.get(action_name)
        if alert_action is None:
            return None, None

        maxtime = alert_action['content']['maxtime']
        normalized_maxtime = self.normalize_time(maxtime)
        return alert_action, normalized_maxtime

    def run(self, params):
        stanza_name = params.get('name').split("://", 1)[1]
        username = params['username']
        session_key = self._input_config.session_key
        password = self.get_password(self.QUEUE_REALM, username, session_key)
        if password is None:
            self.logger.error("couldn't get password for %s", username)
            return

        worker = getConfKeyValue('server', 'general', 'serverName')
        client_cert = self.normalize_cert_path(params['client_cert'])
        target = params['uri']
        verify = self.normalize_verify(params['verify'])

        if verify not in [True, False] and not os.path.isfile(client_cert):
            self.logger.error("invalid verify: %s", params['verify'])
            return

        if client_cert != '' and not os.path.isfile(client_cert):
            self.logger.error("invalid client cert: %s", params['client_cert'])
            return

        actions = self.get_actions(target, worker, password, verify, client_cert)
        alert_actions = self.get_local_alert_actions(session_key)
        self.logger.info("local alert actions: %s", alert_actions.keys())

        for action in actions:
            search_info = action.pop('info', None)
            action_name = action['action_name']
            self.logger.info("original action: %s", action_name)
            key = None
            try:
                key = ModularActionQutils.build_key(
                    {'worker': worker, 'sid': action['sid'], 'action_name': action_name})
                payload = self.get_action_payload(action['settings'])
            except (KeyError, ValueError, ModularActionQueueBR):
                self.logger.exception("Invalid modaction received: %s", json.dumps(action, indent=2))
                if key:
                    self.dequeue(target, key, worker, password, verify, client_cert)
                continue

            sid = payload['sid']
            alert_action, normalized_maxtime = self.validate_action(action_name, alert_actions)
            if alert_action is None:
                self.logger.error("Modular action %s not found", action_name)
                self.dequeue(target, key, worker, password, verify, client_cert)
                continue
            elif normalized_maxtime is None:
                self.logger.error("Invalid maxtime received: %s", alert_action['content']['maxtime'])
                self.dequeue(target, key, worker, password, verify, client_cert)
                continue

            payload['server_uri'] = target
            file_name = os.path.basename(payload['results_file'])
            results_file = None
            with self.ensure_local_dispatch_dir(stanza_name, sid) as dispatch_dir:
                try:
                    results_file = self.fetch_results(target, key, dispatch_dir, file_name, worker, password, verify, client_cert)
                except HTTPError as e:
                    self.logger.error("Failed to fetch results: %s", e)
                    if e.response.status_code == requests.codes.not_found:
                        self.dequeue(target, key, worker, password, verify, client_cert)

                if results_file is not None:
                    self.save_search_info(search_info, dispatch_dir)
                    payload['results_file'] = results_file
                    name = alert_action['name']
                    app = alert_action['acl']['app']
                    script = make_splunkhome_path(["etc", "apps", app, "bin", "%s.py" % name])
                    cmd = [make_splunkhome_path(["bin", "splunk"]), "cmd", "python", script, "--execute"]
                    try:
                        returncode = self.run_action(cmd, payload, normalized_maxtime)
                        if returncode != 0:
                            self.logger.info("Modular alert exit with code %d", returncode)
                        self.dequeue(target, key, worker, password, verify, client_cert)
                    except Exception as e:
                        self.logger.error("Exception when running modular alert %s: %s", stanza_name, e)


if __name__ == '__main__':
    logger = setup_logger('relaymodaction', level=logging.INFO)
    try:
        modinput = RelayModAction(logger=logger)
        modinput.execute()
    except Exception:
        logger.exception("Error")
