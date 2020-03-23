from future import standard_library

standard_library.install_aliases()
from builtins import range
import httplib2
import logging
import time
import random
from io import BytesIO
from http.client import ResponseNotReady

RETRIES = 3


def sdk_request_adapter(url, message, **kwargs):
    """
    :param url: the URL to make the request to (including any query and fragment sections)
    :param message: a dictionary with the following keys:
        - method: The method for the request, typically ``GET``, ``POST``, or ``DELETE``.
        - headers: A list of pairs specifying the HTTP headers (for example: ``[('key': value), ...]``).
        - body: A string containing the body to send with the request (this string
          should default to '').
    :param kwargs: not used
    :return: response_dict, a dictionary with the following keys:
        - status: An integer containing the HTTP status code (such as 200 or 404).
        - reason: The reason phrase, if any, returned by the server.
        - headers: A list of pairs containing the response headers (for example, ``[('key': value), ...]``).
        - body: A stream-like object supporting ``read(size=None)`` and ``close()`` methods to get the body of the response.
    """
    method = message.get("method", "GET").upper()
    body = message.get("body", "") if method == "POST" else None
    headers = dict(message.get("headers", []))
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    for i in range(RETRIES):
        try:
            resp, content = h.request(url, method=method, body=body, headers=headers)
            break
        except ResponseNotReady:
            # splunk restart is still in progress
            time.sleep(30)
        except Exception as ex:  # noqa: E722
            logging.getLogger("..connector").exception(
                "request failed, url=%s, attempts=%s", url, i + 1
            )
            if i == RETRIES - 1 or not _is_retry_safe(method, url):
                raise
            else:
                # intermediate network error
                time.sleep(random.randint(5, 17))

    return {
        "status": resp.status,
        "reason": resp.reason,
        "headers": resp,
        "body": BytesIO(content),
    }


def _is_retry_safe(method, url):
    if method in ("GET", "HEAD", "DELETE", "PUT"):
        # idempotent request
        return True
    elif method == "POST":
        for rest_url in ["/auth/login"]:
            if rest_url in url:
                return True
    return False
