#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
Meta
====
    $Id$
    $DateTime$
    $Author$
    $Change$
"""

from future import standard_library

standard_library.install_aliases()
from builtins import object
import urllib.request, urllib.parse, urllib.error
import datetime
import time

TIMEOUT = 60
POLL_FREQUENCY = 0.5


class TimeoutException(Exception):
    """
    Simple timeout exception
    """

    pass


class RESTInPeace(object):
    """
    Simple module to wrap REST endpoints into a consistent set of methods
    Everything is accessed through servicesNS.
    """

    # Please keep the key in singular form.
    URIS = {
        "alert_action": "/servicesNS/{u}/{a}/admin/alert_actions",
        "app": "/servicesNS/{u}/{a}/apps",
        "app_template": "/servicesNS/{u}/{a}/apps/apptemplates",
        "app_local": "/servicesNS/{u}/{a}/apps/local",
        "app_install": "/servicesNS/{u}/{a}/apps/appinstall",
        "automatic_lookup": "/servicesNS/{u}/{a}/data/props/lookups",
        "calculated_field": "/servicesNS/{u}/{a}/data/props/calcfields",
        "capabilities": "/servicesNS/{u}/{a}/authorization/capabilities",
        "changepassword": "/servicesNS/{u}/{a}/authentication/changepassword",
        "cluster_config": "/servicesNS/{u}/{a}/cluster/config",
        "cluster_master": "/servicesNS/{u}/{a}/cluster/master",
        "cluster_searchhead": "/servicesNS/{u}/{a}/cluster/searchhead",
        "cluster_slave": "/servicesNS/{u}/{a}/cluster/slave",
        "config": "/servicesNS/{u}/{a}/configs",
        "conf_event_renderer": ("/servicesNS/{u}/{a}/configs/conf-event_renderers"),
        "conf_saved_searches": "/servicesNS/{u}/{a}/configs/conf-savedsearches",
        "datamodel": "/servicesNS/{u}/{a}/datamodel/model",
        "datamodel_acceleration": "/servicesNS/{u}/{a}/datamodel/acceleration",
        "datamodel_report": "/servicesNS/{u}/{a}/datamodel/report",
        "deployment_client_config": ("/servicesNS/{u}/{a}/deployment/client/config"),
        "deployment_server_class": (
            "/servicesNS/{u}/{a}/deployment/server/serverclasses"
        ),
        "deployment_server_config": ("/servicesNS/{u}/{a}/deployment/server/config"),
        "deployment_server_client": ("/servicesNS/{u}/{a}/deployment/server/clients"),
        "deployment_server_application": (
            "/servicesNS/{u}/{a}/deployment/server/applications"
        ),
        "distsearch_peer": "/servicesNS/{u}/{a}/search/distributed/peers",
        "eventtype": "/servicesNS/{u}/{a}/saved/eventtypes",
        "fired_alert": "/servicesNS/{u}/{a}/alerts/fired_alerts",
        "field": "/servicesNS/{u}/{a}/search/fields",
        "field_alias": "/servicesNS/{u}/{a}/data/props/fieldaliases",
        "field_extraction": "/servicesNS/{u}/{a}/data/props/extractions",
        "fvtag": "/servicesNS/{u}/{a}/saved/fvtags",
        "httpauth_token": "/servicesNS/{u}/{a}/authentication/httpauth-tokens",
        "index": "/servicesNS/{u}/{a}/data/indexes",
        "input": "/servicesNS/{u}/{a}/data/inputs",
        "input_monitor": "/servicesNS/{u}/{a}/data/inputs/monitor",
        "input_oneshot": "/servicesNS/{u}/{a}/data/inputs/oneshot",
        "input_script": "/servicesNS/{u}/{a}/data/inputs/script",
        "input_tcp_cooked": "/servicesNS/{u}/{a}/data/inputs/tcp/cooked",
        "input_tcp_raw": "/servicesNS/{u}/{a}/data/inputs/tcp/raw",
        "input_udp": "/servicesNS/{u}/{a}/data/inputs/udp",
        "input_eventlog": ("/servicesNS/{u}/{a}/data/inputs/win-event-log-collections"),
        "input_regmon": "/servicesNS/{u}/{a}/data/inputs/WinRegMon",
        "input_perfmon": "/servicesNS/{u}/{a}/data/inputs/win-perfmon",
        "input_hostmon": "/servicesNS/{u}/{a}/data/inputs/WinHostMon",
        "input_netmon": "/servicesNS/{u}/{a}/data/inputs/WinNetMon",
        "input_admon": "/servicesNS/{u}/{a}/data/inputs/ad",
        "input_printmon": "/servicesNS/{u}/{a}/data/inputs/WinPrintMon",
        "job": "/servicesNS/{u}/{a}/search/jobs",
        "ldap_strategy": "/servicesNS/{u}/{a}/authentication/providers/LDAP",
        "license": "/servicesNS/{u}/{a}/licenser/licenses",
        "licenser": "/servicesNS/{u}/{a}/licenser",
        "licenser_group": "/servicesNS/{u}/{a}/licenser/groups",
        "lookup": "/servicesNS/{u}/{a}/data/props/lookups",
        "lookup_table_file": "/servicesNS/{u}/{a}/data/lookup-table-files",
        "macro": "/servicesNS/{u}/{a}/admin/macros",
        "message": "/servicesNS/{u}/{a}/messages",
        "navigation": "/servicesNS/{u}/{a}/data/ui/nav",
        "ntag": "/servicesNS/{u}/{a}/saved/ntags",
        "panel": "/servicesNS/{u}/{a}/data/ui/panels",
        "property": "/servicesNS/{u}/{a}/properties",
        "role": "/servicesNS/{u}/{a}/authorization/roles",
        # only simple and stream available, and only edit method works.
        "receiver": "/services/receivers",
        "saved_search": "/servicesNS/{u}/{a}/saved/searches",
        "scheduled_view": "/servicesNS/{u}/{a}/scheduled/views",
        "search_command": "/servicesNS/{u}/{a}/admin/commandsconf",
        "search_head_cluster": "/servicesNS/{u}/{a}/shcluster",
        "server": "/servicesNS/{u}/{a}/server",
        "sourcetype": "/servicesNS/{u}/{a}/saved/sourcetypes",
        "sourcetype_rename": "/servicesNS/{u}/{a}/saved/sourcetype-rename",
        "tag": "/servicesNS/{u}/{a}/search/tags",
        "tcp_output_group": "/servicesNS/{u}/{a}/data/outputs/tcp/group",
        "time": "/servicesNS/{u}/{a}/data/ui/times",
        "transforms_extraction": ("/servicesNS/{u}/{a}/data/transforms/extractions"),
        "transforms_lookup": "/servicesNS/{u}/{a}/data/transforms/lookups",
        "transparent_summarization": "/servicesNS/{u}/{a}/admin/summarization",
        "user": "/servicesNS/{u}/{a}/authentication/users",
        "ui_manager": "/servicesNS/{u}/{a}/data/ui/manager",
        "ui_pref": "/servicesNS/{u}/{a}/data/ui/prefs",
        "ui_tour": "/servicesNS/{u}/{a}/data/ui/ui-tour",
        "user_pref": "/servicesNS/{u}/{a}/admin/user-prefs",
        "view": "/servicesNS/{u}/{a}/data/ui/views",
        "viewstate": "/servicesNS/{u}/{a}/data/ui/viewstates",
        "vix_index": "/servicesNS/{u}/{a}/data/vix-indexes",
        "vix_provider": "/servicesNS/{u}/{a}/data/vix-providers",
        "workflow_action": "/servicesNS/{u}/{a}/data/ui/workflow-actions",
    }

    # This list contains function-like URIs.
    # Please keep the key in singular form.
    FUNCTION_URIS = {
        "generate_regex": "/servicesNS/{u}/{a}/field_extractor/generate_regex",
    }

    SUCCESS = {"GET": "200", "POST": "201", "DELETE": "200"}

    def __init__(self, helmut_rest_connector, user_namespace=None, app_namespace=None):
        """
        Pass in a logged-in helmut rest connector. Every call afterwards
        will use this connector. Namespaces should be encapsulated inside
        the connector.
        """

        self.conn = helmut_rest_connector

        if user_namespace is not None and app_namespace is not None:
            self._user = user_namespace
            self._app = app_namespace
        else:
            self._user, self._app = self.conn.namespace.strip("/").split("/")

        self.change_namespace(self._user, self._app)

    def change_namespace(self, user, app):
        """
        Change the user/app namespace for all the rest calls.
        Note: This does NOT change the user making the rest calls.

        @rtype user: string
        @param user: username

        @rtype app: string
        @param app: app id
        """
        self._user = urllib.parse.quote(user, "")
        self._app = app

        for uri_name, uri_value in list(self.URIS.items()):
            final_uri_value = uri_value.format(u=self._user, a=self._app)
            self.add_endpoint(uri_name, final_uri_value)
        for uri_name, uri_value in list(self.FUNCTION_URIS.items()):
            final_uri_value = uri_value.format(u=self._user, a=self._app)
            self.add_function_endpoint(uri_name, final_uri_value)

    def add_endpoint(self, uri_name, uri_value):
        """
        Creates generic create, edit, delete, check methods for the
        given endpoint name and value.

        @type uri_name: string
        @param uri_name: the name of the endpoint

        @type uri_value: string
        @param uri_name: the uri for the endpoint
        """

        def gen_create(*args, **kwargs):
            """
            Create
            """
            if args:
                if kwargs:
                    args = args[0] + list(kwargs.items())
                body = args
            else:
                body = kwargs

            return self.conn.make_request("POST", uri_value, body=body)

        gen_create.__doc__ = """
            Create method for the '{ep}' endpoint.
            - uri: '{uri}'

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_create.__name__ = "create_{ep}".format(ep=uri_name)
        setattr(self, gen_create.__name__, gen_create)

        def gen_get(id_name, sub_endpoint="", *args, **kwargs):
            """
            Get
            """
            uri = "{uri}/{id}{sub_ep}".format(
                uri=uri_value,
                id=urllib.parse.quote(id_name, safe=""),
                sub_ep=(
                    sub_endpoint
                    if (sub_endpoint == "" or sub_endpoint.startswith("/"))
                    else "/{s}".format(s=sub_endpoint)
                ),
            )
            return self.conn.make_request("GET", uri, args, kwargs)

        gen_get.__doc__ = """
            Get method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @type sub_endpoint: string
            @param sub_endpoint: child endpoint of the base endpoint

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_get.__name__ = "get_{ep}".format(ep=uri_name)
        setattr(self, gen_get.__name__, gen_get)

        def gen_reload(*args, **kwargs):
            """
            Get
            """
            uri = "{uri}/_reload".format(uri=uri_value)
            return self.conn.make_request("GET", uri, args, kwargs)

        gen_reload.__doc__ = """
            Reload method for the '{ep}' endpoint.
            - uri: '{uri}/_reload'
            - uses the '_reload' endpoint off the base endpoing regardless
              of the object.

            Note: NOT all REST endpoints support this, please check your endpoint
                  before attempting to do this.

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_reload.__name__ = "reload_{ep}".format(ep=uri_name)
        setattr(self, gen_reload.__name__, gen_reload)

        def gen_get_all(*args, **kwargs):
            """
            Get
            """
            return self.conn.make_request("GET", uri_value, args, kwargs)

        gen_get_all.__doc__ = """
            Get all method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_get_all.__name__ = "get_all_{ep}".format(ep=uri_name)
        setattr(self, gen_get_all.__name__, gen_get_all)

        def gen_edit(id_name, sub_endpoint="", urlparam=None, *args, **kwargs):
            """
            Edit
            """
            if args:
                if kwargs:
                    args = args[0] + list(kwargs.items())
                body = args
            else:
                body = kwargs

            uri = "{uri}/{id}{sub_ep}".format(
                uri=uri_value,
                id=urllib.parse.quote(id_name, safe=""),
                sub_ep=(
                    sub_endpoint
                    if (sub_endpoint == "" or sub_endpoint.startswith("/"))
                    else "/{s}".format(s=sub_endpoint)
                ),
            )

            return self.conn.make_request("POST", uri=uri, urlparam=urlparam, body=body)

        gen_edit.__doc__ = """
            Edit method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @type sub_endpoint: string
            @param sub_endpoint: child endpoint of the base endpoint

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_edit.__name__ = "edit_{ep}".format(ep=uri_name)
        setattr(self, gen_edit.__name__, gen_edit)

        def gen_delete(id_name, *args, **kwargs):
            """
            Delete
            """
            uri = "{uri}/{id}".format(
                uri=uri_value, id=urllib.parse.quote(id_name, safe="")
            )
            return self.conn.make_request("DELETE", uri, args, kwargs)

        gen_delete.__doc__ = """
            Delete method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_delete.__name__ = "delete_{ep}".format(ep=uri_name)
        setattr(self, gen_delete.__name__, gen_delete)

        def gen_check(id_name, *args, **kwargs):
            """
            Check
            """
            if not id_name:
                # invalid id_name, so we'll return False.
                return False

            if args:
                if kwargs:
                    args = args[0] + list(kwargs.items())
                body = args
            else:
                body = kwargs

            uri = "{uri}/{id}".format(
                uri=uri_value, id=urllib.parse.quote(id_name, safe="")
            )
            response = self.conn.make_request("GET", uri, body=body)[0]
            return response["status"] == self.SUCCESS["GET"]

        gen_check.__doc__ = """
            Check method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @rtype: boolean
            @return: True if the object exists and False otherwise.
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_check.__name__ = "check_{ep}".format(ep=uri_name)
        setattr(self, gen_check.__name__, gen_check)

        def gen_wait_to_be_created(
            id_name, timeout=TIMEOUT, poll_frequency=POLL_FREQUENCY, *args, **kwargs
        ):
            """
            Wait for the specific item to be created.

            @type timeout: int
            @param timeout: the number in second to poll for.

            @type poll_frequency: number
            @param poll_frequency: the number in seconds to wait between
                                   each poll
            """
            if args:
                if kwargs:
                    args = args[0] + list(kwargs.items())
                body = args
            else:
                body = kwargs

            uri = "{uri}/{id}".format(
                uri=uri_value, id=urllib.parse.quote(id_name, safe="")
            )

            start_time = datetime.datetime.now()
            response = self.conn.make_request("GET", uri, body=body)[0]

            while (
                response["status"] != self.SUCCESS["GET"]
                and (datetime.datetime.now() - start_time).seconds < timeout
            ):
                time.sleep(poll_frequency)
                response = self.conn.make_request("GET", uri, body=body)[0]

            if response["status"] != self.SUCCESS["GET"]:
                raise TimeoutException(
                    "The entity '{uri}/{id}' was not found after {t} "
                    "seconds.".format(
                        uri=uri_value,
                        id=urllib.parse.quote(id_name, safe=""),
                        t=timeout,
                    )
                )

        gen_wait_to_be_created.__doc__ = """
            Wait to be created method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @type timeout: int
            @param timeout: the number in second to poll for.

            @type poll_frequency: number
            @param poll_frequency: the number in seconds to wait between
                                   each poll
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_wait_to_be_created.__name__ = "wait_for_{ep}_to_be_created".format(
            ep=uri_name
        )
        setattr(self, gen_wait_to_be_created.__name__, gen_wait_to_be_created)

        def gen_wait_to_be_deleted(
            id_name, timeout=TIMEOUT, poll_frequency=POLL_FREQUENCY, *args, **kwargs
        ):
            """
            Wait for the specific item to be deleted.

            @type timeout: int
            @param timeout: the number in second to poll for.

            @type poll_frequency: number
            @param poll_frequency: the number in seconds to wait between
                                   each poll
            """
            if args:
                if kwargs:
                    args = args[0] + list(kwargs.items())
                body = args
            else:
                body = kwargs

            uri = "{uri}/{id}".format(
                uri=uri_value, id=urllib.parse.quote(id_name, safe="")
            )

            start_time = datetime.datetime.now()
            response = self.conn.make_request("GET", uri, body=body)[0]

            while (
                response["status"] == self.SUCCESS["GET"]
                and (datetime.datetime.now() - start_time).seconds < timeout
            ):
                time.sleep(poll_frequency)
                response = self.conn.make_request("GET", uri, body=body)[0]

            if response["status"] == self.SUCCESS["GET"]:
                raise TimeoutException(
                    "The entity '{uri}/{id}' was still found after {t} "
                    "seconds.".format(
                        uri=uri_value,
                        id=urllib.parse.quote(id_name, safe=""),
                        t=timeout,
                    )
                )

        gen_wait_to_be_deleted.__doc__ = """
            Wait to be deleted method for the '{ep}' endpoint.
            - uri: '{uri}'

            @type id_name: string
            @param: id_name: the id of the object.

            @type timeout: int
            @param timeout: the number in second to poll for.

            @type poll_frequency: number
            @param poll_frequency: the number in seconds to wait between
                                   each poll
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_wait_to_be_deleted.__name__ = "wait_for_{ep}_to_be_deleted".format(
            ep=uri_name
        )
        setattr(self, gen_wait_to_be_deleted.__name__, gen_wait_to_be_deleted)

    def add_function_endpoint(self, uri_name, uri_value):
        """
        Creates generic run methods for the
        given endpoint name and value.

        @type uri_name: string
        @param uri_name: the name of the endpoint

        @type uri_value: string
        @param uri_name: the uri for the endpoint
        """

        def gen_run(sub_endpoint="", *args, **kwargs):
            """
            Acting like calling a function, send GET request
            to the specific endpoint and return value from the make_request.

            @type sub_endpoint: string
            @param sub_endpoint: child endpoint of the base endpoint

            @return: the return value from the make_request on the endpoint
            """
            uri = "{uri}/{sub_ep}".format(
                uri=uri_value,
                sub_ep=(
                    sub_endpoint
                    if (sub_endpoint == "" or sub_endpoint.startswith("/"))
                    else "/{s}".format(s=sub_endpoint)
                ),
            )
            return self.conn.make_request("GET", uri, args, kwargs)

        gen_run.__doc__ = """
            Acting like calling a function, send GET request to the
            '{ep}' endpoint and return value from the make_request.
            - uri: '{uri}'

            @type sub_endpoint: string
            @param sub_endpoint: child endpoint of the base endpoint

            @return: the return value from the make_request on the endpoint
            """.format(
            ep=uri_name, uri=uri_value
        )
        gen_run.__name__ = "run_{ep}".format(ep=uri_name)
        setattr(self, gen_run.__name__, gen_run)
