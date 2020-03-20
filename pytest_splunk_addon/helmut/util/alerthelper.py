from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
from builtins import str
from builtins import object
import logging
import json
import os
import http.client
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import time

from pytest_splunk_addon.helmut.splunk_factory.splunkfactory import SplunkFactory
from pytest_splunk_addon.helmut.connector.base import Connector

from pytest_splunk_addon.helmut.util.Constants import Constants as const

LOGGER = logging.getLogger("alter helper log")
import socket


class AlertHelpers(object):
    def __init__(self):

        global request_args
        global email_args
        request_args = dict()
        email_args = dict()

    def createbasicAlert(
        self,
        name,
        subject,
        search="index=_internal",  # replace index=_internal with the other search
        cron_schedule="*/1 * * * *",
    ):
        """
        sets the attributes needed for a basic alert such in request_args which
        is a global static list
        search - splunk search query
        name - name of the search
        is_scheduled - save search as scheduled search
        alert.track - List the alert in alert list
        """

        request_args[
            "search"
        ] = search  # replace hardcoding with current working directory
        request_args["name"] = name
        request_args["cron_schedule"] = cron_schedule
        request_args["is_scheduled"] = "True"
        request_args["actions"] = "email"
        request_args["action.email"] = "True"
        request_args["action.email.track_alert"] = "True"
        request_args["alert.track"] = "True"
        request_args["action.populate_lookup.track_alert"] = "True"
        request_args["alert.digest_mode"] = "True"
        request_args["alert.suppress"] = 1
        request_args["alert.suppress.period"] = "24h"

    def setEmailSubject(self, subject):
        request_args["action.email.subject"] = subject
        request_args["action.email.subject.alert"] = subject
        request_args["action.email.subject.report"] = subject

    #  def set_alert_condition(self):

    def setemailMode(self, mailserver, email_mode="TLS"):
        """
        sets the email mode to TLS/SSL/None
        """
        if email_mode == "TLS":
            request_args["action.email.use_tls"] = 1
        else:
            if email_mode == "SSL":
                request_args["action.email.mailserver"] = mailserver
                request_args["action.email.use_ssl"] = 1

    def setup_mail_server(self, splunk, user, password, mail_server, mode="None"):
        """
        Updates the email alert settings of the splunk instance
        for SSL sets the smtp mailserver and ssl port
        Restarts the splunk instance after updating the settings
        """

        request_type = "POST"
        request_url = const.TestConstants["EMAIL_SETTINGS"]

        request_args = dict()
        request_args["auth_password"] = ""
        request_args["auth_username"] = ""
        request_args["mailserver"] = const.TestConstants["SPLUNK_MAIL_HOST"]
        request_args["use_ssl"] = 0
        request_args["use_tls"] = 0
        request_args["reportServerURL"] = " "

        if mode == "SSL":
            request_args["auth_password"] = password
            request_args["auth_username"] = user
            request_args["mailserver"] = const.TestConstants["SMTP_SERVER"].format(
                "465"
            )
            request_args["use_ssl"] = 1
            request_args["reportServerURL"] = " "

        if mode == "TLS":
            request_args["auth_password"] = password
            request_args["auth_username"] = user
            request_args["mailserver"] = const.TestConstants["SMTP_SERVER"].format("25")
            request_args["use_tls"] = 1
            request_args["reportServerURL"] = " "

        self.make_http_request(
            splunk,
            request_type,
            request_url,
            request_args,
            splunk.username,
            splunk.password,
        )
        splunk.execute("splunk restart")

    def updatePaperSettings(
        self, paper_size="Letter", paper_orientation="Portrait", splunk_logo=0
    ):
        """
        Update the email alert setting to update options such as
        format - email format when results included inline
        paper_size - Letter|A4|A3 etc
        paper_orientation - Portrait | landscape
        splunk_logo - Whether to include splunk logo or not
        """
        request_args["action.email.reportPaperSize"] = paper_size
        request_args["action.email.reportPaperOrientation"] = paper_orientation
        request_args["action.email.reportIncludeSplunkLogo"] = splunk_logo

    def addContentsToEmail(self, tokenlist):
        request_args["action.email.message.alert"] = tokenlist

    def addSearchResultstoEmail(self, sendMethod, format="csv"):
        """
        Configures the email to have the search results as
        1. Inline - results directly in the message body
        2. Attachments - Attach the results to the message body
        """
        #        request_args['action.email.sendresults'] = 'True'
        request_args["action.email.sendresults"] = 0
        request_args["action.email.inline"] = 0
        request_args["action.email.sendpdf"] = 0
        request_args["action.email.sendcsv"] = 0

        if sendMethod == "inline":
            """
            inline csv
            inline table
            inline raw
            """
            request_args["action.email.sendresults"] = 1
            request_args["action.email.inline"] = 1
            self.configure_email_format(format)

        if sendMethod == "pdf":
            request_args["action.email.sendresults"] = 1
            request_args["action.email.sendpdf"] = 1

        if sendMethod == "attachment":
            request_args["action.email.sendresults"] = 1
            request_args["action.email.sendcsv"] = 1

        if sendMethod == "Noresults":
            self.configure_email_format(format)

    def configure_email_format(self, email_format="plain"):
        """
        Updates the email format (applies to inline and attachments)
        to one of the following
        1. text
        2. html
        3. csv
        4. raw
        """
        request_args["action.email.format"] = email_format

    def add_email_recipients(self, to_list={}, cc_list={}, bcc_list={}):
        """
        Updates the email recipients in to,cc and bcc list
        """
        to_list1 = to_list.split("|")
        cc_list1 = cc_list.split("|")
        bcc_list1 = bcc_list.split("|")

        toList = ",".join(to_list1)
        ccList = ",".join(cc_list1)
        bccList = ",".join(bcc_list1)

        toList = toList[1:-1]
        ccList = ccList[1:-1]
        bccList = bccList[1:-1]

        request_args["action.email.to"] = toList
        request_args["action.email.cc"] = ccList
        request_args["action.email.bcc"] = bccList

    def deleteAlert(self, alertname):
        """
        deletes an alert using the name of the alert
        """
        request_type = "DELETE"
        request_url = const.TestConstants["SAVED_SEARCH_NAME"].format(alertname)
        request_args = ""
        self.make_http_request(request_type, request_url, request_args)

    def createAlert(self, splunk, user, context):
        """
        Creates an alert by sending POST request to the saved/searches
        REST endpoint
        """
        request_type = "POST"
        print("user and context is {0} and {1}".format(user, context))
        request_url = const.TestConstants["SAVED_SEARCH"].format(user, context)
        self.make_http_request(
            splunk,
            request_type,
            request_url,
            request_args,
            splunk.username,
            splunk.password,
        )

    def get_paper_orientation(self, splunk, alertname):
        """
        Check the rest endpoint for paper orientation (Landscape, Portrait)
        """
        request_type = "GET"
        request_url = const.TestConstants["PAPER_ORIENTATION"].format(alertname)
        req_args = dict()
        req_args["output_mode"] = "json"
        content = self.make_http_request(
            splunk,
            request_type,
            request_url,
            req_args,
            splunk.username,
            splunk.password,
        )
        parsedresponse = json.loads(content)
        paper_orientation = str(
            parsedresponse["entry"][0]["content"]["action.email.reportPaperOrientation"]
        )
        return paper_orientation

    def get_paper_size(self, splunk, alertname):
        """
        check the rest endpoint for paper format(Letter, Legal, A2, A3, A4, A5)
        """
        request_type = "GET"
        req_args = dict()
        req_args["output_mode"] = "json"
        request_url = const.TestConstants["PAPER_SIZE"].format(alertname)
        content = self.make_http_request(
            splunk,
            request_type,
            request_url,
            req_args,
            splunk.username,
            splunk.password,
        )
        parsedresponse = json.loads(content)
        paper_size = str(
            parsedresponse["entry"][0]["content"]["action.email.reportPaperSize"]
        )
        return paper_size

    def get_triggered_alert_count(self, splunk, alert_name, password="changeme"):
        "triggered_alert"
        try:
            request_type = "GET"
            req_args = dict()
            req_args["output_mode"] = "json"
            request_url = const.TestConstants["FIRED_ALERT_DETAILS"].format(alert_name)
            content = self.make_http_request(
                splunk,
                request_type,
                request_url,
                req_args,
                splunk.username,
                splunk.password,
            )
            parsedresponse = json.loads(content)
            triggered_alert = int(
                parsedresponse["entry"][0]["content"]["triggered_alerts"]
            )
            return triggered_alert
        except Exception as e:
            LOGGER.error("Exception when get triggered_alert:" + repr(e))
            return None

    def trigger_alerts(
        self,
        splunk,
        mail_server,
        user,
        password,
        emailMode="None",
        search=None,
        filename="alertconfig.conf",
        hostname=None,
    ):
        """
        This method will trigger an alert using input file. Multiple alerts can
        be defined in the file
        The file format as follows,
        name of alert, cron_schedule, email_to_list, email_cc_list,
        email_bcc_list, email format,adSearchResults to email,
        format in attachment, paper_size, paper_orientation,splunk logo
        """
        conf = open(filename, "r")
        f = conf.readlines()
        self.setup_mail_server(
            splunk, user, password, mail_server, mode=emailMode
        )  # for mode get pytest parameter

        for line in f:
            elements = line.split("|")
            if hostname is None:
                # INFRA-6217
                elements[0] = elements[0] + "." + socket.gethostname()
            else:
                elements[0] = elements[0] + "." + hostname
            self.createbasicAlert(
                name=elements[0],
                cron_schedule=elements[1],
                subject=elements[0],
                search=search,
            )
            self.setEmailSubject(elements[0])
            self.setemailMode(mail_server, email_mode=emailMode)

            self.add_email_recipients(elements[2], elements[3], elements[4])
            self.addSearchResultstoEmail(elements[6], format=elements[5])

            self.updatePaperSettings(
                paper_size=elements[8],
                paper_orientation=elements[9],
                splunk_logo=elements[10],
            )

            print("Creating alert {0}".format(elements[0]))
            print("file name is {0}".format(elements[13]))

            if elements[13].rstrip("\n") != "None":
                with open(elements[13].rstrip("\n"), "r") as myfile:
                    data = "".join(line for line in myfile)
                    self.addContentsToEmail(data)

            self.createAlert(
                splunk,
                context=elements[12].rstrip("\n"),
                user=elements[11].rstrip("\n"),
            )

    def create_new_app(
        self,
        splunk,
        appname,
        appcontext,
        user,
        splunk_user="admin",
        splunk_pwd="changeme",
    ):
        #        app_params = {'name':'nithya','app':'search','user':'admin',}
        app_params = {"name": appname}
        app_url = const.TestConstants["APP_LOCAL"].format(user, appcontext)
        request_type = "POST"
        self.make_http_request(
            splunk,
            request_type,
            app_url,
            app_params,
            splunk_user=splunk_user,
            splunk_pwd=splunk_pwd,
        )

    def create_new_user(
        self, splunk, newuser, pwd, roles, splunk_user="admin", splunk_pwd="changeme"
    ):
        #        app_params = {'name':'nithya','app':'search','user':'admin',}
        app_params = {"name": newuser, "roles": roles, "password": pwd}
        app_url = const.TestConstants["USER_CONTEXT"]
        request_type = "POST"
        self.make_http_request(
            splunk,
            request_type,
            app_url,
            app_params,
            splunk_user=splunk_user,
            splunk_pwd=splunk_pwd,
        )

    def get_splunk(self, TEST_DIR, branch=None, product=None, build=None):
        """
        Splunk  instance
        """
        splunk_home = (
            TEST_DIR + os.sep + "test_installs" + os.sep + "temp_splunk_instance"
        )
        splunk_instance = SplunkFactory.getSplunk(splunk_home)
        splunk_instance.install_nightly(
            branch=branch, package_type=product, build=build
        )
        # splunk_instance.COMMON_FLAGS = splunk_instance.COMMON_FLAGS + ' --auto-ports'
        splunk_instance.start(auto_ports=True)

        return splunk_instance

    def one_shot_upload(
        self,
        splunk,
        user,
        appcontext,
        one_shot_file,
        splunk_user="admin",
        splunk_pwd="changeme",
    ):
        print(
            "this method will upload the data input file needed for \
        running searches in the alerts"
        )
        oneshot_url = const.TestConstants["ONE_SHOT"].format(user, appcontext)
        oneshot_args = {"name": one_shot_file}
        request_type = "POST"
        self.make_http_request(
            splunk,
            request_type,
            oneshot_url,
            oneshot_args,
            splunk_user=splunk_user,
            splunk_pwd=splunk_pwd,
        )

    def make_http_request(
        self,
        splunk,
        request_type,
        request_url,
        request_args,
        splunk_user="admin",
        splunk_pwd="changeme",
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
            return content

        except urllib.error.HTTPError as err:
            LOGGER.error(
                "Http error code is ({0}): {1} : {2}".format(
                    err.code, err.errno, err.strerror
                )
            )
        except http.client.ResponseNotReady as e:
            time.sleep(5)
            LOGGER.warn(
                "httplib.ResponseNotReady error happen, retry once. {e}".format(e=e)
            )
            # retry one time
            try:
                restconn = splunk.create_logged_in_connector(
                    contype=Connector.REST, username=splunk_user, password=splunk_pwd
                )
                response, content = restconn.make_request(
                    request_type, request_url, request_args
                )
                return content
            except Exception as e:
                LOGGER.error("Error happened, exception is {e}".format(e=e))
