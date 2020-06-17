import socket
from time import sleep
import os
#import concurrent.futures
from base_event_ingestor import EventIngestor

#THREAD_POOL = 3
class SC4SEventIngestor(EventIngestor):
    """
    Class to Ingest Events via sc4s
    """

    def __init__(self, required_configs):
        """
        init method for the class

        Args:

            required_configs(dict): {
                splunk_host(str): Host address where events are to be ingested
                sc4s_port(int): Port number of the above host address
            }
        """

        self.splunk_host = required_configs['splunk_host']
        self.sc4s_port = required_configs['sc4s_port']

    def ingest(self, event):
        """
        Ingests events in the splunk via sc4s (Single/Multiple Events)

        Args:
            event(object): Events with "\n" as separator
            
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.splunk_host, self.sc4s_port)
        tried = 0
        while True:
            try:
                sock.connect(server_address)
                break
            except Exception as e:
                tried += 1
                if tried > 90:
                    raise e
                sleep(1)
        #sendall sends the entire buffer you pass or throws an exception.
        sock.sendall(str.encode(event.event))

    # with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
    #     #events(str) with "\n" as separator
    #     event = "Mar 25 13:53:24 xxxxxx-xxxx STP: VLAN 125 Port 1/1/24 STP State -> FORWARDING (DOT1wTransition)\nOct 8 15:00:25 DEVICENAME time=1570561225|hostname=devicename|severity=Informational|confidence_level=Unknown|product=IPS|action=Drop|ifdir=inbound|ifname=bond2|loguid={0x5d9cdcc9,0x8d159f,0x5f19f392,0x1897a828}|origin=1.1.1.1|time=1570561225|version=1|attack=Streaming Engine: TCP Segment Limit Enforcement|attack_info=TCP segment out of maximum allowed sequence. Packet dropped.|chassis_bladed_system=[ 1_3 ]|dst=10.10.10.10|origin_sic_name=CN=something_03_local,O=devicename.domain.com.p7fdbt|performance_impact=0|protection_id=tcp_segment_limit|protection_name=TCP Segment Limit Enforcement|protection_type=settings_tcp|proto=6|rule=393|rule_name=10.384_..|rule_uid={9F77F944-8DD5-4ADF-803A-785D03B3A2E8}|s_port=46455|service=443|smartdefense_profile=Recommended_Protection_ded9e8d8ee89d|src=1.1.1.2|\nRT_UTM: WEBFILTER_URL_PERMITTED: WebFilter: ACTION=\"URL Permitted\" 192.168.32.1(62054)->1.1.1.1(443) CATEGORY=\"Enhanced_Information_Technology\" REASON=\"BY_PRE_DEFINED\" PROFILE=\"UTM-Wireless-Profile\" URL=ent-shasta-rrs.symantec.com OBJ=/ username N/A roles N/A"
    #     for msg in event.split("\n"):
    #         executor.submit(ingest, msg, self.splunk_host, self.sc4s_port)