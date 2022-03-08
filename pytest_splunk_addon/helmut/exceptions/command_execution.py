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
class CommandExecutionFailure(RuntimeError):
    """
    Generic exception for when a Splunk command fails to execute.

    @ivar command: The command that failed.
    @type command: str
    @ivar code: The exit code.
    @type code: int
    @param stdout: The standard output.
    @type stdout: str
    @ivar stderr: The standard error output.
    @type stderr: str
    """

    def __init__(self, command="", code="", stdout="", stderr=""):
        # FAST-8061 Custom exceptions are not raised properly when used in Multiprocessing Pool
        """
        Creates a new exception.

        @param command: The command that failed.
        @type command: str
        @param code: The exit code.
        @type code: int
        @param stderr: The stderr output.
        @type stderr: str
        """
        self.command = command
        self.code = code
        self.stderr = stderr
        self.stdout = stdout

        super(CommandExecutionFailure, self).__init__(self._error_message)

    @property
    def _error_message(self):
        """
        The error message for this exception.

        Is built using L{command}, L{code}, L{stdout} and L{stderr}.

        @rtype: str
        """
        message = "Command {cmd} returned code {code}.\n"
        message += "############\nstdout: {stdout}\n"
        message += "############\nstderr: {stderr}"

        return message.format(
            cmd=self.command, code=self.code, stdout=self.stdout, stderr=self.stderr
        )
