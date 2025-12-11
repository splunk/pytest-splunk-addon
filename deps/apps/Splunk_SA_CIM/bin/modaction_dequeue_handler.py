try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
import json
import operator
import sys

from splunk import RESTException
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication

sys.path.append(make_splunkhome_path(['etc', 'apps', 'Splunk_SA_CIM', 'lib']))
from splunk_sa_cim.log import setup_logger
from splunk_sa_cim.modaction_queue import ModularActionQueueBR, ModularActionQueueISE, ModularActionQueueUnauth, ModularActionQutils

logger = setup_logger('modaction_queue_handler')


class ModularActionDeQueueHandler(PersistentServerConnectionApplication):
    '''REST handler for generating modular action queue api keys.'''

    def __init__(self, command_line, command_arg):
        super(ModularActionDeQueueHandler, self).__init__()

        try:
            self.params = json.loads(command_arg)
        except Exception as e:
            logger.warn(e)
            self.params = {}

        ModularActionQutils.set_log_level(logger, self.params)

        self.modaction_qutils = ModularActionQutils(logger, None)

    def handle(self, args):
        """Main function for REST call.

        :param args: A JSON string representing a dictionary
                     of arguments to the REST call.
        :type args: str

        :return A valid REST response.
        :rtype dict

        - Routing of GET, POST, etc. happens here.
        - All exceptions should be caught here.
        """

        logger.debug('ARGS: %s', args)
        args = json.loads(args)

        try:
            logger.info('Handling %s request.', args['method'])
            method = 'handle_' + args['method'].lower()
            if callable(getattr(self, method, None)):
                return operator.methodcaller(method, args)(self)
            else:
                return self.modaction_qutils.error(
                    'Invalid method for this endpoint',
                    http_client.METHOD_NOT_ALLOWED)
        except ModularActionQueueBR as e:
            msg = 'ModularActionException: {0}'.format(e)
            return self.modaction_qutils.error(
                msg, http_client.BAD_REQUEST)
        except ModularActionQueueUnauth as e:
            msg = 'ModularActionException: {0}'.format(e)
            return self.modaction_qutils.error(
                msg, http_client.UNAUTHORIZED)
        except ModularActionQueueISE as e:
            msg = 'ModularActionException: {0}'.format(e)
            return self.modaction_qutils.error(
                msg, http_client.INTERNAL_SERVER_ERROR)
        except RESTException as e:
            return self.modaction_qutils.error(
                'RESTexception: %s' % e,
                http_client.INTERNAL_SERVER_ERROR)
        except Exception as e:
            msg = 'Unknown exception: %s' % e
            logger.exception(msg)
            return self.modaction_qutils.error(
                msg, http_client.INTERNAL_SERVER_ERROR)

    def handle_post(self, args):
        '''Main function for REST call.

        :param args:
            A JSON string representing a dictionary of arguments
            to the REST call.
        :type args: str

        :return A valid REST response.
        :rtype dict

        - Routing of GET, POST, etc. happens here.
        - All exceptions should be caught here.
        '''
        # validate encryption
        if not self.modaction_qutils.is_connection_encrypted(
                args.get('connection', {})):
            raise ModularActionQueueISE('Unable to validate encryption')

        # headers
        headers = args.get('headers', [])

        # get worker
        worker = self.modaction_qutils.get_header_item(
            headers, 'X-API-ID')

        # get api_key
        api_key = self.modaction_qutils.get_header_item(
            headers, 'X-API-KEY')

        # get system key
        self.modaction_qutils.session_key = args.get(
            'system_authtoken', None)

        # validate api key
        if not self.modaction_qutils.is_api_key_valid(
                worker, api_key):
            raise ModularActionQueueUnauth(
                'Unable to validate X-API information')

        # validate payload
        payload = args.get('payload', '')
        self.modaction_qutils.validate_dequeue_payload(payload, worker)

        # get query
        query = {"$or": [{'_key': x} for x in json.loads(payload)]}
        logger.debug(query)

        # unsave
        try:
            self.modaction_qutils.unsave_work(query)
        except Exception as e:
            logger.exception(e)
            logger.warn('Unable to unsave work')

        # delete
        return self.modaction_qutils.delete_work(query)
