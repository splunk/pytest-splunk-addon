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
class UnsupportedConnectorError(BaseException):
    """
    Raised in manager_utils during creation of a Manager when the class type
    of the new Manager object is being determined. When mapping the class type
    of the connector currently in use to the appropriate and corresponding
    subclass of Manager associated with that connector type, this
    exception will be raised if the Manager has no subclasses associated with
    that connector type.

    Also raised during creation of a connector for a splunk instance if
    attempting to create a connector type which isn't supported or doesnt exist
    """

    def __init__(self, message=None):
        message = message or "The specified connector is not supported"
        super(UnsupportedConnectorError, self).__init__(message)
