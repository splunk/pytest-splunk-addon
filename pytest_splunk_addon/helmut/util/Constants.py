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
from builtins import object


class Constants(object):
    TestConstants = {
        # Email alerting constants
        "EMAIL_SETTINGS": "/servicesNS/admin/search/admin/alert_actions/email",
        "PAPER_ORIENTATION": "/servicesNS/admin/search/saved/searches/{0}",
        "PAPER_SIZE": "/servicesNS/admin/search/saved/searches/{0}",
        "SMTP_SERVER": "10.184.16.130:{0}",
        "SPLUNK_MAIL_HOST": "10.184.16.130",
        # Splunk constants
        "AUTO_PORTS": " --auto-ports",
        "DFLT_BRNCH": "current",
        "RUN_LOCAL": "local",
        "RUN_REMOTE": "remote",
        "SSH_PORT": "22",
        "SPLUNK_START": "splunkd start",
        "SPLUNK_STOP": "splunkd stop",
        "SPLUNK_RESTART": "splunkd restart",
        "SERVER_INFO": "/services/server/info",
        # Search head pooling constants
        "SLAVE": "slave",
        "MASTER": "captain",
        "ADHOC": "adhoc",
        "SERVER_ROLE": "/services/server/roles",
        "SHP_CONFIG_PEER": "/services/shcluster/config/config",
        "SHP_MEMBER_INFO": "/services/shcluster/{0}/info",
        "SHP_MEMBER_GUID": "/services/shcluster/captain/members",
        "SHP_MEMBER_MEMBERS": "/services/shcluster/member/members",
        "SHP_CAPTAIN_CONFIG": "/services/shcluster/config",
        "SHP_ARTIFACT": "/services/shcluster/{0}/artifacts",
        "SHP_BOOTSTRAP": "/services/shcluster/member/consensus/foo/bootstrap",
        "SHP_CONSENSUS": "/services/shcluster/member/consensus",
        # 'SHP_ADD_PEER':'/services/shcluster/member/consensus/foo/set_configuration',
        "SHP_ADD_PEER": "/services/shcluster/member/consensus/foo/bootstrap",
        "SHP_DYNAMIC_SETUP": "/servicesNS/nobody/system/configs/conf-server/shclustering",
        "SHP_CAPTAIN_INFO": "/services/shcluster/captain/info",
        "SHP_STATUS": "/services/shcluster/status",
        "SHP_CAPTAIN_ARTIFACTS": "/services/shcluster/captain/artifacts",
        "SHP_JOBS": "/services/shcluster/captain/jobs",
        "CONF_DEPLOY_MGR": "/services/apps/deploy",
        "SHP_CAPTAIN_TRANSFER": "/services/shcluster/member/consensus/foo/transfer_captaincy",
        # Search constants
        "SAVED_SEARCH": "/servicesNS/{0}/{1}/saved/searches",  # {0} is the user and {1} is the app
        "FIRED_ALERT": "/servicesNS/admin/search/alerts/fired_alerts",
        "SAVED_SEARCH_NAME": "/servicesNS/admin/search/admin/savedsearch/{0}",
        "FIRED_ALERT_DETAILS": "/servicesNS/admin/search/alerts/fired_alerts/{0}",
        "ADD_DIST_PEER": "/servicesNS/nobody/search/search/distributed/peers",
        "EDIT_SAVED_SEARCH": "/servicesNS/nobody/{0}/saved/searches",
        "EDIT_APP": "/servicesNS/nobody/system/apps/local",
        "SEARCH_JOB": "/services/{0}/jobs",
        "SEARCH_JOB_ID": "/services/search/jobs/{0}",
        "JOB_CONTROL": "/services/search/jobs/{0}/control",
        "JOB_EVENTS": "/search/jobs/{0}/events",
        "JOB_RESULTS": "/search/jobs/{0}/results",
        "JOBS_RESULTS_PREVIEW": "/search/jobs/{0}/results_preview",
        "SEARCH_JOB_LOG": "/search/jobs/{0}/search.log",
        "JOB_SUMMARY": "/search/jobs/{0}/summary",
        "JOB_TIMELINE": "/search/jobs/{0}/timeline",
        # Knowledge Object Constants
        "ADD_TAG": "/servicesNS/nobody/{0}/search/fields/{1}/tags",  # 0 is fieldname
        "GET_TAG": "/servicesNS/nobody/{0}/{1}/tags",
        "EDIT_EVENTTYPE": "/servicesNS/nobody/{0}/saved/eventtypes",
        "GET_EVENTTYPE": "/servicesNS/nobody/{0}/saved/eventtypes",
        "EDIT_LOOKUP": "/servicesNS/nobody/{0}/data/props/lookups",
        "UPLOAD_LOOKUP_FILE": "/servicesNS/admin/{0}/data/lookup-table-files",
        "CREATE_TABLE_LOOKUP": "/servicesNS/nobody/{0}/data/transforms/lookups",
        "GET_LOOKUP_FILE": "/servicesNS/nobody/{0}/data/lookup-table-files/{0}",
        "GET_TABLE_LOOKUP": "/servicesNS/nobody/{0}/data/transforms/lookups/{0}",
        "EDIT_MACRO": "/servicesNS/nobody/{0}/admin/macros",
        "EDIT_FELD_ALIAS": "/servicesNS/nobody/{0}/data/props/fieldaliases",
        "GET_FIELD_ALIAS": "/servicesNS/nobody/{0}/data/props/fieldaliases/{1}",
        "EXTRACTION": "",
        "EDIT_CALC_FIELDS": "/servicesNS/nobody/{0}/data/props/calcfields",
        "GET_CALC_FIELDS": "/servicesNS/nobody/{0}/data/props/calcfields/{1}",
        "EDIT_FIELD_EXTRACTION": "/servicesNS/nobody/{0}/data/transforms/extractions",
        "GET_FIELD_EXTRACTION": "/servicesNS/admin/{0}/data/transforms/extractions/{1}",
        "EDIT_IFX": "/servicesNS/nobody/{0}/data/props/extractions",
        "GET_IFX": "/servicesNS/nobody/{0}/data/props/extractions/{1}",
        "EDIT_DASHBOARD": "/servicesNS/nobody/{0}/data/ui/views",
        "GET_DASHBOARD": "/servicesNS/nobody/{0}/data/ui/views/{1}",
        "SOURCE_TYPE_RENAME": "/servicesNS/nobody/{0}/data/props/sourcetype-rename",
        "EDIT_DATAMODEL": "/servicesNS/nobody/{0}/datamodel/model",
        "GET_DATAMODEL": "/servicesNS/nobody/{0}/datamodel/model/{1}",
        "EMBED_REPORT": "/servicesNS/nobody/{0}/saved/searches/{1}/embed",
        # knowledge objects with user space
        "EDIT_FIELD_EXTRACTION_USRCXT": "/servicesNS/{0}/{1}/data/transforms/extractions",
        "ADD_TAG_USRCXT": "/servicesNS/{0}/{1}/search/fields/{2}/tags",
        "SOURCE_TYPE_RENAME_USRCXT": "/servicesNS/{0}/{1}/data/props/sourcetype-rename",
        "EDIT_FELD_ALIAS_USRCXT": "/servicesNS/{0}/{1}/data/props/fieldaliases",
        "EDIT_IFX_USRCTX": "/servicesNS/{0}/{1}/data/props/extractions",
        "EDIT_SAVED_SEARCH_USRCTX": "/servicesNS/{0}/{1}/saved/searches",
        "SUPPRESS": "/servicesNS/{0}/{1}/saved/searches/{2}/suppress",
        "ACKNOWLEDGE": "/servicesNS/{0}/{1}/saved/searches/{2}/acknowledge",
        # App constants
        "APP_INSTALL": "/servicesNS/{0}/{1}/apps/appinstall",
        "APP_LOCAL": "/servicesNS/{0}/{1}/apps/local",
        "ONE_SHOT": "/servicesNS/{0}/{1}/data/inputs/oneshot",
        "USER_CONTEXT": "/services/authentication/users",
        "STORAGE_PASSWORDS": "/servicesNS/{0}/{1}/storage/passwords",
        # Config constants
        "CONFIG_CONF_INPUTS_NEW": "/services/configs/conf-inputs/_new",
        "CONF_PROPERTY": "/services/properties/{0}/{1}/{2}",
        # Server constants
        "SERVER_INTRO_INDEXER": "/services/server/introspection/indexer",
        # Authentication constants
        "AUTHENTICATION_USERS": "/services/authentication/users",
        # Cluster constants
        "MASTER_INDEXES": "/services/cluster/master/indexes",
        "MASTER_BUCKETS": "/services/cluster/master/buckets",
        "MASTER_GENERATION": "/services/cluster/master/generation",
        "SEARCH_HEAD_GENERATION": "/services/cluster/searchhead/generation",
        "MASTER_MESSAGE": "/services/messages",
        "MASTER_COMMIT_GENERATION": "/services/cluster/master/control/control/commit_generation",
        "MASTER_CONTROL_ROLL_BUCKET": "/services/cluster/master/control/control/roll-hot-buckets",
        "MASTER_SEARCH_HEADS": "/services/cluster/master/searchheads",
        "MASTER_PEERS": "/services/cluster/master/peers",
        # Forwarder director
        "INDEXER_DISCOVERY": "/services/indexer_discovery",
        # Data constants
        "DATA_INDEXES": "/services/data/indexes",
        "DATA_INDEXES_FREEZE": "/services/data/indexes/{0}/freeze-buckets",
        "DATA_INPUTS_TCP_RAW": "/services/data/inputs/tcp/raw",
        # Authorization & Authentication
        "AUTH_ROLE": "/services/authorization/roles/",
        "AUTH_USER": "/services/authentication/users/",
        "AUTH_LDAP": "/services/authentication/providers/LDAP/",
        "AUTH_SAML": "/services/authentication/providers/SAML/",
        "AUTH_SCRIPTED": "/services/authentication/providers/Scripted/",
        # Error Message
        "MSG_SHP_ROLLING_RESTART_COMPLETE": "Message : Search Head Clustering is not currently in a rolling Restart state. May be the rolling restart is complete or this node is going to restart itself.",
        # Auth Settings
        "LDAP_AUTH_CONF": {
            "name": "LDAP",
            "host": "10.66.128.50",
            "port": "389",
            "groupBaseDN": "OU=groups,OU=automation,DC=jacktest,DC=com",
            "groupMappingAttribute": "dn",
            "groupMemberAttribute": "member",
            "groupNameAttribute": "cn",
            "userBaseDN": "OU=Users,OU=automation,DC=jacktest,DC=com",
            "userNameAttribute": "samaccountname",
            "bindDN": "CN=Administrator,CN=Users,DC=jacktest,DC=com",
            "bindDNpassword": "QWE123asd",
            "realNameAttribute": "cn",
        },
        "LDAP_AUTH_CONF1": {
            "bindDNpassword": "changeme",
            "groupBaseDN": "ou=groups,dc=coreuitest,dc=com",
            "groupMemberAttribute": "member",
            "groupNameAttribute": "cn",
            "host": "10.66.130.102",
            "name": "LDAP1",
            "realNameAttribute": "displayname",
            "userBaseDN": "ou=people,dc=coreuitest,dc=com",
            "userNameAttribute": "uid",
        },
        "SAML_AUTH_CONF": {
            "name": "SAML",
            "allowSslCompression": "true",
            "attributeQueryRequestSigned": "true",
            "attributeQueryResponseSigned": "true",
            "attributeQuerySoapPassword": "QWE123asd",
            "attributeQuerySoapUsername": "saml_automation",
            "entityId": "saml_automation",
            "fqdn": "",
            "idpAttributeQueryUrl": "https://ping.splunk.io:9031/idp/attrsvc.ssaml2",
            "idpCertPath": "",
            "idpSLOUrl": "https://ping.splunk.io:9031/idp/SLO.saml2",
            "idpSSOUrl": "https://ping.splunk.io:9031/idp/SSO.saml2",
            "redirectPort": "0",
            "signAuthnRequest": "true",
            "signedAssertion": "true",
            # 'enableSplunkdSSL': 'true',
            "sslKeysfile": "aNewServerCertificate.pem",
            "sslKeysfilePassword": "changed",
            # 'caCertFile': 'aCACertificate.pem',
            # 'caPath': '/root/splunk/etc/auth/self_signed_certs'
        },
    }
