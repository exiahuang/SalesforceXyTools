####################################
#create by exia.huangxy
####################################
"""Core classes and exceptions for Simple-Salesforce"""


# has to be defined prior to login import
DEFAULT_API_VERSION = '29.0'


import logging
import warnings
import json
from .. import requests

try:
    from urlparse import urlparse
except ImportError:
    # Python 3+
    from urllib.parse import urlparse
from .login import SalesforceLogin
# from .util import date_to_iso8601, SalesforceError
# from .util import *
from . import util


try:
    from collections import OrderedDict
except ImportError:
    # Python < 2.7
    from ordereddict import OrderedDict

#pylint: disable=invalid-name
logger = logging.getLogger(__name__)



# pylint: disable=too-many-instance-attributes
class SFSoap(object):
    """Salesforce Instance

    An instance of Salesforce is a handy way to wrap a Salesforce session
    for easy use of the Salesforce REST API.
    """
    # pylint: disable=too-many-arguments
    def __init__(
            self, username=None, password=None, security_token=None,
            session_id=None, instance=None, instance_url=None,
            organizationId=None, sandbox=False, version=DEFAULT_API_VERSION,
            proxies=None, session=None, client_id=None, settings=None):
        """Initialize the instance with the given parameters.

        Available kwargs

        Password Authentication:

        * username -- the Salesforce username to use for authentication
        * password -- the password for the username
        * security_token -- the security token for the username
        * sandbox -- True if you want to login to `test.salesforce.com`, False
                     if you want to login to `login.salesforce.com`.

        Direct Session and Instance Access:

        * session_id -- Access token for this session

        Then either
        * instance -- Domain of your Salesforce instance, i.e.
          `na1.salesforce.com`
        OR
        * instance_url -- Full URL of your instance i.e.
          `https://na1.salesforce.com

        Universal Kwargs:
        * version -- the version of the Salesforce API to use, for example
                     `29.0`
        * proxies -- the optional map of scheme to proxy server
        * session -- Custom requests session, created in calling code. This
                     enables the use of requests Session features not otherwise
                     exposed by simple_salesforce.

        """
        self.settings = settings

        # Determine if the user passed in the optional version and/or sandbox
        # kwargs
        self.sf_version = version
        self.sandbox = sandbox
        self.session = session or requests.Session()
        self.proxies = self.session.proxies
        # override custom session proxies dance
        if proxies is not None:
            if not session:
                self.session.proxies = self.proxies = proxies
            else:
                logger.warning(
                    'Proxies must be defined on custom session object, '
                    'ignoring proxies: %s', proxies
                )

        # Determine if the user wants to use our username/password auth or pass
        # in their own information
        if all(arg is not None for arg in (
                username, password, security_token)):
            self.auth_type = "password"

            # Pass along the username/password to our login helper
            self.session_id, self.sf_instance = SalesforceLogin(
                session=self.session,
                username=username,
                password=password,
                security_token=security_token,
                sandbox=self.sandbox,
                sf_version=self.sf_version,
                proxies=self.proxies,
                client_id=client_id)

        elif all(arg is not None for arg in (
                session_id, instance or instance_url)):
            self.auth_type = "direct"
            self.session_id = session_id

            # If the user provides the full url (as returned by the OAuth
            # interface for example) extract the hostname (which we rely on)
            if instance_url is not None:
                self.sf_instance = urlparse(instance_url).hostname
            else:
                self.sf_instance = instance

        elif all(arg is not None for arg in (
                username, password, organizationId)):
            self.auth_type = 'ipfilter'

            # Pass along the username/password to our login helper
            self.session_id, self.sf_instance = SalesforceLogin(
                session=self.session,
                username=username,
                password=password,
                organizationId=organizationId,
                sandbox=self.sandbox,
                sf_version=self.sf_version,
                proxies=self.proxies,
                client_id=client_id)

        else:
            raise TypeError(
                'You must provide login information or an instance and token'
            )

        if self.sandbox:
            self.auth_site = 'https://test.salesforce.com'
        else:
            self.auth_site = 'https://login.salesforce.com'

        self.headers = {
            "Content-Type": "text/xml;charset=UTF-8",
            "Accept-Encoding": 'identity, deflate, compress, gzip',
            "SOAPAction": '""'
        }

        self.base_url = ('https://{instance}/services/data/v{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))
        self.apex_url = ('https://{instance}/services/apexrest/'
                         .format(instance=self.sf_instance))

        self.soap_url = ('https://{instance}/services/Soap/s/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))
        # self.soap_url = settings["soap_login_url"]


    def execute_anonymous(self, apex_string):
        # apex_string = quoteattr(apex_string).replace('"', '')
        body = util.get_soap_anonymous_body(apex_string)
        # request_body = self.create_apex_envelope(body)
        request_body = util.create_apex_envelope(self.session_id, self.settings, body)


        try:
            
            # print(self.soap_url)
            # print(self.headers)
            # print(request_body)
            response = requests.post(
                        self.soap_url, request_body, verify=False, headers=self.headers,
                        proxies=self.proxies)
            # print(response)
            print(response.text)
            print(response.content)
            print(response.status_code)

        except requests.exceptions.RequestException as e:
            self.result = {
                "Error Message":  "Network connection timeout when issuing EXECUTE ANONYMOUS request",
                "success": False
            }
            return self.result

        # session is expired ??
        if "INVALID_SESSION_ID" in response.text:
            return False
        content = response.content
        result = {"success": response.status_code < 399}
        result["debugLog"] = util.getUniqueElementValueFromXmlString(response.text, "debugLog")
        return result

