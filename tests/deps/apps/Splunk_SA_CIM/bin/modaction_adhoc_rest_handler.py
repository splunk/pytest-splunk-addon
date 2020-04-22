try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
import json
import operator
import re
import splunk
import splunk.auth
import splunk.rest
import splunk.util
import sys

try:
    from urllib.request import quote
except ImportError:
    from urllib import quote
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication
from time import gmtime

sys.path.append(make_splunkhome_path(['etc', 'apps', 'Splunk_SA_CIM', 'lib']))
from splunk_sa_cim.log import setup_logger

logger = setup_logger('modaction_adhoc_rest_handler')


class ModularActionAdhocException(Exception):
    """Custom exception for Modular Action Adhoc REST handler"""
    pass


class ModularActionAdhocRestHandler(PersistentServerConnectionApplication):
    """REST handler for dispatching modular actions in ad-hoc mode."""
    ALERT_ACTIONS_URI = '/services/alerts/alert_actions/%s'

    PARAM_ACTION_NAME = 'action_name'
    TOKENS_EXPECTED = (
        'action_name',
        '_time',
        'source',
        'indexer_guid',
        'event_hash')
    TOKENS_TRIGGER_TIME = ('trigger_time',)
    TOKENS_RANDOM = ('#random',)
    TOKENS_UNAVAILABLE = ('name_hash',)
    TOKENS_UNAVAILABLE_KV = ('results.file', 'results.url', 'name')

    # Simple regular expression for finding tokens in search commands.
    TEMPLATE_REGEX = re.compile(r'''\$([\w.*#\- ]+)(?:\{([^}]+)\})?\$''')

    # key=value replacement
    TEMPLATE_REGEX_KV = re.compile(r"""
        ('?              # Optional opening single quotation mark
        [A-Za-z0-9_.-]+  # A word representing a Splunk field name
        '?)              # Optional closing single quotation mark
        \s*              # Optional whitespace
        =                # Required equals character
        \s*              # Optional whitespace
        "?               # Optional opening double quotation mark
        \$               # Required opening dollar sign indicating Splunk string substitution
        ([\w.*#\- ]+)    # A word representing a string substitution
        (?:\{([^}]+)\})? # A complex value substitution
        \$               # Required closing dollar sign.
        "?               # Optional closing double quotation mark
        """, re.X)

    PARAM_TEMPLATE = "action.%s."

    def __init__(self, command_line, command_arg):
        super(ModularActionAdhocRestHandler, self).__init__()

    @classmethod
    def get_action(cls, action, session_key):
        """Retrieve an alert action configuration via REST.
        Only alert actions that use sendalert are valid for adhoc invocations.

        :param action: An alert action name.
        :type action: str
        :param session_key: A Splunk session key.
        :type session_key: str

        :return A dictionary representing the alert action configuration,
                retrieved from REST.
        :rtype dict
        """

        getargs = {'output_mode': 'json', 'count': 0}
        unused_response, content = splunk.rest.simpleRequest(
            cls.ALERT_ACTIONS_URI % action,
            getargs=getargs,
            sessionKey=session_key)
        parsed_content = json.loads(content)['entry'][0]['content']

        # param._cam is a JSON string in its own right.
        cam_params = json.loads(
            parsed_content.get('param._cam', '{}'))

        if splunk.util.normalizeBoolean(
                cam_params.get('supports_adhoc', False)):
            return parsed_content
        else:
            raise ModularActionAdhocException(
                'Alert action does not support adhoc invocation.')

    @classmethod
    def replace_tokens(cls, inputstr, tokens, replacement='', kv=False):
        """Replace a token in a search.

        :param inputstr: A Splunk search string.
        :type inputstr: str
        :param tokens: A list of tokens to be substituted.
        :type tokens: list(str)
        :param replacement: A replacement string.
        :type replacement: str
        :param kv: A Boolean governing the behavior of the token replacement
                   on key=value pairs (see below)
        :type kv: bool

        :return A Splunk search string with tokens replaced.
        :rtype str

        Two replacement modes are provided based on
        the value of the "kv" Boolean:

        If kv==True, tokens in this form are REMOVED ENTIRELY from the string.
        This is used to scrub key=value pairs from a search string when the
        subject of the replacement is unavailable.

        Whitespace around the equals sign is permitted
        in this replacement mode.

            <field>="$token$"
            '<field>'="$token$"
            <field>=$token$
            '<field>'=$token$

        If kv==False, tokens in this form are merely replaced:

            $token$
            '$token$'
            "$token$"

        Only the token itself is replaced in this mode;
        leading and trailing quotes are unaltered.
        """
        # idx is the index of the replacement group that must match the token.
        rx, idx = (cls.TEMPLATE_REGEX_KV, 1) if kv else (cls.TEMPLATE_REGEX, 0)

        rv = inputstr
        # Tokens are replaced in reverse order to avoid recalculating indexes.
        for match_obj in reversed(list(rx.finditer(inputstr))):
            if match_obj.groups()[idx] in tokens:
                rv = rv[:match_obj.start()] + str(replacement) + rv[match_obj.end():]
        return rv

    @classmethod
    def replace_standard_tokens(cls, inputstr):
        """Replace tokens that are either always unavailable or
        that have a constant value when a modular action is
        executed in the ad-hoc context.

        :param inputstr: A Splunk search string.
        :type inputstr: str

        :return A Splunk search string with tokens replaced.
        :rtype str
        """

        tmpstr = inputstr

        # Replace any key-value pairs found that reference these tokens.
        tmpstr = cls.replace_tokens(tmpstr, cls.TOKENS_UNAVAILABLE_KV, kv=True)

        # Replace standalone tokens.
        tmpstr = cls.replace_tokens(tmpstr, cls.TOKENS_UNAVAILABLE)

        # Replace random tokens.
        tmpstr = cls.replace_tokens(tmpstr, cls.TOKENS_RANDOM, '$random$')

        # Replace trigger_time
        tmpstr = cls.replace_tokens(
            tmpstr, cls.TOKENS_TRIGGER_TIME, splunk.util.mktimegm(gmtime()))

        return tmpstr

    @classmethod
    def replace_event_tokens(
            cls,
            inputstr,
            replacement_map,
            substitute_defaults=False):
        """Replace tokens in a search string using data submitted by the user.

        :param inputstr: A Splunk search string.
        :type inputstr: str
        :param replacement_map:
            A dictionary of key=value replacements to be conducted.
        :param substitute_defaults:
            Whether or not do substitute tokens with defaults specified.
            For instance, $action.<action_name>.<action_param>{default=""}$
        :type substitute_defaults: bool

        :return A tuple (search, unused_token_dict) representing:
            - a Splunk search string with tokens replaced
            - any unused tokens.
        :rtype tuple(str, dict)
        """

        rv = inputstr
        unused = {}
        default_re = re.compile(r'^default\s*=\s*(.+)$')

        for k, v in replacement_map.items():
            tmp = cls.replace_tokens(rv, [k], v)
            if tmp == rv:
                unused[k] = v
            else:
                rv = tmp

        # substitute defaults
        if substitute_defaults:
            for match_obj in reversed(list(cls.TEMPLATE_REGEX.finditer(rv))):
                if match_obj.group(2):
                    logger.debug(
                        'Discovered token replacement with default specified: %s',
                        match_obj.groups())
                    default_match = default_re.match(match_obj.group(2))
                    if default_match:
                        replacement = default_match.group(1).strip('"')
                        rv = rv[:match_obj.start()] + replacement + rv[match_obj.end():]

        return rv, unused

    @classmethod
    def quote_value(cls, value):
        """Quote an injected token's value by:

        - enclosing the string in double quotation marks
        - escaping internal double quotation marks

        :param value: A value to be quoted.
        :type value: str

        :return: A properly quoted token.
        :rtype: str
        """
        return '"%s"' % value.strip('"').replace('"', r'\"')

    @classmethod
    def inject_tokens(cls, action_name, inputstr, inject_map):
        """Inject tokens received from user input into
        the sendalert clause of the search string.

        If a token is already present in the sendalert clause,
        it will NOT be re-inserted, since that would cause duplicate arguments
        to be passed to the "sendalert" command.

        :param action_name: The modular action name.
        :type action_name: str
        :param inputstr:
            A string representing a Splunk search,
            which is expected to contain "sendalert".
        :type inputstr: str
        :param inject_map:
            A dictionary containing key=value token pairs to be injected.
        :type inject_map: dict

        :return A Splunk search string with tokens injected.
        :rtype str
        """

        param_template = cls.PARAM_TEMPLATE % action_name

        # CIM-731: permit sendalert pipelines with arbitrary action names
        clause_rx = re.compile(
            r"sendalert\s+(?P<action_name>[\w-]+)\s*(?P<args>[^|]*)(?:\||\s*$)")

        tokens = {}
        for k, v in inject_map.items():
            tokens[k.replace(param_template, '')] = v

        token_rx = re.compile(r'(%s)\s*=' % '|'.join(tokens.keys()))

        clause_match = clause_rx.search(inputstr)

        if clause_match:
            # Find the param.* tokens in the command arguments
            token_str = clause_match.groupdict()['args']
            token_matches = token_rx.findall(token_str)

            cleaned_inject_map = {
                k: v
                for k, v in tokens.items()
                if k not in token_matches
            }
            inject_str = " ".join([
                k + "=" + cls.quote_value(cleaned_inject_map[k])
                for k in sorted(cleaned_inject_map)
            ])

            if inject_str:
                components = (
                    i for i in [
                        inputstr[0:clause_match.span(1)[1]].strip(),
                        inject_str,
                        inputstr[clause_match.span(1)[1]:].strip()
                    ]
                    if i != '')
                return " ".join(components)
            else:
                return inputstr
        else:
            # Should never get here.
            raise ModularActionAdhocException(
                'Mismatch between modular action name and sendalert clause.')

    @classmethod
    def get_default_replacements(cls, action_name, action_contents):
        """Return alert action parameters derived from REST,
        in the action.<action_name>.<param_name> format
        suitable for use in token substitution.

        :param action_name: A modular action name.
        :type action_name: str
        :param action_contents: A dictionary of alert action contents.
        :type action_contents: dict

        :return A dictionary of key=value pairs
        :rtype dict
        """

        v_params = {}
        param_template = cls.PARAM_TEMPLATE % action_name

        # Get only the valid modular alert-style parameters
        for k, v in action_contents.items():
            if k != 'name' and str(v):
                v_params[param_template + k] = v

        return v_params

    @classmethod
    def get_user_replacements(cls, action_name, action_contents, replacements):
        """Return the valid k=v replacements derived from user input,
        in the action.<action_name>.<param_name>
        format suitable for use in token substitution.

        :param action_name: A modular action name.
        :type action_name: str
        :param action_contents: A dictionary of alert action contents.
        :type action_contents: dict
        :param replacements:
            A dictionary of key-value substitutions requested by the user.
        :type replacements: dict

        :return A dictionary of key=value pairs
        :rtype dict
        """

        v_params = {}
        param_template = cls.PARAM_TEMPLATE % action_name

        logger.debug('param_template: %s', param_template)
        logger.debug('action_contents: %s', action_contents)
        logger.debug('replacements: %s', replacements)

        # Get only the valid modular alert-style parameters for the alert action
        for k, v in replacements.items():
            if (k.startswith(param_template)
                    and k.replace(param_template, '') in action_contents):
                v_params[k] = v
            elif k == 'action_name':
                v_params[k] = v
            else:
                raise ModularActionAdhocException(
                    'Invalid parameter for adhoc modular action.')

        return v_params

    @staticmethod
    def error(msg, status):
        """
        Return error.

        :param msg: A message describing the problem (a string)
        :type msg: str
        :param status: An integer to be returned as the HTTP status code.
        :type status: int
        """
        logger.error(msg)
        return {'status': status, 'payload': msg}

    def build_command(self, action_name, token_map, session_key):
        """Return a modular action search command string valid for adhoc execution,
        performing token substitution on the command.

        :param action_name: Name of the alert action.
        :type action_name: str
        :param token_map: A dictionary of k=v string replacements to be conducted.
        :type token_map: dict
        :param session_key: A Splunk session key
        :type session_key: str

        Parameters that can be substituted in the alert action command are identifiable via $token$ substitution strings:

            MODALERT format (this uses the normal naming scheme):
                $action.<action_name>.param.<parameter_name>$

                Example: $action.risk.param.index$

            LEGACY format:
                $action.<action_name>.<parameter_name>$

                Example: $action.risk._risk_object$

        Values for these parameters can be derived from user input, OR from default values defined in alert_actions.conf.

        1. SUBSTITUTIONS VIA USER INPUT

            Token substitutions provided by the user will be in the token_map argument to this function. When a value
            is derived from user input, the name is expected to be in MODALERT format, e.g.:

                token_map = {'action.risk.param._risk_score': '100'}

        2. DEFAULT SUBSTITUTIONS

        Token substitutions for which the user has provided no value must be performed using values retrieved from the
        alert_actions.conf configuration for the modular action. However, parameter names in alert_actions.conf drop the
        "action.action_name" prefix. Thus when a value is derived from alert_actions.conf, it must be mapped as
        shown to complete the substitution:

          Modular alert format:

              param.<parameter_name> in alert_actions.conf --> replaces token $action.<action_name>.<parameter_name>$

          Legacy format (only applicable to certain alert actions such as "risk"):

              <parameter_name> in alert_actions.conf --> replaces token $action.<action_name>.<parameter_name>$

          Inline format:
              <default_value> replaces token $action.<action_name>.<parameter_name>{default=<default_value>}$

        """

        # Get the alert action contents. May raise ModularActionAdhocException.
        action_contents = self.get_action(action_name, session_key)

        # Perform standard token replacements for any values
        # that are never present in an adhoc invocation (e.g., "name_hash")
        command = self.replace_standard_tokens(
            action_contents['command'])

        # Validate the user-provided replacement strings.
        # May raise ModularActionAdhocException.
        user_replacements = self.get_user_replacements(
            action_name, action_contents, token_map)

        # Obtain the default alert action parameters.
        default_replacements = self.get_default_replacements(
            action_name, action_contents)

        # Substitute tokens using user input (unused replacements don't matter)
        command, _ = self.replace_event_tokens(
            command, user_replacements)

        # Substitute tokens using default values
        # (unused replacements don't matter)
        command, _ = self.replace_event_tokens(
            command, default_replacements, substitute_defaults=True)

        # Inject unused key=value pairs in the query_args that are NOT substituted into the alert action's "command"
        # parameter directly following the alert action name (e.g., "sendalert risk <injected tokens>".
        # Parameters already present in the sendalert string will not be duplicated.
        # Note: token injection is only performed for commands that use sendalert.
        if "sendalert" in command:
            command = self.inject_tokens(
                action_name, command, user_replacements)

        return command

    # Search utility commands
    @staticmethod
    def _normalize_search(search, alert_cmd):
        """Normalize a search for parse or dispatch.

        :param search: A search to be prefixed to the final search.
        :type search: str
        :param alert_cmd:
            An alert action command string,
            with all token substitutions already performed.
        :type alert_cmd: str

        :return The normalized search string
        :rtype str
        """

        if not search.lstrip().startswith(("|", "search")):
            search = "search " + search.lstrip()

        return search.strip() + " | " + alert_cmd

    @staticmethod
    def _parse_search(search, session_key):
        """Trivially attempt to parse a search command before dispatching.

        :param search: A search to be prefixed to the final search.
        :type search: str
        :param session_key: A Splunk session key.
        :type session_key: str

        :return True if the search parsed, else ModularActionAdhocException
        :rtype bool
        :raises ModularActionAdhocException

        Note: We intentionally avoid the similar
        splunk.search.Parser.parseSearch() method
        because of the excessive number of imports used in that library.

        """
        args = {
            'output_mode': 'json',
            'parse_only': 't',
            'q': search
        }

        r, unused_c = splunk.rest.simpleRequest(
            '/search/parser',
            getargs=args,
            sessionKey=session_key,
            raiseAllErrors=True
        )

        if r.status != 200:
            raise ModularActionAdhocException(
                'Constructed search could not be parsed.')

        return True

    @staticmethod
    def _dispatch_search(search, namespace, owner, session_key, dispatch_args=None):
        """Dispatch a search.

        :param search: A search to be prefixed to the final search.
        :type search: str
        :param session_key: A Splunk session key.
        :type session_key: str

        :return The SID of the dispatched search
        :rtype str

        Note: We specifically avoid the similar splunk.search.dispatch()
        method because of the excessive number of imports used in that library.
        """

        args = {
            'output_mode': 'json',
            'search': search
        }

        if dispatch_args:
            args.update(dispatch_args)

        if namespace and owner:
            uri = '/servicesNS/{0}/{1}/search/jobs'.format(
                quote(owner, safe=''),
                quote(namespace, safe='')
            )
        else:
            uri = 'search/jobs'

        r, c = splunk.rest.simpleRequest(
            uri, postargs=args, sessionKey=session_key, raiseAllErrors=True)

        if r.status != http_client.CREATED:
            logger.debug('JOBS_ENDPOINT_RESPONSE: %s', r)
            logger.debug('JOBS_ENDPOINT_CONTENT: %s', c)
            raise ModularActionAdhocException(
                'Error when dispatching search: status_code="%s"' % r.status)

        return json.loads(c)['sid']

    def handle(self, args):
        """Main function for REST call.

        :param args:
            A JSON string representing a dictionary of arguments to
            the REST call.
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
                return self.error(
                    'Invalid method for this endpoint',
                    http_client.METHOD_NOT_ALLOWED)
        except ModularActionAdhocException as e:
            msg = 'ModularActionException: {0}'.format(e)
            return self.error(msg, http_client.BAD_REQUEST)
        except splunk.RESTException as e:
            return self.error(
                'RESTexception: %s' % e, http_client.INTERNAL_SERVER_ERROR)
        except Exception as e:
            msg = 'Unknown exception: %s' % e
            logger.exception(msg)
            return self.error(msg, http_client.INTERNAL_SERVER_ERROR)

    def handle_post(self, args):
        """Dispatch a modular action in adhoc mode.

        :param args: A dictionary of arguments to the REST call.
        :type args: dict

        :return A valid REST response.
        :rtype dict
        """

        # Retrieve arguments. Everything not popped from form_args is assumed
        # to be a key=value replacement string that will be passed to
        # validate_replacements().
        session_key = args['session']['authtoken']
        post_args = dict(args.pop('form', []))
        action_name = post_args.get('action_name', '')
        search = post_args.pop('search', '')

        # If the handler was invoked with a namespace,
        # both namespace and owner will be used when dispatching search.
        namespace = args.pop('ns', {}).get('app')
        owner = args['session']['user']

        # Earliest and latest used only in dispatching the search,
        # not in any token substitutions.
        valid_dispatch_args = ['earliest_time', 'latest_time']
        dispatch_args = {
            k: post_args.pop(k, None)
            for k in valid_dispatch_args
        }

        if not all([action_name, search, session_key]):
            raise ModularActionAdhocException(
                'Missing parameters for adhoc modular action.')

        if not post_args:
            logger.info(
                'Modular action invoked with no user token replacements.')

        action_cmd = self.build_command(action_name, post_args, session_key)

        # Normalize the search
        finalized_cmd = self._normalize_search(search, action_cmd)
        logger.info("Finalized command: %s", finalized_cmd)

        # Attempt to parse and dispatch the search
        # (may raise ModularActionAdhocException)
        if self._parse_search(finalized_cmd, session_key):
            sid = self._dispatch_search(
                finalized_cmd, namespace, owner, session_key, dispatch_args)

            return {
                'status': http_client.CREATED,
                'payload': {
                    'command': finalized_cmd,
                    'sid': sid,
                }
            }

        else:

            return {
                'status': http_client.BAD_REQUEST,
                'payload': {
                    'command': finalized_cmd,
                }
            }
