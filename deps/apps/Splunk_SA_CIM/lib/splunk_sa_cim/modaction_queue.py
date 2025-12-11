import base64
import hashlib
try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
import json
import logging
import os
import re
import splunk.rest as rest
import splunk.util as util

try:
    from urllib.parse import quote, quote_plus
except ImportError:
    from urllib import quote, quote_plus

from splunk import AuthorizationFailed
from splunk.clilib.bundle_paths import make_splunkhome_path

# Python 2+3 basestring
try:
    basestring
except NameError:
    basestring = str


def validate_settings(settings):
    try:
        x = json.loads(settings)
    except Exception:
        return False

    if isinstance(x, dict) and x:
        return True

    return False


class ModularActionQueueBR(Exception):
    '''Custom exception for Modular Action Queue REST handler'''
    pass


class ModularActionQueueUnauth(Exception):
    '''Custom exception for Modular Action Queue REST handler'''
    pass


class ModularActionQueueISE(Exception):
    '''Custom exception for Modular Action Queue REST handler'''
    pass


class ModularActionQutils(object):
    API_KEY_RE = re.compile('^[a-fA-F0-9]{128}$')
    CAM_QUEUE_URI = '/servicesNS/nobody/Splunk_SA_CIM/storage/collections/data/cam_queue'
    QUEUE_PAYLOAD_MAP = {
        'time': (
            lambda x: isinstance(x, (float, int)) and x >= 0,
            'must be a number greater than 0'
        ),
        'action_name': (
            lambda x: isinstance(x, basestring) and x and x != 'unknown',
            'must be a valid action name'
        ),
        'sid': (
            lambda x: isinstance(x, basestring) and x,
            'must be a string with positive length'
        ),
        'info': (
            lambda x: isinstance(x, basestring),
            'must be a string of any length'
        ),
        'worker': (
            lambda x: isinstance(x, basestring) and x,
            'must be a string with positive length'
        ),
        'settings': (
            validate_settings,
            'must be a json encoded nonempty dictionary'
        )
    }
    REQUIRED_KEYS = sorted(QUEUE_PAYLOAD_MAP.keys())

    def __init__(self, logger, session_key):
        self.logger = logger
        self.session_key = session_key

    @staticmethod
    def set_log_level(logger, params):
        debug = util.normalizeBoolean(params.get('debug', False))

        if debug not in [True, False]:
            logger.warn('Unable to normalize debug parameter')
            debug = False

        if debug:
            logger.setLevel(logging.DEBUG)

    @staticmethod
    def is_connection_encrypted(connection):
        if not isinstance(connection, dict):
            return False

        if 'ssl' in connection:
            ssl = util.normalizeBoolean(connection['ssl'])

            if ssl in [True, False]:
                return ssl

        return False

    @staticmethod
    def get_header_item(headers, item):
        if not isinstance(headers, list):
            return None

        for header in headers:
            if isinstance(header, list) and len(header) == 2:
                if header[0] == item:
                    return header[1]

        return None

    @staticmethod
    def is_api_key_formatted(api_key):
        if (isinstance(api_key, basestring)
                and ModularActionQutils.API_KEY_RE.match(
                    api_key)):
            return True

        return False

    @staticmethod
    def validate_payload(payload):
        try:
            jsonargs = json.loads(payload)
        except Exception:
            raise ModularActionQueueBR('Payload must be valid JSON')

        if not isinstance(jsonargs, list):
            raise ModularActionQueueBR('Payload must be a JSON list')

        if not jsonargs:
            raise ModularActionQueueBR('Payload must not be empty')

        return jsonargs

    @staticmethod
    def build_key(item):
        try:
            hashtxt = item['action_name'] + item['sid']

            return '{0}@@{1}'.format(
                item['worker'],
                hashlib.sha1(hashtxt.encode('utf-8')).hexdigest()
            )
        except (TypeError, KeyError):
            raise ModularActionQueueBR('Unable to build _key')

    @staticmethod
    def get_unsave_sids(dequeued_items, sid_items):
        ''' This method returns a list of sids that need to be
        unsaved.  Verify that for each sid, the only work
        remaining is that being "dequeued".

        @param dequeued_items - a dict
        @param sid_items - a dict

        [{'_key': x, 'sid': y}]

        @return dict
        '''
        try:
            dequeued_keys = [
                x['_key']
                for x in dequeued_items
                if x.get('_key')
            ]
            sids = set([
                x['sid']
                for x in sid_items
                if x.get('sid')
            ])
            bad_sids = set([
                x['sid']
                for x in sid_items
                if (x.get('_key')
                    and x['_key'] not in dequeued_keys)
            ])

            return list(sids - bad_sids)

        except Exception:
            return []

    def error(self, msg, status):
        '''
        Return error.

        :param msg: A message describing the problem (a string)
        :type msg: str
        :param status: An integer to be returned as the HTTP status code.
        :type status: int
        '''
        self.logger.error(msg)
        return {'status': status, 'payload': msg}

    def is_api_key_valid(self, worker, api_key):
        if not self.is_api_key_formatted(api_key):
            return False

        en = 'cam_queue:{0}:'.format(worker)
        uri = '/servicesNS/nobody/Splunk_SA_CIM/storage/passwords/{0}'.format(
            quote(en, safe=''))

        try:
            if not self.session_key:
                raise AuthorizationFailed

            unused_r, c = rest.simpleRequest(
                uri,
                sessionKey=self.session_key,
                getargs={'output_mode': 'json'},
                raiseAllErrors=True)

            clear_password = json.loads(c)['entry'][0]['content']['clear_password']

        except Exception as e:
            self.logger.exception(e)
            return False

        return clear_password == api_key

    def get_work(self, worker):
        if not (isinstance(worker, basestring) and worker):
            raise ModularActionQueueBR(
                'Must specify a worker in order to get work')

        if not self.session_key:
            raise AuthorizationFailed

        # get cam_queue
        uri = '{0}?query={1}'.format(
            self.CAM_QUEUE_URI,
            # quote_plus usage intentional here
            quote_plus(json.dumps({'worker': worker}))
        )

        try:
            r, c = rest.simpleRequest(
                uri,
                sessionKey=self.session_key,
                method='GET'
            )
        except Exception as e:
            self.logger.exception(e)
            raise ModularActionQueueISE(
                'Unable to retrieve cam_queue')

        if r.status != http_client.OK:
            self.logger.error(c)
            raise ModularActionQueueISE(
                'Unable to retrieve cam_queue')

        return json.loads(c)

    def get_results(self, key):
        if not (isinstance(key, basestring) and key):
            raise ModularActionQueueBR(
                'Must specify a key in order to get results')

        if not self.session_key:
            raise AuthorizationFailed

        # get cam_queue
        uri = '{0}/{1}'.format(
            self.CAM_QUEUE_URI,
            quote(key, safe='')
        )

        try:
            r, c = rest.simpleRequest(
                uri,
                sessionKey=self.session_key,
                method='GET'
            )
        except Exception as e:
            self.logger.exception(e)
            raise ModularActionQueueISE(
                'Unable to retrieve cam_queue')

        if r.status != http_client.OK:
            self.logger.error(c)
            raise ModularActionQueueISE(
                'Unable to retrieve cam_queue')

        settings = json.loads(c).get('settings')
        # normalize path
        results_file = os.path.normpath(
            json.loads(settings).get('results_file', ''))
        # verify path
        if not results_file.startswith(
                make_splunkhome_path(
                    ['var', 'run', 'splunk', 'dispatch'])):
            self.logger.error(
                'Unable to load results_file: %s', results_file)
            raise ModularActionQueueISE(
                'Unable to load results_file')

        # read-binary usage intentional here
        with open(results_file, 'rb') as fh:
            return base64.b64encode(fh.read()).decode('utf-8')

    def validate_queue_payload(self, payload, max_items):
        jsonargs = self.validate_payload(payload)

        if len(jsonargs) > max_items:
            raise ModularActionQueueBR('Payload must not exceed max_items')

        for i, jsonitem in enumerate(jsonargs):
            if not isinstance(jsonitem, dict):
                raise ModularActionQueueBR(
                    'Payload items must be valid dictionaries')

            jsonkeys = sorted(jsonitem.keys())

            if not self.REQUIRED_KEYS == jsonkeys:
                raise ModularActionQueueBR(
                    'Payload items must only contain keys: {0}'.format(
                        self.REQUIRED_KEYS))

            for key, val in jsonitem.items():
                exp, reason = self.QUEUE_PAYLOAD_MAP[key]

                if not exp(val):
                    raise ModularActionQueueBR(
                        'Payload item "{0}" was invalidated: {1}'.format(
                            key, reason))

            # build and add _key
            jsonargs[i]['_key'] = self.build_key(jsonitem)

        return jsonargs

    def validate_dequeue_payload(self, payload, worker):
        jsonargs = self.validate_payload(payload)

        for jsonitem in jsonargs:
            if not isinstance(jsonitem, basestring):
                raise ModularActionQueueBR(
                    'Payload items must be valid strings')

            if not jsonitem.startswith('{0}@@'.format(worker)):
                raise ModularActionQueueBR(
                    'Payload item must pertain to authenticated worker')

    def save_work(self, save_sids):
        if not self.session_key:
            raise AuthorizationFailed

        for save_sid in save_sids:
            try:
                rest.simpleRequest(
                    'search/jobs/{0}/control'.format(
                        quote(save_sid, safe='')),
                    postargs={'action': 'save'},
                    sessionKey=self.session_key,
                    raiseAllErrors=True
                )

                self.logger.info(
                    'Successfully saved job: %s', save_sid)
            except Exception as e:
                self.logger.exception(e)
                self.logger.warn(
                    'Unable to save job: %s', save_sid)

    def unsave_work(self, query):
        if not self.session_key:
            raise AuthorizationFailed

        # get cam_queue
        uri = '{0}?query={1}'.format(
            self.CAM_QUEUE_URI,
            # quote_plus usage intentional here
            quote_plus(json.dumps(query))
        )

        try:
            r, c = rest.simpleRequest(
                uri,
                sessionKey=self.session_key,
                method='GET'
            )
        except Exception as e:
            self.logger.exception(e)
            raise ModularActionQueueISE(
                'Unable to retrieve work from cam_queue')

        if r.status != http_client.OK:
            self.logger.error(c)
            raise ModularActionQueueISE(
                'Unable to retrieve work from cam_queue')

        dequeued_items = json.loads(c)

        if not dequeued_items:
            self.logger.warn('No work found; no jobs to unsave')
            return

        sid_query = {
            "$or": [
                {'sid': x.get('sid')}
                for x in dequeued_items
                if x.get('sid')
            ]
        }
        sid_uri = '{0}?query={1}'.format(
            self.CAM_QUEUE_URI,
            # quote_plus usage intentional here
            quote_plus(json.dumps(sid_query))
        )

        try:
            r, c = rest.simpleRequest(
                sid_uri,
                sessionKey=self.session_key,
                method='GET'
            )
        except Exception as e:
            self.logger.exception(e)
            raise ModularActionQueueISE(
                'Unable to retrieve SIDs from cam_queue')

        if r.status != http_client.OK:
            self.logger.error(c)
            raise ModularActionQueueISE(
                'Unable to retrieve SIDs from cam_queue')

        sid_items = json.loads(c)

        if not sid_items:
            self.logger.error('No SIDs found; no jobs to unsave')
            return

        # figure out if sids have any keys not in work keys
        unsave_sids = self.get_unsave_sids(
            dequeued_items, sid_items)

        for unsave_sid in unsave_sids:
            try:
                rest.simpleRequest(
                    'search/jobs/{0}/control'.format(
                        quote(unsave_sid, safe='')),
                    postargs={'action': 'unsave'},
                    sessionKey=self.session_key,
                    raiseAllErrors=True
                )

                self.logger.info(
                    'Successfully unsaved job: %s', unsave_sid)
            except Exception as e:
                self.logger.exception(e)
                self.logger.warn(
                    'Unable to unsave job: %s', unsave_sid)

    def delete_work(self, query):
        if not self.session_key:
            raise AuthorizationFailed

        # get cam_queue
        uri = '{0}?query={1}'.format(
            self.CAM_QUEUE_URI,
            # quote_plus usage intentional here
            quote_plus(json.dumps(query))
        )

        try:
            r, c = rest.simpleRequest(
                uri,
                sessionKey=self.session_key,
                method='DELETE'
            )

            return {
                'status': r.status,
                'payload': c.decode('utf-8')
            }

        except Exception as e:
            self.logger.exception(e)
            raise ModularActionQueueISE('Unable to dequeue item(s)')
