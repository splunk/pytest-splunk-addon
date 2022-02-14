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
import sys
import time
import string

try:
    import py
except ImportError:
    # We're assuming here that pytest is unavailable
    print("Pytest unavailable, running tests in dev context")

TIMEOUT = 120


class SearchUtilException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class SearchUtil(object):
    def __init__(self, jobs, logger):
        """
        Constructor of the SearchUtil object.
        """
        self.logger = logger
        self.jobs = jobs

    def failTest(self, message):
        """
        Fail the test appropriately, QA uses pytest. Dev gets a generic message
        """
        if "pytest" in list(sys.modules.keys()):
            py.test.fail(message)
        else:
            raise SearchUtilException(message)

    def checkQueryCount(self, query, targetCount, interval=15, retries=4, max_time=120):
        self.logger.debug("query is %s", query)
        tryNum = 0
        while tryNum <= retries:
            job = self.jobs.create(query, max_time=max_time)
            job.wait(max_time)
            result_count = job.get_result_count()
            if result_count == targetCount:
                return True
            else:
                self.logger.info(
                    "Count of results is not as expected, it is %d. Expected %d",
                    result_count,
                    targetCount,
                )
                tryNum += 1
                time.sleep(interval)

        return False

    def checkQueryCountIsGreaterThanZero(
        self, query, interval=15, retries=4, max_time=120
    ):
        self.logger.debug("query is %s", query)
        tryNum = 0
        while tryNum <= retries:
            job = self.jobs.create(query, auto_finalize_ec=200, max_time=max_time)
            job.wait(max_time)
            result_count = len(job.get_results())
            if result_count > 0:
                self.logger.debug("Count of results is > 0, it is:%d", result_count)
                return True
            else:
                self.logger.debug("Count of results is 0")
                tryNum += 1
                time.sleep(interval)
        return False

    def deleteEventsFromIndex(self, index_name="*", max_wait_time=120):
        """
        Hides events belonging to specified index from SPL Search using ``| delete`` command.

        Args:
            index_name: Name of the index to delete events from.
            max_wait_time: Amount of time job can wait to finish.
        """
        query = f"search index={index_name} | delete"
        self.logger.debug("query is %s", query)
        try:
            job = self.jobs.create(query)
            job.wait(max_wait_time)
            self.logger.info("Successfully deleted old events")

        except Exception as e:
            self.logger.debug("CAREFUL - Could not delete old events!")
            self.logger.debug(e)

    def checkQueryCountIsZero(self, query, max_time=120):
        self.logger.debug("query is %s", query)
        tryNum = 0

        job = self.jobs.create(query, auto_finalize_ec=200, max_time=max_time)
        job.wait(max_time)
        result_count = len(job.get_results())

        if result_count == 0:
            self.logger.debug("Count of results is 0")
            return True, None
        else:
            self.logger.debug("Count of results is > 0, it is:%d", result_count)
            return False, job.get_results()

    def get_search_results(self, query, max_time=120):
        """
            Execute a search query
        Args:
            query (str): query string for Splunk Search
            max_time: Amount of time job can wait to finish.
        Returns:
            events that match the query
        """

        self.logger.debug("query is %s", query)
        try:
            job = self.jobs.create(query, auto_finalize_ec=120, max_time=max_time)
            job.wait(max_time)
            return job.get_results()
        except Exception as e:
            self.logger.debug("Errors when executing search!!!")
            self.logger.debug(e)

    def wrapLogOutput(self, msg, actual, expected, errors, level="debug"):
        """Simple wrapper method for showing expected and actual output
        in the debug log. Pass in level to adjust level from default (debug)
        to error or warning.
        """

        errOutput = string.Template(
            """${msg}
            ===ACTUAL=====
            ${actual}
            ===EXPECTED===
            ${expected}
            ===ERRORS=====
            ${errors}\n"""
        )

        output = errOutput.substitute(
            {"msg": msg, "actual": actual, "expected": expected, "errors": errors}
        )

        # This is solely so the definition of errOutput above can look good
        # while making the debug output readable.
        if level == "debug":
            self.logger.debug(
                "\n".join(map(str.strip, list(map(str, output.splitlines()))))
            )
        elif level == "warning":
            self.logger.warning(
                "\n".join(map(str.strip, list(map(str, output.splitlines()))))
            )
        elif level == "error":
            self.logger.error(
                "\n".join(map(str.strip, list(map(str, output.splitlines()))))
            )
        else:
            # Whatever, if level specified badly just print as debug
            self.logger.debug(
                "\n".join(map(str.strip, list(map(str, output.splitlines()))))
            )

    def getFieldValuesDict(self, query, interval=15, retries=4):

        """Execute a query and check for a matching set (not necessarily
        complete) of output fields, and secondarily for a minimum
        number of results.
        """

        tryNum = 0
        status = False

        while tryNum <= retries and not status:

            job = self.jobs.create(query, max_time=60)
            job.wait(240)
            result_count = len(job.get_results())
            results = job.get_results()
            messages = job.get_messages()

            if result_count > 0:
                # we need to cast to str before int because it's a ResultField
                # which can't be cast directly to str...
                keys = list(map(str, list(results[0].keys())))
                print(keys)
                values = list(map(str, list(results[0].values())))
                print(values)
                dictionary = dict(list(zip(keys, values)))
                print(dictionary)
                return dictionary
            else:
                self.wrapLogOutput(
                    msg="Zero results from search:",
                    actual="",
                    expected="greater than 0",
                    errors="\n".join(messages),
                )

            if not status:
                tryNum += 1
                time.sleep(interval)

        return status

    def getFieldValuesList(self, query, interval=15, retries=4):
        """
        Get list of results from the query. Where each result will be
        a dictionary. The search job will retry at given interval if
        no results found.

        Args:
            query (str): query to search on Splunk instance
            interval (int): at what interval each retry should be made
            retries (int): number of retries to make if no results found
        """

        tryNum = 0
        status = False

        while tryNum <= retries and not status:
            job = self.jobs.create(query, max_time=60)
            job.wait(240)
            results = job.get_results(offset=0, count=4000)
            result_count = len(results)
            messages = job.get_messages()

            if result_count > 0:
                for each_result in results:
                    keys = list(map(str, list(each_result.keys())))
                    values = list(map(str, list(each_result.values())))
                    yield dict(list(zip(keys, values)))
                break
            else:
                self.wrapLogOutput(
                    msg="Zero results from search:",
                    actual="",
                    expected="greater than 0",
                    errors="\n".join(messages),
                )

            if not status:
                tryNum += 1
                time.sleep(interval)

        return status
