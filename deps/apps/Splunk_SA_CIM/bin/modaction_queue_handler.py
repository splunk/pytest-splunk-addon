try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
import json
import operator
import splunk.rest as rest
import sys

from splunk import RESTException
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication

sys.path.append(make_splunkhome_path(['etc', 'apps', 'Splunk_SA_CIM', 'lib']))
from splunk_sa_cim.log import setup_logger
from splunk_sa_cim.modaction_queue import ModularActionQueueBR, ModularActionQueueISE, ModularActionQueueUnauth, ModularActionQutils


logger = setup_logger('modaction_queue_handler')


class ModularActionQueueHandler(PersistentServerConnectionApplication):
    '''REST handler for generating modular action queue api keys.'''
    DEFAULT_MAX_ITEMS = 10

    def __init__(self, command_line, command_arg):
        super(ModularActionQueueHandler, self).__init__()

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

        # get max items
        max_items = self.params.get('max_items')

        if not (isinstance(max_items, int) and max_items > 0):
            max_items = self.DEFAULT_MAX_ITEMS

        # get system key
        self.modaction_qutils.session_key = args.get(
            'system_authtoken', None)

        # validate payload
        payload = args.get('payload', '')
        jsonargs = self.modaction_qutils.validate_queue_payload(
            payload, max_items)

        # get sid list
        sids = [jsonitem['sid'] for jsonitem in jsonargs]

        # save
        try:
            self.modaction_qutils.save_work(sids)
        except Exception as e:
            logger.exception(e)
            logger.warn('Unable to save work')

        # system key
        system_key = args.get('system_authtoken', None)

        # post
        batch_save_uri = '/servicesNS/nobody/Splunk_SA_CIM/storage/collections/data/cam_queue/batch_save'

        try:
            r, c = rest.simpleRequest(
                batch_save_uri,
                sessionKey=system_key,
                jsonargs=json.dumps(jsonargs)
            )

            return {
                'status': r.status,
                'payload': c.decode('utf-8')
            }

        except Exception as e:
            logger.exception(e)
            raise ModularActionQueueISE('Unable to queue item(s)')
