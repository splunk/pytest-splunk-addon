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
from future import standard_library

standard_library.install_aliases()
from builtins import object


class RESTURIS(object):
    """
    Simple module to wrap REST endpoints into a consistent set of methods
    """

    URIS = {
        "APP": "/servicesNS/{u}/{a}/apps",
        "APP_TEMPLATE": "/servicesNS/{u}/{a}/apps/apptemplates",
        "APP_LOCAL": "/servicesNS/{u}/{a}/apps/local/",
        "APP_INSTALL": "/servicesNS/{u}/{a}/apps/appinstall",
        "AUTOMATIC_LOOKUP": "/servicesNS/{u}/{a}/data/props/lookups",
        "AUTHENTICATION": "/services/authentication/users",
        "CALCUALTED_FIELD": "/servicesNS/{u}/{a}/data/props/calcfields",
        "CAPABILITIES": "/services/authorization/capabilities/",
        "CHANGEPASSWORD": "/servicesNS/{u}/{a}/authentication/changepassword/",
        "CONFIG": "/servicesNS/{u}/{a}/configs/{config}/",
        "CLUSTER_CONFIG": "/servicesNS/{u}/{a}/cluster/config",
        "CLUSTER_MASTER": "/servicesNS/{u}/{a}/cluster/master",
        "CLUSTER_SEARCHHEAD": "/servicesNS/{u}/{a}/cluster/searchhead",
        "CLUSTER_SLAVE": "/servicesNS/{u}/{a}/cluster/slave",
        "DATAMODEL_REPORT": "/services/datamodel/pivot/{dm}",
        "DATAMODEL_ACC": "/services/datamodel/model/",
        "DATAMODEL": "/servicesNS/{u}/{a}/datamodel/model/",
        "DATAMODEL_ACCELERATION": "/services/datamodel/acceleration",
        "DATAMODEL_DOWNLOAD": "/servicesNS/{u}/{a}/data/models/{dm}/download",
        "DATAMODEL_PIVOT": "/servicesNS/{u}/{a}/datamodel/pivot/",
        "DEPLOYMENT_CLIENT_CONFIG": ("/servicesNS/{u}/{a}/deployment/client/config"),
        "DEPLOYMENT_SERVER_CLASSES": (
            "/servicesNS/{u}/{a}/deployment/server/serverclasses"
        ),
        "DEPLOYMENT_SERVER_CONFIG": ("/servicesNS/{u}/{a}/deployment/server/config"),
        "DEPLOYMENT_SERVER_CLIENTS": ("/servicesNS/{u}/{a}/deployment/server/clients"),
        "DEPLOYMENT_SERVER_APPLICATION": (
            "/servicesNS/{u}/{a}/deployment/server/applications"
        ),
        "EVENTTYPE": "/servicesNS/{u}/{a}/saved/eventtypes",
        "FIRED_ALERT": "/servicesNS/{u}/{a}/alerts/fired_alerts",
        "FIELD": "/servicesNS/{u}/{a}/search/fields",
        "FIELD_ALIAS": "/servicesNS/{u}/{a}/data/props/fieldaliases",
        "FIELD_EXTRACTION": "/servicesNS/{u}/{a}/data/props/extractions",
        "FVTAG": "/servicesNS/{u}/{a}/saved/fvtags",
        "HTTPAUTH_TOKEN": "/servicesNS/{u}/{a}/authentication/httpauth-tokens",
        "INDEX": "/servicesNS/{u}/{a}/data/indexes/",
        "INPUT_MONITOR": "/servicesNS/{u}/{a}/data/inputs/monitor",
        "INPUT_ONESHOT": "/servicesNS/{u}/{a}/data/inputs/oneshot",
        "INPUT_SCRIPT": "/servicesNS/{u}/{a}/data/inputs/script",
        "INPUT_TCP_COOKED": "/servicesNS/{u}/{a}/data/inputs/tcp/cooked",
        "INPUT_TCP_RAW": "/servicesNS/{u}/{a}/data/inputs/tcp/raw",
        "INPUT_UDP": "/servicesNS/{u}/{a}/data/inputs/udp",
        "INPUT_EVENTLOG": ("/servicesNS/{u}/{a}/data/inputs/win-event-log-collections"),
        "INPUT_REGMON": "/servicesNS/{u}/{a}/data/inputs/WinRegMon",
        "INPUT_PERFMON": "/servicesNS/{u}/{a}/data/inputs/win-perfmon",
        "INPUT_HOSTMON": "/servicesNS/{u}/{a}/data/inputs/WinHostMon",
        "INPUT_NETMON": "/servicesNS/{u}/{a}/data/inputs/WinNetMon",
        "INPUT_ADMON": "/servicesNS/{u}/{a}/data/inputs/ad",
        "INPUT_PRINTMON": "/servicesNS/{u}/{a}/data/inputs/WinPrintMon",
        "JOB": "/servicesNS/{u}/{a}/search/jobs",
        "LDAP": "/services/authentication/providers/LDAP/",
        "LOOKUP": "/servicesNS/{u}/{a}/data/props/lookups/",
        "LOOKUP_TRANSFORM": "/servicesNS/{u}/{a}/data/transforms/lookups/",
        "LOOKUP_TABLE_FILES": "/servicesNS/{u}/{a}/data/lookup-table-files",
        "LOGIN": "/services/auth/login",
        "MACRO": "/servicesNS/{u}/{a}/data/macros",
        "MESSAGES": "/servicesNS/{u}/{a}/messages",
        "NAVIGATION": "/servicesNS/{u}/{a}/data/ui/nav",
        "NTAG": "/servicesNS/{u}/{a}/saved/ntags",
        "OPEN_IN_PIVOT_GENERATE": "/services/datamodel/generate",
        "PROPERTIES": "/servicesNS/{u}/{a}/properties",
        "ROLE": "/services/authorization/roles/",
        "REFRESH": "/debug/refresh",
        "SAVED_SEARCH": "/servicesNS/{u}/{a}/saved/searches",
        "SCHEDULED_VIEW": "/servicesNS/{u}/{a}/scheduled/views",
        "SEARCH_COMMANDS": "/servicesNS/{u}/{a}/search/commands",
        "SOURCETYPE": "/servicesNS/{u}/{a}/saved/sourcetypes",
        "SERVER_CONTROL_RESTART": "/services/server/control/restart/",
        "SERVER_SETTINGS": "/services/{u}/server-settings/settings",
        "ACCESS_CONTROL_XML": "/services/data/ui/manager/accesscontrols",
        "TAG": "/servicesNS/{u}/{a}/search/tags",
        "TIME": "/servicesNS/{u}/{a}/data/ui/times",
        "TRANSFORMS_EXTRACTION": ("/servicesNS/{u}/{a}/data/transforms/extractions"),
        "TRANSFORMS_LOOKUP": "/servicesNS/{u}/{a}/data/transforms/lookups/",
        "TRANSPARENT_SUMMARIZATION": "/servicesNS/{u}/{a}/admin/summarization",
        "TYPEAHEAD": "/servicesNS/{u}/{a}/search/typeahead/",
        "USER": "/servicesNS/{u}/{a}/authentication/users",
        "UI_MANAGER": "/servicesNS/{u}/{a}/data/ui/manager",
        "UI_PREFS": "/servicesNS/{u}/{a}/admin/ui-prefs",
        "USER_PREFS": "/servicesNS/{u}/{a}/admin/user-prefs",
        "VIEW": "/servicesNS/{u}/{a}/data/ui/views",
        "VIEWSTATES": "/servicesNS/{u}/{a}/data/ui/viewstates",
        "VIX_INDEXES": "/servicesNS/{u}/{a}/data/vix-indexes",
        "VIX_PROVIDERS": "/servicesNS/{u}/{a}/data/vix-providers",
        "WORKFLOW_ACTION": "/servicesNS/{u}/{a}/data/ui/workflow-actions",
        "RELOAD_ENDPOINT": "/services/configs/conf-{conf}/_reload",
        "ROLL_HOT_TO_COLD": "/services/data/indexes/{index}/chill-bucket?bucket_id={bucket_id}",
        "INDEXER_S2S_TOKEN": "/services/data/inputs/tcp/splunktcptoken",
        "FORWARDER_S2S_TOKEN": "/services/data/outputs/tcp/group",
        "SAML": "/services/authentication/providers/SAML",
        "JOBS_CREATED_FROM_SAVED_SEARCH": "/servicesNS/{u}/{a}/saved/searches/{name}/history",
        "SAML_USER_ROLE_MAP": "/services/{u}/SAML-user-role-map",
        "SAML_GROUP": "/services/{u}/SAML-groups",
        "SAML_METADATA": "services/{u}/SAML-sp-metadata",
        "SAML_AUTH": "/services/{u}/SAML-auth",
        "SPLUNK_AUTH": "/services/admin/Splunk-auth/splunk_auth",
    }
