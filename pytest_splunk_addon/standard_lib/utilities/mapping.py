"""
Replaced value of tokens
"""
FIELD_MAPPING = {
    "src": {
        "token": [
            "src",
            "srcaddr",
            "src_addr",
            "src-addr",
            "srcip",
            "src_ip",
            "src-ip",
            "srcaddress",
            "src_address",
            "src-address",
            "source",
            "sourceaddr",
            "source_addr",
            "source-addr",
            "sourceip",
            "source_ip",
            "source-ip",
            "sourceaddress",
            "source_address",
            "source-address",
            "srcfqdn",
            "src_fqdn",
            "src-fqdn",
            "sourcefqdn",
            "source_fqdn",
            "source-fqdn"
        ],
        "replacementType": "random",
        "replacement": "src[]",
        "field": "src",
        "possible_replacement": ['ipv4', 'ipv6', 'host', 'fqdn']
    },
    "dest": {
        "token": [
            "dest",
            "destaddr",
            "dest_addr",
            "dest-addr",
            "destip",
            "dest_ip",
            "dest-ip",
            "destaddress",
            "dest_address",
            "dest-address",
            "destination",
            "destinationaddr",
            "destination_addr",
            "destination-addr",
            "destinationip",
            "destination_ip",
            "destination-ip",
            "destinationaddress",
            "destination_address",
            "destination-address",
            "destfqdn",
            "dest_fqdn",
            "dest-fqdn",
            "destinationfqdn",
            "destination_fqdn",
            "destination-fqdn"
        ],
        "replacementType": "random",
        "replacement": "dest[]",
        "field": "dest",
        "possible_replacement": ['ipv4', 'ipv6', 'host', 'fqdn']
    },
    "user": {
        "token": [
            "user",
            "username",
            "usr",
            "user_name",
            "user-name",
            "users"
        ],
        "replacementType": "random",
        "replacement": "user[]",
        "field": "user",
        "possible_replacement": ["name", "email", "domain_user", "distinquised_name"]
    },
    "src_port": {
        "token": [
            "src_port",
            "src-port",
            "source_port",
            "source-port",
            "sourceport",
            "srcport"
        ],
        "replacementType": "random",
        "replacement": "src_port",
        "field": "src_port"
    },
    "dest_port": {
        "token": [
            "dest_port",
            "dest-port",
            "destination_port",
            "destination-port",
            "destinationport",
            "destport"
        ],
        "replacementType": "random",
        "replacement": "dest_port",
        "field": "dest_port"
    },
    "dvc": {
        "token": [
            "dvc"
        ],
        "replacementType": "random",
        "replacement": "dvc[]",
        "field": "dvc",
        "possible_replacement": ['ipv4', 'ipv6', 'host', 'fqdn']
    },
    "url": {
        "token": [
            "url",
            "uri"
        ],
        "replacementType": "random",
        "replacement": "url[]",
        "field": "url",
        "possible_replacement": ["ip_host", "fqdn_host", "path", "query", "protocol"]
    },
    "guid": {
        "token": [
            "guid"
        ],
        "replacementType": "random",
        "replacement": "guid"
    },
    "host": {
        "token": [
            "host",
            "hostaddr",
            "host_addr",
            "host-addr",
            "hostaddress",
            "host_address",
            "host-address",
            "httphost",
            "http_host",
            "http-host",
            "hostname",
            "host_name",
            "host-name"
        ],
        "replacementType": "random",
        "replacement": "host[] # REVIEW : ",
        "field": "host",
        "possible_replacement": ["host", "ipv4", "ipv6", "fqdn"]
    },
    "ipv4": {
        "token": [
            "ip",
            "ipv4",
            "ipaddr",
            "ip_addr",
            "ip-addr",
            "ipaddress",
            "ip_address",
            "ip-address"
        ],
        "replacementType": "random",
        "replacement": "ipv4"
    },
    "ipv6": {
        "token": [
            "ipv6"
        ],
        "replacementType": "random",
        "replacement": "ipv6"
    },
    "hex": {
        "token": [
            "hex",
            "puid"
        ],
        "replacementType": "random",
        "replacement": "hex(20)"
    },
    "email": {
        "token": [
            "email",
            "e-mail",
            "e_mail",
            "mail",
            "mailid",
            "mail_id",
            "mail-id",
            "emailid",
            "email_id",
            "email-id",
            "emailaddr",
            "email_addr",
            "email-addr",
            "emailaddress",
            "email_address",
            "email-address"
        ],
        "replacementType": "random",
        "replacement": "email"
    },
    "mac": {
        "token": [
            "mac",
            "macaddr",
            "mac_addr",
            "mac-addr",
            "macaddress",
            "mac_address",
            "mac-address",
            "macname",
            "mac_name",
            "mac-name"
        ],
        "replacementType": "random",
        "replacement": "mac"
    }
}


FILE_MAPPING = {
    "ipv4": ["anomalous.ip_address.sample", "ip_address.sample", "webhosts.sample", "ip.sample", "ipaddress.sample"],
    "mac": ["anomalous.mac_address.sample", "mac_address.sample", "mac.sample", "remote_mac.sample"],
    "host": ["anomalous.hostname.sample", "hostname.sample", "linux.host.sample", "computer_name.sample", "host_name.sample"],
    "user": ["userName.sample", "mac_user.sample", "user_name.sample"],
    "dvc": ["dvc.sample", "dvc_ids.sample"],
    "url": ["uri.sample", "url.sample"],
    "email": ["email_address.sample"]
}
