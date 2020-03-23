from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
import urllib.request, urllib.error, urllib.parse
import logging
import urllib.request, urllib.parse, urllib.error
import threading
import json

import os
from pytest_splunk_addon.helmut.util.Constants import Constants as const
from pytest_splunk_addon.helmut.connector.base import Connector

LOGGER = logging.getLogger("search helper log")


class SearchHelpers(threading.Thread):
    def edit_savedsearch(
        self,
        splunk,
        savedsearchname,
        appcontext="search",
        arguments={"output_mode": "json"},
        request_type="GET",
        acl=None,
        splunk_user="",
        splunk_pwd="",
    ):
        LOGGER.info("Creating edit a saved search")
        if splunk_user == "":
            splunk_user = splunk.username
        if splunk_pwd == "":
            splunk_pwd = splunk.password
        request_url = const.TestConstants["EDIT_SAVED_SEARCH"].format(appcontext)

        if request_type == "POST":
            request_args = arguments

        if request_type == "UPDATE":
            request_type = "POST"
            request_url = request_url + "/" + savedsearchname
            request_args = arguments

        if request_type == "GET" or request_type == "DELETE":
            request_url = request_url + "/" + savedsearchname
            request_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk, request_type, request_url, request_args, splunk_user, splunk_pwd
        )

        if acl != None:
            acl_req_url = request_url + "/" + savedsearchname + "/acl"
            res, cont = self.make_http_request(
                splunk, request_type, acl_req_url, acl, splunk_user, splunk_pwd
            )

        return response, content

    def edit_savedsearch_with_uxt(
        self,
        splunk,
        savedsearchname,
        usercontext="admin",
        appcontext="search",
        arguments={"output_mode": "json"},
        request_type="GET",
        acl=None,
    ):
        """
            usercontext:applicationcontext namespace
        """
        LOGGER.info("Creating edit a saved search")
        request_url = const.TestConstants["EDIT_SAVED_SEARCH_USRCTX"].format(
            usercontext, appcontext
        )

        if request_type == "POST":
            request_args = arguments

        if request_type == "UPDATE":
            request_type = "POST"
            request_url = request_url + "/" + savedsearchname
            request_args = arguments

        if request_type == "GET" or request_type == "DELETE":
            request_url = request_url + "/" + savedsearchname
            request_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            request_url,
            request_args,
            splunk.username,
            splunk.password,
        )

        if acl != None:
            acl_req_url = request_url + "/" + savedsearchname + "/acl"
            res, cont = self.make_http_request(
                splunk, request_type, acl_req_url, acl, splunk.username, splunk.password
            )

        return response, content

    def tag_actions(
        self,
        splunk,
        fieldname,
        fieldvalue,
        tagname,
        tag_action,
        usercontext="admin",
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        """
        creates/edits/deletes a tag
        REST EDNPOINT - search/fields/{field_name}/tags
        """
        tag_url = const.TestConstants["ADD_TAG"].format(appcontext, fieldname)
        tag_value_pair = urllib.parse.quote(
            fieldname + "=" + fieldvalue + " : " + tagname
        )

        # print 'request type is {0}'.format(request_type)

        print(threading.currentThread().getName(), "starting")

        if request_type == "POST":
            tag_args = {"value": fieldvalue, tag_action: tagname}

        if request_type == "GET" or request_type == "DELETE":
            tag_args = {"output_mode": "json"}
            tag_url = (
                const.TestConstants["GET_TAG"].format(appcontext, usercontext)
                + "/"
                + tag_value_pair
            )

        response, content = self.make_http_request(
            splunk, request_type, tag_url, tag_args, splunk.username, splunk.password
        )

        if acl != None:
            tag_acl_url = (
                const.TestConstants["GET_TAG"].format(appcontext, usercontext)
                + "/"
                + tag_value_pair
                + "/acl"
            )
            response, content = self.make_http_request(
                splunk, request_type, tag_acl_url, acl, splunk.username, splunk.password
            )

        return response, content

    def tag_actions_uxt(
        self,
        splunk,
        fieldname,
        fieldvalue,
        tagname,
        tag_action,
        usercontext="admin",
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        """
        creates/edits/deletes a tag
        REST EDNPOINT - search/fields/{field_name}/tags
        """
        tag_url = const.TestConstants["ADD_TAG_USRCXT"].format(
            usercontext, appcontext, fieldname
        )
        tag_value_pair = urllib.parse.quote(
            fieldname + "=" + fieldvalue + " : " + tagname
        )

        # print 'request type is {0}'.format(request_type)

        print(threading.currentThread().getName(), "starting")

        if request_type == "POST":
            tag_args = {"value": fieldvalue, tag_action: tagname}

        if request_type == "GET" or request_type == "DELETE":
            tag_args = {"output_mode": "json"}
            tag_url = (
                const.TestConstants["GET_TAG"].format(appcontext, usercontext)
                + "/"
                + tag_value_pair
            )

        response, content = self.make_http_request(
            splunk, request_type, tag_url, tag_args, splunk.username, splunk.password
        )

        if acl != None:
            tag_acl_url = (
                const.TestConstants["GET_TAG"].format(appcontext, usercontext)
                + "/"
                + tag_value_pair
                + "/acl"
            )
            response, content = self.make_http_request(
                splunk, request_type, tag_acl_url, acl, splunk.username, splunk.password
            )

        return response, content

    def edit_eventtype(
        self,
        splunk,
        eventtypename,
        search,
        appcontext="search",
        request_type="GET",
        splunk_user="admin",
        splunk_pwd="changeme",
        acl=None,
    ):
        """
        """
        LOGGER.info("create new eventtype")

        eventtype_url = const.TestConstants["EDIT_EVENTTYPE"].format(appcontext)
        if request_type == "POST":
            eventtype_args = {"name": eventtypename, "search": search}
            urllib.parse.urlencode(eventtype_args)

        if acl != None:
            eventtype_acl_url = eventtype_url + "/" + eventtypename + "/acl"
            response, content = self.make_http_request(
                splunk, request_type, eventtype_acl_url, acl, splunk_user, splunk_pwd
            )

        if request_type == "GET" or request_type == "DELETE":
            eventtype_args = {"output_mode": "json"}
            eventtype_url = (
                const.TestConstants["EDIT_EVENTTYPE"].format(appcontext)
                + "/"
                + eventtypename
            )

        response, content = self.make_http_request(
            splunk, request_type, eventtype_url, eventtype_args, splunk_user, splunk_pwd
        )
        return response, content

    def edit_field_transform(
        self,
        splunk,
        fieldExtractionName,
        stanza,
        extractiontype,
        fieldtobeExtracted,
        appcontext="search",
        request_type="GET",
        splunk_user="admin",
        splunk_pwd="changeme",
        acl=None,
    ):
        """
        """
        LOGGER.info("create field transform using interactive field extractor")

        ifx_url = const.TestConstants["EDIT_IFX"].format(appcontext)
        fieldextraction = stanza + " : " + extractiontype + "-" + fieldExtractionName

        if request_type == "POST":
            ifx_args = {
                "name": fieldExtractionName,
                "stanza": stanza,
                "type": extractiontype,
                "value": fieldtobeExtracted,
            }

        if request_type == "DELETE" or request_type == "GET":
            ifx_args = {"output_mode": "json"}
            ifx_url = ifx_url + "/" + urllib.parse.quote(fieldextraction)

        response, content = self.make_http_request(
            splunk, request_type, ifx_url, ifx_args, splunk_user, splunk_pwd
        )

        if acl != None:
            ifx_acl_url = ifx_url + "/" + urllib.parse.quote(fieldextraction) + "/acl"
            resp, cont = self.make_http_request(
                splunk, request_type, ifx_acl_url, acl, splunk_user, splunk_pwd
            )

        return response, content

    def edit_field_transform_uxt(
        self,
        splunk,
        fieldExtractionName,
        stanza,
        extractiontype,
        fieldtobeExtracted,
        appcontext="search",
        usercontext="admin",
        request_type="GET",
        splunk_user="admin",
        splunk_pwd="changeme",
        acl=None,
    ):
        """
        """
        LOGGER.info("create field transform using interactive field extractor")

        ifx_url = const.TestConstants["EDIT_IFX_USRCTX"].format(usercontext, appcontext)
        fieldextraction = stanza + " : " + extractiontype + "-" + fieldExtractionName

        if request_type == "POST":
            ifx_args = {
                "name": fieldExtractionName,
                "stanza": stanza,
                "type": extractiontype,
                "value": fieldtobeExtracted,
            }

        if request_type == "DELETE" or request_type == "GET":
            ifx_args = {"output_mode": "json"}
            ifx_url = ifx_url + "/" + urllib.parse.quote(fieldextraction)

        response, content = self.make_http_request(
            splunk, request_type, ifx_url, ifx_args, splunk.username, splunk.password
        )

        if acl != None:
            ifx_acl_url = ifx_url + "/" + urllib.parse.quote(fieldextraction) + "/acl"
            resp, cont = self.make_http_request(
                splunk, request_type, ifx_acl_url, acl, splunk.username, splunk.password
            )

        return response, content

    def edit_sourcetype_rename(
        self,
        splunk,
        oldsourcetypename,
        newsourcetypename,
        appcontext="search",
        request_type="GET",
        splunk_user="admin",
        splunk_pwd="changeme",
        acl=None,
    ):
        """
        """
        source_url = const.TestConstants["SOURCE_TYPE_RENAME"].format(appcontext)

        if request_type == "POST":
            source_args = {"name": oldsourcetypename, "value": newsourcetypename}

        if request_type == "DELETE" or request_type == "GET":
            source_args = {"output_mode": "json"}
            source_url = source_url + "/" + oldsourcetypename

        response, content = self.make_http_request(
            splunk, request_type, source_url, source_args, splunk_user, splunk_pwd
        )

        if acl != None:
            source_acl_url = source_url + "/" + oldsourcetypename + "/acl"
            resp, cont = self.make_http_request(
                splunk, request_type, source_acl_url, acl, splunk_user, splunk_pwd
            )

        return response, content

    # add user context sourcetype rename
    def edit_sourcetype_rename_uxt(
        self,
        splunk,
        oldsourcetypename,
        newsourcetypename,
        appcontext="search",
        usercontext="admin",
        request_type="GET",
        splunk_user="admin",
        splunk_pwd="changeme",
        acl=None,
    ):
        """
        """
        source_url = const.TestConstants["SOURCE_TYPE_RENAME_USRCXT"].format(
            usercontext, appcontext
        )

        if request_type == "POST":
            source_args = {"name": oldsourcetypename, "value": newsourcetypename}

        if request_type == "DELETE" or request_type == "GET":
            source_args = {"output_mode": "json"}
            source_url = source_url + "/" + oldsourcetypename

        response, content = self.make_http_request(
            splunk, request_type, source_url, source_args, splunk_user, splunk_pwd
        )

        if acl != None:
            source_acl_url = source_url + "/" + oldsourcetypename + "/acl"
            resp, cont = self.make_http_request(
                splunk, request_type, source_acl_url, acl, splunk_user, splunk_pwd
            )

        return response, content

    def edit_field_alias(
        self,
        splunk,
        alias_name,
        stanza_name,
        field_name,
        field_alias,
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("create edit field alias")
        alias_url = const.TestConstants["EDIT_FELD_ALIAS"].format(appcontext)
        field_alias_name = urllib.parse.quote(
            stanza_name + " : " + "FIELDALIAS-" + alias_name
        )

        if request_type == "POST":
            field_name = "alias" + "." + field_name
            alias_args = {
                "name": alias_name,
                "stanza": stanza_name,
                field_name: field_alias,
            }

        if request_type == "DELETE" or request_type == "GET":
            alias_url = alias_url + "/" + field_alias_name
            alias_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            alias_url,
            alias_args,
            splunk_user=splunk.username,
            splunk_pwd=splunk.password,
        )

        if acl != None:
            alias_acl_url = alias_url + "/" + field_alias_name + "/acl"
            resp, cont = self.make_http_request(
                splunk,
                request_type,
                alias_acl_url,
                acl,
                splunk_user=splunk.username,
                splunk_pwd=splunk.password,
            )

        return response, content

    def edit_field_alias_uxt(
        self,
        splunk,
        alias_name,
        stanza_name,
        field_name,
        field_alias,
        usercontext="admin",
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("create edit field alias")
        alias_url = const.TestConstants["EDIT_FELD_ALIAS_USRCXT"].format(
            usercontext, appcontext
        )
        field_alias_name = urllib.parse.quote(
            stanza_name + " : " + "FIELDALIAS-" + alias_name
        )

        if request_type == "POST":
            field_name = "alias" + "." + field_name
            alias_args = {
                "name": alias_name,
                "stanza": stanza_name,
                field_name: field_alias,
            }

        if request_type == "DELETE" or request_type == "GET":
            alias_url = alias_url + "/" + field_alias_name
            alias_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            alias_url,
            alias_args,
            splunk_user=splunk.username,
            splunk_pwd=splunk.password,
        )

        if acl != None:
            alias_acl_url = alias_url + "/" + field_alias_name + "/acl"
            resp, cont = self.make_http_request(
                splunk,
                request_type,
                alias_acl_url,
                acl,
                splunk_user=splunk.username,
                splunk_pwd=splunk.password,
            )

        return response, content

    def edit_calc_fields(
        self,
        splunk,
        calc_field_name,
        stanza_name,
        calc_field_value,
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Creates calculcated fields")
        calc_url = const.TestConstants["EDIT_CALC_FIELDS"].format(appcontext)

        derived_cal_field_name = urllib.parse.quote(
            stanza_name + " : " + "EVAL-" + calc_field_name
        )

        if request_type == "POST":
            calc_args = {
                "name": calc_field_name,
                "stanza": stanza_name,
                "value": calc_field_value,
            }

        if request_type == "DELETE" or request_type == "GET":
            calc_url = calc_url + "/" + derived_cal_field_name
            calc_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            calc_url,
            calc_args,
            splunk_user=splunk.username,
            splunk_pwd=splunk.password,
        )

        if acl != None:
            calc_acl_url = calc_url + "/" + derived_cal_field_name + "/acl"
            resp, cont = self.make_http_request(
                splunk,
                request_type,
                calc_acl_url,
                acl,
                splunk.username,
                splunk.password,
            )

        return response, content

    def edit_field_extraction(
        self,
        splunk,
        regex,
        source_key,
        transform_name,
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Creates edits field extractions")
        ext_url = const.TestConstants["EDIT_FIELD_EXTRACTION"].format(appcontext)

        if request_type == "POST":
            ext_args = {
                "REGEX": regex,
                "SOURCE_KEY": source_key,
                "name": transform_name,
            }

        if request_type == "DELETE" or request_type == "GET":
            ext_url = ext_url + "/" + transform_name
            ext_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk, request_type, ext_url, ext_args, splunk.username, splunk.password
        )

        if acl != None:
            ext_acl_url = ext_url + "/" + transform_name + "/" + "acl"
            resp, cont = self.make_http_request(
                splunk, request_type, ext_acl_url, acl, splunk.username, splunk.password
            )

        return response, content

    def edit_field_extraction_uxt(
        self,
        splunk,
        regex,
        source_key,
        transform_name,
        usercontext="admin",
        appcontext="search",
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Creates edits field extractions")
        ext_url = const.TestConstants["EDIT_FIELD_EXTRACTION_USRCXT"].format(
            usercontext, appcontext
        )

        if request_type == "POST":
            ext_args = {
                "REGEX": regex,
                "SOURCE_KEY": source_key,
                "name": transform_name,
            }

        if request_type == "DELETE" or request_type == "GET":
            ext_url = ext_url + "/" + transform_name
            ext_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk, request_type, ext_url, ext_args, splunk.username, splunk.password
        )

        if acl != None:
            ext_acl_url = ext_url + "/" + transform_name + "/" + "acl"
            resp, cont = self.make_http_request(
                splunk, request_type, ext_acl_url, acl, splunk.username, splunk.password
            )

        return response, content

    def edit_dashboard(
        self,
        splunk,
        dashboard_name,
        dashboard_xml,
        appcontext,
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Creates a dashboard")
        dashboard_url = const.TestConstants["EDIT_DASHBOARD"].format(appcontext)

        if request_type == "POST":
            dashboard_args = {"name": dashboard_name, "eai:data": dashboard_xml}

        if request_type == "DELETE" or request_type == "GET":
            dashboard_url = dashboard_url + "/" + dashboard_name
            dashboard_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            dashboard_url,
            dashboard_args,
            splunk.username,
            splunk.password,
        )

        if acl != None:
            dashboard_acl_url = dashboard_url + "/" + dashboard_name
            response, content = self.make_http_request(
                splunk,
                request_type,
                dashboard_acl_url,
                acl,
                splunk.username,
                splunk.password,
            )

        return response, content

    def edit_lookup(
        self,
        splunk,
        lookupfilepath,
        lookupfilename,
        lookupname,
        appcontext="search",
        request_type="GET",
        acl=None,
    ):

        LOGGER.info("upload a lookup file")
        if acl == "sharing=global":
            lookup_url = "/servicesNS/nobody/{0}/data/lookup-table-files".format(
                appcontext
            )
        else:
            lookup_url = const.TestConstants["UPLOAD_LOOKUP_FILE"].format(appcontext)
        lookup_path = os.path.join(
            splunk.splunk_home, "var", "run", "splunk", "lookup_tmp"
        )
        lookup_args = {
            "eai:data": lookup_path + os.sep + lookupfilename,
            "name": lookupfilename,
        }
        cmd = 'cmd python -c "import os; os.makedirs(\\"{0}\\")"'.format(lookup_path)
        (code, stdout, stderr) = splunk.execute(cmd)
        # copy lookup file to lookup_tmp folder in $splunk_home/var/run/splunk
        splunk._file_utils.send(lookupfilepath, lookup_path)
        request_type = "POST"
        response, content = self.make_http_request(
            splunk,
            request_type,
            lookup_url,
            lookup_args,
            splunk.username,
            splunk.password,
        )
        LOGGER.info("Create a lookup using the lookup file")
        lookup_url = const.TestConstants["CREATE_TABLE_LOOKUP"].format(appcontext)
        lookup_args = {"name": lookupname, "filename": lookupfilename}
        request_type = request_type
        response, content = self.make_http_request(
            splunk,
            request_type,
            lookup_url,
            lookup_args,
            splunk.username,
            splunk.password,
        )

        return response, content

    def edit_lookup_file(
        self,
        splunk,
        ssh_user="",
        ssh_pwd="",
        lookupfilepath="",
        lookupfilename="",
        lookupname="",
        request_type="GET",
        appcontext="search",
    ):

        lookup_url = const.TestConstants["UPLOAD_LOOKUP_FILE"].format(appcontext)

        if request_type == "POST":
            LOGGER.info("upload a lookup file")
            lookup_path = os.path.join(
                splunk.splunk_home, "var", "run", "splunk", "lookup_tmp"
            )
            lookup_path_local = os.path.join(lookupfilepath, lookupfilename)
            splunk.connection.execute("mkdir " + lookup_path)
            splunk._file_utils.send(lookup_path_local, lookup_path)
            LOGGER.info("Create a lookup using the lookup file")
            lookup_args = {
                "eai:data": os.path.join(lookup_path, lookupfilename),
                "name": lookupname,
            }

        if request_type == "DELETE" or request_type == "GET":
            lookup_url = lookup_url + "/" + lookupname
            lookup_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            lookup_url,
            lookup_args,
            splunk.username,
            splunk.password,
        )
        return response, content

    def edit_macros(
        self,
        splunk,
        appcontext,
        macro_name,
        macro_definition,
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Create edit a macro")
        macro_url = const.TestConstants["EDIT_MACRO"].format(appcontext)

        if request_type == "POST":
            macro_args = {"name": macro_name, "definition": macro_definition}

        if acl != None:
            macro_acl_url = macro_url + "/" + macro_name
            response, content = self.make_http_request(
                splunk,
                request_type,
                macro_acl_url,
                acl,
                splunk.username,
                splunk.password,
            )

        if request_type == "DELETE" or request_type == "GET":
            macro_url = macro_url + "/" + macro_name
            macro_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk,
            request_type,
            macro_url,
            macro_args,
            splunk.username,
            splunk.password,
        )

        return response, content

    def embed_report(
        self,
        splunk,
        reportname,
        appcontext="search",
        arguments={"output_mode": "json"},
        request_type="GET",
        acl=None,
    ):
        LOGGER.info("Create embedded report")
        request_url = const.TestConstants["EMBED_REPORT"].format(appcontext, reportname)
        request_args = {"output_mode": "json"}
        response, content = self.make_http_request(
            splunk,
            request_type,
            request_url,
            request_args,
            splunk.username,
            splunk.password,
        )

        return response, content

    def edit_datamodel(
        self,
        splunk,
        appcontext,
        dm_name,
        dm_description,
        request_type="GET",
        acl=None,
        splunk_user="admin",
        splunk_pwd="changed",
    ):
        LOGGER.info("Edit data model")

        dm_url = const.TestConstants["EDIT_DATAMODEL"].format(appcontext)

        if request_type == "POST":
            dm_args = {"name": dm_name}

        if acl != None:
            dm_acl_url = dm_url + "/" + dm_name
            response, content = self.make_http_request(
                splunk, request_type, dm_url, dm_args, splunk_user, splunk_pwd
            )

        if request_type == "DELETE" or request_type == "GET":
            dm_url = dm_url + "/" + dm_name
            dm_args = {"output_mode": "json"}

        response, content = self.make_http_request(
            splunk, request_type, dm_url, dm_args, splunk_user, splunk_pwd
        )

        return response, content

    def check_geobin(self, nightlysplunk, statsfunc, geobin):
        query = (
            "search index=geo checkin.geolong>=%s checkin.geolong<%s checkin.geolat>=%s checkin.geolat<%s | stats %s"
            % (
                geobin["_geo_bounds_west"],
                geobin["_geo_bounds_east"],
                geobin["_geo_bounds_south"],
                geobin["_geo_bounds_north"],
                statsfunc,
            )
        )
        job = nightlysplunk.jobs().create(query)
        job.wait()
        result = job.get_results()[0]
        for key in result:
            self.logger.info(result)
            assert result[key] == geobin[key]

    def make_http_request(
        self,
        splunk,
        request_type,
        request_url,
        request_args,
        splunk_user="admin",
        splunk_pwd="changed",
    ):
        """
        This is a REST helper that will generate a http request
        using request_type - GET/POST/...
        request_url and request_args
        """
        restconn = splunk.create_logged_in_connector(
            contype=Connector.REST, username=splunk_user, password=splunk_pwd
        )
        try:
            response, content = restconn.make_request(
                request_type, request_url, request_args
            )
            return response, content

        except urllib.error.HTTPError as err:
            print(
                "Http error code is ({0}): {1} : {2}".format(
                    err.code, err.errno, err.strerror
                )
            )

    def get_fired_alerts(self, splunk, saved_search_name):
        LOGGER.info("Creating edit a saved search")
        splunk_user = splunk.username
        splunk_pwd = splunk.password
        req_args = {"output_mode": "json"}
        req_url = const.TestConstants["FIRED_ALERT_DETAILS"].format(saved_search_name)
        response, content = self.make_http_request(
            splunk, "GET", req_url, req_args, splunk_user, splunk_pwd
        )
        parsedresponse = json.loads(content)
        alertlisting = []
        for job in parsedresponse["entry"]:
            alertlisting.append(job["content"])
        return alertlisting
