####################################
#create by exia.huangxy
#Extend Simple-Salesforce
####################################
from .. import requests
from . import Salesforce
from . import SFType
from . import util

DEFAULT_API_VERSION = '37.0'


'''
Enterprise API:
https://server-api.salesforce.com/services/Soap/c/27.0/orgId
Partner API:
https://server-api.salesforce.com/services/Soap/u/27.0/orgId
Metadata API:
https://server-api.salesforce.com/services/Soap/m/27.0/orgId
Note this is easy to get using the LoginResult.metadataServerUrl
Apex API:
https://server-api.salesforce.com/services/Soap/s/27.0
Tooling API:
https://server-api.salesforce.com/services/Soap/T/27.0/orgId
'''

class Soap(Salesforce):
    def __init__(
            self, username=None, password=None, security_token=None,
            session_id=None, instance=None, instance_url=None,
            organizationId=None, sandbox=False, version=DEFAULT_API_VERSION,
            proxies=None, session=None, client_id=None, settings=None):
        super(Soap, self).__init__(username, password, security_token,
            session_id, instance, instance_url,
            organizationId, sandbox, version,
            proxies, session, client_id)

        self.settings = settings

        self.soap_headers = {
            "Content-Type": "text/xml;charset=UTF-8",
            "Accept-Encoding": 'identity, deflate, compress, gzip',
            "SOAPAction": '""'
        }

        self.base_url = ('https://{instance}/services/data/v{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))
        self.apex_url = ('https://{instance}/services/apexrest/'
                         .format(instance=self.sf_instance))

        # Enterprise API:
        self.enter_api_url = ('https://{instance}/services/Soap/c/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))

        # Partner API:
        self.enter_api_url = ('https://{instance}/services/Soap/u/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))

        # Metadata API:
        self.meta_api_url = ('https://{instance}/services/Soap/m/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))

        # Apex API:
        self.apex_api_url = ('https://{instance}/services/Soap/s/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))

        # Tooling API:
        self.tooling_api_url = ('https://{instance}/services/Soap/T/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))


        print(self.base_url)
        print(self.apex_url)
        print(self.apex_api_url)
        print('------->')

    # get SObject by name
    def get_sobject(self, name):
        # fix to enable serialization
        # (https://github.com/heroku/simple-salesforce/issues/60)
        if name.startswith('__'):
            return super(Salesforce, self).__getattr__(name)

        return SFType(
            name, self.session_id, self.sf_instance, sf_version=self.sf_version,
            proxies=self.proxies, session=self.session)


    def execute_anonymous(self, apex_string):
        body = util.get_soap_anonymous_body(apex_string)
        request_body = util.create_apex_envelope(self.session_id, self.settings, body)

        try:
            
            # print(self.soap_url)
            # print(self.headers)
            # print(request_body)
            # response = requests.post(
            #             self.apex_api_url, request_body, verify=False, headers=self.soap_headers,
            #             proxies=self.proxies)
            response = self._soap_post(self.apex_api_url, request_body, self.soap_headers)
            # print(response)
            # print('response.text------->')
            # print(response.text)
            # print('response.content----->')
            # print(response.content)
            # print('response.status_code----->')
            # print(response.status_code)

        except requests.exceptions.RequestException as e:
            self.result = {
                "Error Message":  "Network connection timeout when issuing EXECUTE ANONYMOUS request",
                "success": False
            }
            return self.result

        # print('--->1')
        # session is expired ??
        if "INVALID_SESSION_ID" in response.text:
            return False
        content = response.content
        result = {"success": response.status_code < 399}
        # print('--->2')
        if result["success"]:
            response_result = util.getUniqueElementValueFromXmlString(response.text, "success")
            # print('--->3')
            if response_result == "false":
                response_compileProblem = util.getUniqueElementValueFromXmlString(response.text, "compileProblem")
                response_compiled = util.getUniqueElementValueFromXmlString(response.text, "compiled")
                response_column = util.getUniqueElementValueFromXmlString(response.text, "column")
                result["debugLog"] = "result : " + response_result
                result["debugLog"] += "\n\ncompiled : " + response_compiled
                result["debugLog"] += "\n\ncompileProblem : " + response_compileProblem
                result["debugLog"] += "\n\nerror column : " + response_column
            else:
                result["debugLog"] = util.getUniqueElementValueFromXmlString(response.text, "debugLog")
        else:
            # print('--->4')
            result["debugLog"] = util.getUniqueElementValueFromXmlString(response.text, "faultstring")

        print(result["debugLog"])
        return result


    def _soap_post(self, url, request_body, headers, **kwargs):
        result = requests.post(url, request_body, headers=headers, proxies=self.proxies, verify=False)
        if result.status_code >= 300:
            raise SoapException(result, result.status_code)
        return result

    def _soap_get(self, url, request_body="", headers="", **kwargs):
        result = requests.get(url, request_body, headers=headers, proxies=self.proxies, verify=False)
        # if result.status_code >= 300:
        #     raise SoapException(result, result.status_code)
        return result


class SoapException(Exception):

    def __init__(self, message, status_code=None):
        super(SoapException, self).__init__(message)
        self.status_code = status_code


