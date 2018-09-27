"""
Create by exia.huangxy
Extend Simple-Salesforce
https://github.com/exiahuang
"""

try:
    from SalesforceXyTools import requests
except ImportError:
    import requests
from . import Salesforce
from . import SFType
from . import util
from . import soap_envelopes
from . import xmltodict
import xml.dom.minidom
from .myconsole import MyConsole
import time
import os
import base64
import json
from datetime import datetime

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
            proxies=None, session=None, client_id=None, myconsole=None):
        super(Soap, self).__init__(username, password, security_token,
            session_id, instance, instance_url,
            organizationId, sandbox, version,
            proxies, session, client_id)

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

        if myconsole:
            self.myconsole = myconsole
        else:
            self.myconsole = MyConsole()

        self.myconsole.debug('>>>init Soap api')
        self.myconsole.debug(self.base_url)
        self.myconsole.debug(self.apex_url)
        self.myconsole.debug(self.apex_api_url)
        self.myconsole.debug('>>>init end')

    # get SObject by name
    def get_sobject(self, name):
        # fix to enable serialization
        # (https://github.com/heroku/simple-salesforce/issues/60)
        if name.startswith('__'):
            return super(Salesforce, self).__getattr__(name)

        return SFType(
            name, self.session_id, self.sf_instance, sf_version=self.sf_version,
            proxies=self.proxies, session=self.session)


    def execute_anonymous(self, apex_string, debug_levels):
        body = util.get_soap_anonymous_body(apex_string)
        request_body = util.create_apex_envelope(self.session_id, debug_levels, body)

        try:
            response = self._soap_post(self.apex_api_url, request_body, self.soap_headers)
            # result = requests.post(url, request_body, headers=headers, proxies=self.proxies, verify=False)
            # print('>'*80)
            # print(response.status_code)
            # print(response.text)
            # self.myconsole.debug(response.status_code)
        except requests.exceptions.RequestException as e:
            self.result = {
                "Error Message":  "Network connection timeout when issuing EXECUTE ANONYMOUS request",
                "success": False
            }
            return self.result

        if "INVALID_SESSION_ID" in response.text:
            return False

        result = {"success": response.status_code < 399}
        if result["success"]:
            response_result = util.getUniqueElementValueFromXmlString(response.text, "success")
            if response_result == "false":
                response_compileProblem = self._get_xml_content(response.text, "compileProblem")
                response_compiled = self._get_xml_content(response.text, "compiled")
                response_column = self._get_xml_content(response.text, "column")
                result["debugLog"] = "result : " + response_result
                result["debugLog"] += "\n\ncompiled : " + response_compiled
                result["debugLog"] += "\n\ncompileProblem : " + response_compileProblem.replace('<compileProblem xsi:nil="true"/>', '')
                result["debugLog"] += "\n\nerror column : " + response_column
                result["debugLog"] += "\n\nlog : \n\n" + self._get_xml_content(response.text, "debugLog")
            else:
                result["debugLog"] = self._get_xml_content(response.text, "debugLog")
        else:
            result["debugLog"] = self._get_xml_content(response.text, "faultstring")

        # self.myconsole.debug(result["debugLog"])
        return result

    def _get_xml_content(self, xml, tag):
        try:
            return util.getUniqueElementValueFromXmlString(xml, tag)
        except Exception as ex:
            return ''
            pass

    def _soap_post(self, url, request_body, headers, **kwargs):
        self.myconsole.debug('>>>start soap post : ' + url)
        result = requests.post(url, request_body, headers=headers, proxies=self.proxies, verify=False)
        self.myconsole.debug(request_body)
        self.myconsole.debug(headers)
        self.myconsole.debug('>>>response:')
        self.myconsole.debug(result)
        self.myconsole.debug(result.status_code)
        # self.myconsole.debug(result.text)
        # self.myconsole.debug(result.content)
        
        if result.status_code >= 300:
            print(result.status_code)
            print(result.text)
            raise SoapException(result, result.status_code)
        return result

    def _soap_get(self, url, request_body="", headers="", **kwargs):
        result = requests.get(url, request_body, headers=headers, proxies=self.proxies, verify=False)
        # if result.status_code >= 300:
        #     raise SoapException(result, result.status_code)
        return result

class MetadataApi(Soap):
    def __init__(
            self, username=None, password=None, security_token=None,
            session_id=None, instance=None, instance_url=None,
            organizationId=None, sandbox=False, version=DEFAULT_API_VERSION,
            proxies=None, session=None, client_id=None, myconsole=None):
        super(MetadataApi, self).__init__(username, password, security_token,
            session_id, instance, instance_url,
            organizationId, sandbox, version,
            proxies, session, client_id, myconsole)
        self.describe_metadata_response = None

    def _doSoapQuery(self, name, request_body):
        self.myconsole.debug('>>>retrieve')
        try:
            response = self._soap_post(self.meta_api_url, request_body, self.soap_headers)
            result = xmltodict.parse(response.content)
            result = result["soapenv:Envelope"]["soapenv:Body"][name]
            if not result or "result" not in result: 
                return {}
            result = result["result"]
            return result
        except requests.exceptions.RequestException as e:
            self.result = {
                "Name":  name,
                "Error Message":  "Network connection timeout when issuing EXECUTE ANONYMOUS request",
                "success": False
            }
            return self.result

    def _doSoapQueryList(self, name, request_body):
        self.myconsole.debug('>>>doSoapQueryList')
        try:
            response = self._soap_post(self.meta_api_url, request_body, self.soap_headers)
            result = xmltodict.parse(response.content)
            result = result["soapenv:Envelope"]["soapenv:Body"][name]
            if not result or "result" not in result: 
                return []
            result = result["result"]
            return result
        except requests.exceptions.RequestException as e:
            self.result = {
                "Name":  name,
                "Error Message":  "Network connection timeout when issuing EXECUTE ANONYMOUS request",
                "success": False
            }
            return self.result

    def packageTypeList(self, retrive_metadata_objects=None):
        metadata_types = []
        if not retrive_metadata_objects:
            describeMetadataResult = self.describeMetadata()
            retrive_metadata_objects = describeMetadataResult["metadataObjects"]
    
        for metaObj in retrive_metadata_objects:
            if metaObj["inFolder"] == "false":
                if metaObj["xmlName"] == "StandardValueSet":
                    metadata_types.append({
                        "name" : "StandardValueSet",
                        "members" : soap_envelopes.get_StandardValueSet(self.sf_version)
                    })
                elif metaObj["xmlName"] == "CustomObject":
                    metadata_types.append({
                        "name" : metaObj["xmlName"],
                        "members" : self._getCustomObjectMembers()
                    })
                else:
                    metadata_types.append({
                        "name" : metaObj["xmlName"],
                        "members" : ["*"]
                    })
            else:
                members = []
                query_option_list = []
                for folder in self.listFolder(metaObj["xmlName"]):
                    members.append(folder['fullName'])
                    query_option_list.append({
                        "metadata_type" : metaObj["xmlName"],
                        "folder" : folder['fullName']
                    })
                self.myconsole.debug('>>>list infolder : ' + metaObj["xmlName"])
                if query_option_list is not None and len(query_option_list) > 0:
                    members.extend([meta["fullName"] for meta in self.listMetadata(query_option_list)]) 
                metadata_types.append({
                    "name" : metaObj["xmlName"],
                    "members" : members
                })
        return metadata_types
    
    def _getCustomObjectMembers(self):
        return [str(sobj["name"]) for sobj in self.describe()["sobjects"]]

    def buildPackageXml(self, retrive_metadata_objects=None):
        packagexml_types = ""
        for package_type in self.packageTypeList(retrive_metadata_objects):
            members = ["""        <members>{member}</members>""".format(member=member) for member in package_type["members"]]
            packagexml_types = packagexml_types + soap_envelopes.PACKAGEXML_TYPE.format(members='\n'.join(members),name=package_type["name"])
        return soap_envelopes.PACKAGE_XML.format(types=packagexml_types, version=self.sf_version)

    def listAllMetadata(self):
        listAllMetadataResult = []
        metadata_types = []
        describeMetadataResult = self.describeMetadata()
        if "metadataObjects" in describeMetadataResult:
            for metaObj in describeMetadataResult["metadataObjects"]:
                if metaObj["inFolder"] == "false":
                    if metaObj["xmlName"] == "StandardValueSet":
                        continue
                    else:
                        metadata_types.append({
                                "metadata_type" : metaObj["xmlName"],
                                "folder" : ""
                        })
                else:
                    query_option_list = []
                    for folder in self.listFolder(metaObj["xmlName"]):
                        query_option_list.append({
                            "metadata_type" : metaObj["xmlName"],
                            "folder" : folder['fullName']
                        })
                    if query_option_list is not None and len(query_option_list) > 0:
                        listAllMetadataResult.extend(self.listMetadata(query_option_list))
        listAllMetadataResult.extend(self.listMetadata(metadata_types))
        return listAllMetadataResult

    def getAllMetadataMap(self):
        allMetadataMap = {}
        for meta in self.listAllMetadata():
            type = meta["type"]
            meta_dict = allMetadataMap[type] if type in allMetadataMap else {}
            meta_dict[meta["fileName"]] = meta
            allMetadataMap[type] = meta_dict
        return allMetadataMap

    # https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_folder.htm
    def listFolder(self,type_name):
        self.myconsole.debug('>>>listFolder')
        if type_name == "EmailTemplate":
            metadata_type = "EmailFolder"
        elif "Folder" in type_name:
            metadata_type = type_name
        else:
            metadata_type = type_name + "Folder"
        self.myconsole.debug(metadata_type)
        folders = self.listMetadata([{
                        "metadata_type" : metadata_type,
                        "folder" : ""
                    }])
        self.myconsole.debug('>>>listFolderResult:')
        self.myconsole.debug(folders)
        return folders
    
    def listMetadata(self, query_option_list):
        listAllMetadataResult = []
        if len(query_option_list) > 3 :
            for query_option_list_3 in util.chunks(query_option_list, 3):
                listAllMetadataResult.extend(self._listMetadataLimit(query_option_list_3))
        else:
            listAllMetadataResult.extend(self._listMetadataLimit(query_option_list))
        return listAllMetadataResult

    # query_option_list : max len is 3
    def _listMetadataLimit(self, query_option_list):
        if query_option_list is None or len(query_option_list) == 0:
            return []
        # self.sf_version
        request_body = soap_envelopes.get_list_metadata_envelope(session_id=self.session_id, query_option_list=query_option_list,api_version=self.sf_version)
        result = self._doSoapQueryList("listMetadataResponse", request_body)
        print(result)
        if not isinstance(result, list): 
            result = []
        return result

    def describeMetadata(self):
        if self.describe_metadata_response:
            return self.describe_metadata_response
        request_body = soap_envelopes.get_describe_metadata_envelope(session_id=self.session_id, api_version=self.sf_version)
        self.describe_metadata_response = self._doSoapQuery("describeMetadataResponse", request_body)
        return self.describe_metadata_response

    def retrieve(self, retrive_metadata_objects=None):
        request_body = soap_envelopes.get_retrieve_unpackaged_envelope(session_id=self.session_id, package_type_list=self.packageTypeList(retrive_metadata_objects), api_version=self.sf_version)
        """start retreive
            result["id"]
            result["done"]
            result["state"]
        """
        result = self._doSoapQuery("retrieveResponse", request_body)
        is_done = result["done"]
        process_id = result["id"]
        while is_done == 'false':
            result = self.checkRetrieveStatus(process_id)
            if is_done == 'false':
                if result["status"] != "Succeeded":
                    self.myconsole.debug(result)
                self.myconsole.log("retrieve status=%s, id=%s, please wait. " % (result["status"], result["id"]))
            if not result or not result["success"]:
                self.result = result
                return self.result
                # result["state"] if self.api_version < 31 else result["status"]
            status = result["status"]
            is_done = result["done"]
            sleep_time = 3
            time.sleep(sleep_time)

        if status == "Failed":
            self.result = {
                "success": False,
                "Error Message": result["errorMessage"]
            }
            return self.result
        
        self.result = result
        return result

    def retrieveZip(self, save_dir="", zip_file_name="package.zip", retrive_metadata_objects=None):
        result = self.retrieve(retrive_metadata_objects)
        if "zipFile" in result:
            save_full_path = os.path.join(save_dir, zip_file_name)
            file_path, file_name = os.path.split(save_full_path)
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            with open(save_full_path, "wb") as fo:
                fo.write(base64.b64decode(result["zipFile"]))
                fo.close()
            return save_full_path
        return None

    def unzipfile(self, zipfile_path, extract_to, src_dir="src"):
        import zipfile
        zip_ref = zipfile.ZipFile(zipfile_path, 'r')
        zip_ref.extractall(extract_to)
        os.rename(os.path.join(extract_to, "unpackaged"), os.path.join(extract_to, src_dir))

    def checkRetrieveStatus(self, process_id):
        # self.doSoapQuery
        request_body = soap_envelopes.get_check_retrieve_status(session_id=self.session_id, process_id=process_id)
        return self._doSoapQuery("checkRetrieveStatusResponse", request_body)
    
    """start retreive
        result["id"]
        result["done"]
        result["state"]
    """
    def startRetrieve(self):
        request_body = soap_envelopes.get_retrieve_unpackaged_envelope(session_id=self.session_id, package_type_list=self.packageTypeList(), api_version=self.sf_version)
        return self._doSoapQuery("retrieveResponse", request_body)

    # def updateMetadata(self):
    #     self.myconsole.debug('>>>updateMetadata')

class ToolingApi(Salesforce):
    def __init__(
            self, username=None, password=None, security_token=None,
            session_id=None, instance=None, instance_url=None,
            organizationId=None, sandbox=False, version=DEFAULT_API_VERSION,
            proxies=None, session=None, client_id=None, myconsole=None):
        super(ToolingApi, self).__init__(username, password, security_token,
            session_id, instance, instance_url,
            organizationId, sandbox, version,
            proxies, session, client_id)
        # Tooling API:
        self.tooling_api_url = ('https://{instance}/services/Soap/T/{version}/'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))
        if myconsole:
            self.myconsole = myconsole
        else:
            self.myconsole = MyConsole()

    def getMetadata(self, metadata_type, id):
        url = self.base_url + 'sobjects/' + metadata_type + '/' + id
        status_code, result = self._call_api(method="GET", url=url, data=None)
        return status_code, result

    def createMetadata(self, type, post_body):
        url = self.base_url + 'sobjects/' + type
        status_code, result = self._call_api(method="POST", url=url, data=post_body)
        self.myconsole.debug(result)
        return status_code, result

    def deleteMetadata(self, metadata_type, id):
        url = self.base_url + 'sobjects/' + metadata_type + '/' + id
        status_code, result = self._call_api(method="DELETE", url=url, data=None, return_type='text')
        self.myconsole.debug(result)
        if status_code >= 300:
            self.myconsole.debug(result)
        else:
            self.myconsole.debug('>>>delete OK')
            self.myconsole.debug(result)
        return status_code, result

    def updateMetadata(self, metadata_type, id, body):
        # create MetadataContainer
        MetadataContainerId = self._createMetadataContainer(id)
        if not MetadataContainerId:
            self.myconsole.debug("create MetadataContainer error!")
            return

        # create ApexClassMember
        ApexClassMemberId = self._createMetadataMember(metadata_type, MetadataContainerId, id, body)
        if not ApexClassMemberId:
            self.myconsole.debug("create ApexClassMember error!")
            return

        # create ContainerAsyncRequest
        containerAsyncRequestId = self._createContainerAsyncRequest(MetadataContainerId, "false")
        if not containerAsyncRequestId:
            self.myconsole.debug("create ContainerAsyncRequest error!")
            return

        # check ContainerAsyncRequest Status
        ContainerAsyncRequest_status_code, ContainerAsyncRequest_status = self._checkContainerAsyncRequestStatue(containerAsyncRequestId)
        self.myconsole.debug(">>>check ContainerAsyncRequest Status")
        self.myconsole.debug(ContainerAsyncRequest_status)

        # delete MetadataContainer
        self.myconsole.debug('>>>delete MetadataContainer')
        url=self.base_url + 'tooling/sobjects/MetadataContainer/' + MetadataContainerId
        status_code, result = self._call_api(method="DELETE", url=url, data=None, return_type='text')
        self.myconsole.debug(status_code)
        self.myconsole.debug(result)
        
        result = {
            "status_code" : ContainerAsyncRequest_status_code,
            "is_success" : ContainerAsyncRequest_status["State"] == "Completed",
            "error_msg" : ContainerAsyncRequest_status["ErrorMsg"] if "ErrorMsg" in ContainerAsyncRequest_status else ""
        }

        result.update(self._getComponentFailures(ContainerAsyncRequest_status))

        return result

    def createTrigger(self, tableEnumOrId, name, body):
        params = {
            'tableEnumOrId' : tableEnumOrId,
            'name' : name,
            'body' : body
        }
        return self.createMetadata("ApexTrigger", params)
    
    def createApexComponent(self, MasterLabel, name, markup):
        params = {
                    'MasterLabel' : MasterLabel,
                    'name' : name,
                    'markup' : markup
                }
        return self.createMetadata("ApexComponent", params)

    def createApexPage(self, MasterLabel, name, markup):
        params = {
                    'MasterLabel' : MasterLabel,
                    'name' : name,
                    'markup' : markup
                }
        return self.createMetadata("ApexPage", params)

    def createApexClass(self, name, body):
        params = {
            'name' : name,
            'body' : body
        }
        return self.createMetadata("ApexClass", params)

    def deleteApexClass(self, id):
        return self.deleteMetadata("ApexClass", id)

    def getApexClass(self, id):
        url = self.base_url + 'sobjects/ApexClass/' + id
        status_code, result = self._call_api(method="GET", url=url, data=None)
        return status_code, result

    def updateApexClass(self, id, body):
        self.updateMetadata("ApexClass", id, body)

    def runTestAsynchronous(self, id_list):
        url = self.base_url + "tooling/runTestsAsynchronous/?classids=" + ",".join(id_list)
        status_code, result = self._call_api(method="GET", url=url, data=None)
        return status_code, result

    def runTestSynchronous(self, id_list):
        url = self.base_url + "tooling/runTestsSynchronous"
        test_param = [ {"classId" : id} for id in id_list ]
        params = { "tests":test_param }
        status_code, result = self._call_api(method="POST", url=url, data=params)
        return status_code, result
    
    def getLog(self, id):
        url = self.base_url + "sobjects/ApexLog/" + id + "/Body"
        status_code, result = self._call_api(method="GET", url=url, data=None, return_type='text')
        return status_code, result

    def toolingQuery(self, queryStr):
        url = self.base_url + "tooling/query"
        params = {'q': queryStr}
        status_code, result = self._call_api(method="GET", url=url, data=None, params=params)
        return status_code, result

    def _getComponentFailures(self, ContainerAsyncRequest_status):
        try:
            if ContainerAsyncRequest_status["State"] == "Failed":
                msg = ContainerAsyncRequest_status["DeployDetails"]["componentFailures"][0]
                return {
                    "lineNumber" : msg["lineNumber"],
                    "columnNumber" : msg["columnNumber"],
                    "problemType" : msg["problemType"],
                    "problem" : msg["problem"]
                }
        except Exception as ex:
            self.myconsole.debug(ex)
            pass
        return {
                "lineNumber" : "",
                "columnNumber" : "",
                "problemType" : "",
                "problem" : ""
        }

    def _createMetadataContainer(self, id):
        params = {
            "Name" : id + "_" + datetime.now().strftime("%m%d%H%M%S")
        }
        url = self.base_url + 'tooling/sobjects/MetadataContainer'
        status_code, result = self._call_api(method="POST", url=url, data=params)
        self.myconsole.debug(">>>create MetadataContainer object")
        self.myconsole.debug(result)
        MetadataContainerId = ""
        if "success" in result and result["success"]:
            MetadataContainerId = result["id"]
        return MetadataContainerId

    def _createMetadataMember(self, MetadataType, MetadataContainerId, ContentEntityId, body):
        params = {
            "MetadataContainerId" : MetadataContainerId,
            "ContentEntityId" : ContentEntityId,
            "Body" : body
        }
        url = self.base_url + 'tooling/sobjects/' + MetadataType + 'Member'
        status_code, result = self._call_api(method="POST", url=url, data=params)
        self.myconsole.debug('>>>create %sMember' % MetadataType)
        self.myconsole.debug(result)
        memberId = ""
        if "success" in result and result["success"]:
            memberId = result["id"]
        return memberId

    def _createApexClassMember(self, MetadataContainerId, ContentEntityId, body):
        self._createMetadataMember("ApexClass", MetadataContainerId, ContentEntityId, body)

    def _createContainerAsyncRequest(self, MetadataContainerId, isCheckOnly):
        params = {
            "MetadataContainerId" : MetadataContainerId,
            "isCheckOnly": isCheckOnly
        }
        containerAsyncRequest_url = self.base_url + 'tooling/sobjects/containerAsyncRequest'
        status_code, result = self._call_api(method="POST", url=containerAsyncRequest_url, data=params)
        self.myconsole.debug('>>>create containerAsyncRequest')
        self.myconsole.debug(result)
        containerAsyncRequestId = ""
        if "success" in result and result["success"]:
            containerAsyncRequestId = result["id"]
        return containerAsyncRequestId

    def _checkContainerAsyncRequestStatue(self, containerAsyncRequestId):
        check_status_url = self.base_url + 'tooling/sobjects/containerAsyncRequest/' + containerAsyncRequestId
        status_code, result = self._call_api(method="GET", url=check_status_url, data=None)
        while result["State"] == "Queued":
            time.sleep(2)
            self.myconsole.log("check ContainerAsyncRequest Status : please wait...")
            status_code, result = self._call_api(method="GET", url=check_status_url, data=None)
            self.myconsole.debug(result['State'])
        return status_code, result


class SoapException(Exception):

    def __init__(self, message, status_code=None):
        super(SoapException, self).__init__(message)
        self.status_code = status_code


