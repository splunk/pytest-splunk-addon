"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
# import os
# import sys
#
# import ..log as log
#
# RELATIVE_SDK_PATH = os.path.join('contrib', 'splunk-sdk-python')
#
#
# def add_sdk_to_path():
#     """
#     Adds the SDK to the system path.
#     """
#     path = get_absolute_sdk_path()
#     sys.path.insert(0, path)
#
#
# def add_contrib_to_path():
#     """
#     Adds the splunk modules to the system path.
#     """
#     path = get_absolute_contrib_path()
#     sys.path.insert(0, path)
#
#
# def get_absolute_sdk_path():
#     """
#     Returns the absolute path of the SDK.
#
#     @return: The path
#     @rtype: str
#     """
#     path = os.path.join(__file__, '..', RELATIVE_SDK_PATH)
#     return os.path.abspath(path)
#
#
# def get_absolute_contrib_path():
#     """
#     Returns the absolute path of contrib.
#
#     @return: The path
#     @rtype: str
#     """
#     path = os.path.join(__file__, '..', 'contrib')
#     return os.path.abspath(path)
#
#
# add_sdk_to_path()
# add_contrib_to_path()
#
# __all__ = ['connector', 'exceptions', 'manager', 'misc', 'splunk',
#            'splunk_dowload', 'splunk_package', 'ssh', 'util']
#
# __version_info__ = ('1', '4', '14')
# __version__ = '.'.join(__version_info__)
