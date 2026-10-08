
python.version = {default|python|python2|python3}
* Optional setting. Requires 8.0+
* For Python scripts only, selects which Python version to use.
* Set to either "default" or "python" to use the system-wide default Python
  version.
* Optional.
* Default: Not set; uses the system-wide Python version.

[relaymodaction://<name>]
uri = <string>
* Remote splunk instance management URI.
* Format should be protocol://host:port

description = <string>
* Description for the remote Splunk instance.

username = <string>
* Label pertaining to the API key stored in secure storage, must be unique.
* Realm is "cam_queue".

verify = <string>
* Specifies if SSL verification is needed between worker and remote search head.
* Defaults to True

client_cert = <string>
* Filename of client certificate.
* Specify when SSL verification is needed, leave empty otherwise.
* Certificate should be put in $splunk_home/etc/apps/Splunk_SA_CIM/auth
