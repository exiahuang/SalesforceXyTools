import sublime
import sublime_plugin
from datetime import datetime
import xdrlib
import os,sys,re,json
import shutil
import subprocess,threading
import webbrowser
import random
import platform
from time import sleep

from .salesforce import *
from . import baseutil
from .baseutil import SysIo
from .uiutil import SublConsole
from .setting import SfBasicConfig
from .const import AURA_DEFTYPE_EXT

##########################################################################################
#Salesforce Util
##########################################################################################
def sf_login(sf_basic_config, project_name='', Soap_Type=Soap):
    project = settings = sf_basic_config.get_setting()
    sublconsole = SublConsole(sf_basic_config)

    try:
        # project = {}
        # if project_name:
        #     projects = settings["projects"]
        #     project = projects[project_name]
        # else:
        #     project = settings["default_project_value"]

        # sublconsole.debug('settings--->')
        # sublconsole.debug(json.dumps(settings, indent=4))
        # sublconsole.debug(json.dumps(project, indent=4))

        if project_name:
            # TODO
            sublconsole.debug('>>>>sf_login [project_name]: ' +  project_name)
            sf = Soap_Type(username=project["username"], 
                        password=project["password"], 
                        security_token=project["security_token"], 
                        sandbox=project["is_sandbox"],
                        version=project["api_version"],
                        myconsole=sublconsole
                        )

        elif settings["use_oauth2"]:
            sublconsole.debug('>>>>sf_login : use oauth2')
            sf = Soap_Type( session_id=project["access_token"] ,
                            instance_url=project["instance_url"],
                            sandbox=project["is_sandbox"],
                            version=project["api_version"],
                            myconsole=sublconsole
                            )
            # sf = Soap_Type(username=project["username"],
            #                 session_id=project["sessionId"] ,
            #                 instance_url=project["instanceUrl"],
            #                 sandbox=project["is_sandbox"],
            #                 version=project["api_version"],
            #                 client_id=project["id"],
            #                 settings=settings
            #                 # password=None,
            #                 # security_token=None,
            #                 # instance=None,
            #                 # organizationId=None,
            #                 # proxies=None,
            #                 # session=None,
            #                 # project=None
            #                 )

        elif settings["use_password"]:
            sublconsole.debug('>>>>sf_login : use password')
            sf = Soap_Type(username=project["username"], 
                        password=project["password"], 
                        security_token=project["security_token"], 
                        sandbox=project["is_sandbox"],
                        version=project["api_version"],
                        myconsole=sublconsole
                        )

        sf.settings = settings
        # sublconsole.debug(sf.session_id)
        return sf
    except Exception as e:
        if settings["use_oauth2"]:
            sublconsole.showlog('please login salesforce on your browser!')
            sf_oauth2(sf_basic_config)
        else:
            sublconsole.showlog(e)
            sublconsole.show_in_dialog('Login Error! ' + baseutil.xstr(e))
        return


##########################################################################################
#Salesforce Auth
##########################################################################################
from SalesforceXyTools.libs import server
sfdc_oauth_server = None

def re_auth(sf_basic_config):
    settings =  sf_basic_config.get_setting()
    if settings["use_oauth2"]:
        sf_oauth2(settings)

def sf_oauth2(sf_basic_config):
    sublconsole = SublConsole(sf_basic_config)
    settings =  sf_basic_config.get_setting()
    from SalesforceXyTools.libs import auth
    project_setting = settings
    # project_setting = settings["default_project_value"]
    is_sandbox = project_setting["is_sandbox"]

    if refresh_token(sf_basic_config):
        return

    server_info = sublime.load_settings("sfdc.server.sublime-settings")
    client_id = server_info.get("client_id")
    client_secret = server_info.get("client_secret")
    redirect_uri = server_info.get("redirect_uri")
    oauth = auth.SalesforceOAuth2(client_id, client_secret, redirect_uri, is_sandbox)
    authorize_url = oauth.authorize_url()
    sublconsole.debug('authorize_url-->')
    sublconsole.debug(authorize_url)
    start_server()
    open_in_default_browser(sf_basic_config, authorize_url)

def start_server():
    global sfdc_oauth_server
    if sfdc_oauth_server is None:
        sfdc_oauth_server = server.Server()

def stop_server():
    global sfdc_oauth_server
    if sfdc_oauth_server is not None:
        sfdc_oauth_server.stop()
        sfdc_oauth_server = None
        
def refresh_token(sf_basic_config):
    settings =  sf_basic_config.get_setting()
    sublconsole = SublConsole(sf_basic_config)
    sublconsole.debug('>>>>start to refresh token')
    from SalesforceXyTools.libs import auth

    if not settings["use_oauth2"]:
        return False

    project_setting = settings
    is_sandbox = project_setting["is_sandbox"]

    if "refresh_token" not in project_setting:
        sublconsole.debug("refresh token missing")
        return False

    sublconsole.debug('>>>>load server info')
    server_info = sublime.load_settings("sfdc.server.sublime-settings")
    client_id = server_info.get("client_id")
    client_secret = server_info.get("client_secret")
    redirect_uri = server_info.get("redirect_uri")
    oauth = auth.SalesforceOAuth2(client_id, client_secret, redirect_uri, is_sandbox)
    _refresh_token = project_setting["refresh_token"]
    # sublconsole.debug(refresh_token)
    response_json = oauth.refresh_token(_refresh_token)
    # sublconsole.debug(response_json)

    if "error" in response_json:
        sublconsole.debug('>>>>response josn error')
        sublconsole.debug(response_json)
        return False

    if "refresh_token" not in response_json:
        response_json["refresh_token"] = _refresh_token

    sublconsole.debug('>>>>refresh_token:')
    sublconsole.debug(refresh_token)
    sublconsole.debug('>>>>save session')
    sf_basic_config.save_session(response_json)
    sublconsole.debug("------->refresh_token ok!")
    return True

class OauthUtil():
    def __init__(self, sf_basic_config):
        self.sf_basic_config = sf_basic_config
        self.settings =  sf_basic_config.get_setting()
    
    def is_use_oauth(self):
        return self.settings["use_oauth2"]



##########################################################################################
#Metadata Cache
##########################################################################################
class CacheLoader(object):
    def __init__(self, file_name, always_reload=False, sf_basic_config = None):
        if sf_basic_config:
            self.sf_basic_config = sf_basic_config
        else:
            self.sf_basic_config = SfBasicConfig()
            
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.settings = self.sf_basic_config.get_setting()
        self.MAX_DEEP = 2
        self.file_name = file_name
        self.save_dir =  self.sf_basic_config.get_config_dir()
        self.full_path = os.path.join(self.save_dir, self.file_name)
        self.all_cache = None
        self.always_reload = always_reload

    def is_exist(self):
        return os.path.exists(self.full_path)

    def get_cache(self):
        if self.all_cache:
            return self.all_cache
        self.all_cache = self._load()
        return self.all_cache

    def reload(self):
        return

    def clean(self):
        if os.path.exists(self.full_path):
            os.remove(self.full_path)

    def save_dict(self, dict_obj, encoding='utf-8'):
        self.save(json.dumps(dict_obj, ensure_ascii=False, indent=4), encoding=encoding)
    
    def save(self, json_str, encoding='utf-8'):
        full_path = self.full_path
        if not os.path.exists(os.path.dirname(full_path)):
            self.sublconsole.showlog("mkdir: " + os.path.dirname(full_path))
            os.makedirs(os.path.dirname(full_path))
        try:
            fp = open(full_path, "w", encoding=encoding)
            fp.write(json_str)
        except Exception as e:
            self.sublconsole.showlog('save file error! ' + full_path)
            self.sublconsole.showlog(e)
        finally:
            fp.close()

    def _load(self, deep=1, not_null_id=True, encoding='utf-8'):
        if self.always_reload:
            self.reload()
        if self.is_exist():
            data = {}
            with open(self.full_path, "r", encoding=encoding) as fp:
                data = json.loads(fp.read(),encoding)
            return data
        elif deep <= self.MAX_DEEP:
            self.reload()
            deep = deep + 1
            return self._load(deep, not_null_id)
        return

class SobjectUtil(CacheLoader):
    def __init__(self, sf_basic_config = None):
        super(SobjectUtil, self).__init__("sobject.cache", always_reload=True, sf_basic_config=sf_basic_config)
        self.meta_api = sf_login(self.sf_basic_config, Soap_Type=MetadataApi)

    def reload(self):
        self.sublconsole.showlog("start to reload metadata cache, please wait...")
        self.clean()
        allMetadataResult = self.meta_api.describe()
        
        allMetadataMap = {}
        allMetadataMap["sobjects"] = {}
        for meta in allMetadataResult["sobjects"]:
            name = meta["name"]
            allMetadataMap["sobjects"][name] = meta
        allMetadataMap["lastUpdated"] = str(datetime.now())
        self.save_dict(allMetadataMap)
        # self.sublconsole.save_and_open_in_panel(json.dumps(allMetadataMap, ensure_ascii=False, indent=4), self.save_dir, self.file_name , is_open=False)

    # get all fields from sobject
    def get_sobject_fields(self, sobject_name):
        sftype = self.meta_api.get_sobject(sobject_name)
        sftypedesc = sftype.describe()
        return [baseutil.xstr(field["name"]) for field in sftypedesc["fields"]]

    def soql_format(self, soql_str):
        soql = baseutil.del_comment(soql_str)
        match = re.match("select\s+\*\s+from[\s\t]+(\w+)([\t\s\S]*)", soql, re.I|re.M)
        if match:
            sobject_name = match.group(1)
            condition = match.group(2)
            fields = self.get_sobject_fields(sobject_name)
            fields_str = ','.join(fields)
            soql = ("select %s from %s %s" % (fields_str, sobject_name, condition))
        return soql
    
    def get_sobject_info(self, sobject_name):
        all_cache = self.get_cache()
        sobject_info = None
        if sobject_name in all_cache["sobjects"]:
            sobject_info = all_cache["sobjects"][sobject_name]
            sobject_info["sftypedesc"] = self.meta_api.get_sobject(sobject_name).describe()
            sobject_info["fields"] = [baseutil.xstr(field["name"]) for field in sobject_info["sftypedesc"]["fields"]]
            sobject_info["fields_obj"] = sobject_info["sftypedesc"]["fields"]
            sobject_info["soql"] = self.get_soql(sobject_name, sobject_info["fields"])
        return sobject_info

    def get_soql(self, sobject_name, fields):
        return "SELECT %s FROM %s" % (" , ".join(fields), sobject_name)
    
    def get_sobject_info_list(self, sobject_name_list):
        return [ self.get_sobject_info(sobject_name) for sobject_name in sobject_name_list]
    
    # def _get_sobject_custom_fields(self, sftypedesc):
    #     return [field for field in sftypedesc["fields"]]

    def get_sobject_name_list_for_sel(self):
        all_cache = self.get_cache()
        sobject_name_list = []
        sobject_show_list = []
        for sobject_info in all_cache["sobjects"].values():
            sobject_show_list.append( "%s , %s , %s" % (str(sobject_info["name"]), str(sobject_info["label"]), str(sobject_info["keyPrefix"])))
            sobject_name_list.append(str(sobject_info["name"]))
        return sobject_show_list, sobject_name_list

    def open_in_web(self, sobject_name, view_type="data_list"):
        sobject_info = self.get_sobject_info(sobject_name)
        returl = sobject_info["keyPrefix"]
        if returl:
            # open in browser
            sf = sf_login(self.sf_basic_config)
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                        .format(instance=sf.sf_instance,
                                sid=sf.session_id,
                                returl=returl))
            self.sublconsole.debug(login_url)
            open_in_default_browser(self.sf_basic_config, login_url)
        else:
            self.sublconsole.showlog("metadata is null!")


class MetadataUtil(CacheLoader):
    def __init__(self, sf_basic_config = None):
        super(MetadataUtil, self).__init__("metadata.cache", always_reload=False, sf_basic_config=sf_basic_config)

        self.desc_meta_file = "describe_metadata.cache"
        self.all_cache = None

    def reload(self):
        self.sublconsole.showlog("start to reload metadata cache, please wait...")
        self.clean()
        meta_api = sf_login(self.sf_basic_config, Soap_Type=MetadataApi)
        
        allMetadataResult = meta_api.getAllMetadataMap()
        allMetadataResult["AuraDefinition"] = self._load_lux_cache()
        self.save_dict(allMetadataResult)
    
    def _covert_AuraDefinition_to_cache_dict(self, AuraDefinition_records):
        AuraDefinition_MetadataMap = {}
        try:
            for AuraDefinition in AuraDefinition_records:
                deftype = AuraDefinition["DefType"]
                if deftype in AURA_DEFTYPE_EXT:
                    aura_name = AuraDefinition["AuraDefinitionBundle"]["DeveloperName"]
                    aura_key = "aura/%s/%s%s" % (aura_name, aura_name, AURA_DEFTYPE_EXT[deftype])
                    AuraDefinition_MetadataMap[aura_key] = {
                            "id": AuraDefinition["Id"], 
                            "fileName": aura_key, 
                            "fullName": aura_name + AURA_DEFTYPE_EXT[deftype], 
                            "createdById": AuraDefinition["CreatedById"], 
                            "createdByName": AuraDefinition["CreatedBy"]["Name"] if AuraDefinition["CreatedBy"] else '', 
                            "createdDate": AuraDefinition["CreatedDate"], 
                            "lastModifiedById": AuraDefinition["LastModifiedById"],  
                            "lastModifiedByName": AuraDefinition["LastModifiedBy"]["Name"] if AuraDefinition["LastModifiedBy"] else '', 
                            "lastModifiedDate": AuraDefinition["LastModifiedDate"], 
                            "manageableState": "", 
                            "type": "AuraDefinition", 
                            "AuraDefinitionSrc": True, 
                            "DefType": AuraDefinition["DefType"], 
                            "DefExt": AURA_DEFTYPE_EXT[deftype], 
                            "Format": AuraDefinition["Format"], 
                            "AuraDefinitionBundleId": AuraDefinition["AuraDefinitionBundleId"], 
                            "AuraDefinitionBundleName": aura_name
                        }
            return AuraDefinition_MetadataMap
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')
            return AuraDefinition_MetadataMap

    def _load_lux_cache(self, attr=None):
        try:
            aura_soql = 'SELECT Id, CreatedDate, CreatedById, CreatedBy.Name, LastModifiedDate, LastModifiedById, LastModifiedBy.Name, AuraDefinitionBundle.DeveloperName, AuraDefinitionBundleId, DefType, Format FROM AuraDefinition'
            if attr:
                aura_soql = aura_soql + " Where AuraDefinitionBundle.DeveloperName = '%s' and DefType = '%s' limit 1" % (attr["lux_name"], attr["lux_type"])

            meta_api = sf_login(self.sf_basic_config, Soap_Type=MetadataApi)
            AuraDefinition = meta_api.query(aura_soql)
            AuraDefinition_MetadataMap = {}
            if AuraDefinition and 'records' in AuraDefinition:
                AuraDefinition_MetadataMap = self._covert_AuraDefinition_to_cache_dict(AuraDefinition['records'])
            if attr: 
                if len(AuraDefinition_MetadataMap) > 0 : return list(AuraDefinition_MetadataMap.values())[0]
                else : return {}
            return AuraDefinition_MetadataMap
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')
            return {}

    def get_meta_attr(self, full_path):
        sysio = SysIo()
        attr = sysio.get_file_attr(full_path)
        if attr and "file_key" in attr:
            meta = self.get_meta(attr["metadata_type"], attr["file_key"])
            if not meta:
                print('load from server')
                self.update_metadata_cache_by_filename(full_path)
                meta = self.get_meta(attr["metadata_type"], attr["file_key"])
            if meta: attr.update(meta)
        return attr

    def get_describe_metadata_cache(self, deep=1):
        self.sublconsole.debug("build describeMetadata Cache")
        desc_meta_path = os.path.join(self.sf_basic_config.get_config_dir(), self.desc_meta_file)
        if os.path.exists(desc_meta_path):
            data = {}
            with open(desc_meta_path, "r", encoding='utf-8') as fp:
                data = json.loads(fp.read(),'utf-8')
            return data
        elif deep <= self.MAX_DEEP:
            meta_api = sf_login(self.sf_basic_config, Soap_Type=MetadataApi)
            describeMetadataResult = meta_api.describeMetadata()
            self.sublconsole.save_and_open_in_panel(json.dumps(describeMetadataResult, ensure_ascii=False, indent=4), self.save_dir, self.desc_meta_file, is_open=False)
            deep = deep + 1
            return self.get_describe_metadata_cache(deep)
        return

    def update_metadata_cache(self, full_path, id):
        server_meta = self._get_server_meta(full_path, id)
        if server_meta:
            self._save_meta(server_meta)

    def delete_metadata_cache(self, full_path):
        attr = self.get_meta_attr(full_path)
        if attr and "file_key" in attr:
            meta = self.get_meta(attr["metadata_type"], attr["file_key"])
            self._del_meta(meta)

    def get_meta_category(self):
        all_cache = self.get_cache()
        return list(all_cache.keys())
        
    def get_meta_namelist(self, category):
        all_cache = self.get_cache()
        category_meta = all_cache[category]
        return list(category_meta.keys())

    def get_meta_by_category(self, category):
        all_cache = self.get_cache()
        return all_cache[category] if category in all_cache else None
    
    def get_meta(self, category, fileName):
        category_meta = self.get_meta_by_category(category)
        if category_meta and fileName in category_meta:
            meta = category_meta[fileName]
            meta["webUrl"] = self.get_web_url(meta)
            return meta
        return
    
    def is_modified(self, full_path, id):
        attr = self.get_meta_attr(full_path)
        server_meta = self._get_server_meta(full_path, id)
        if not server_meta:
            return "Not Found metadata, id=%s" % id
        if not attr:
            self._save_meta(server_meta)
            return "Maybe the server metadata is lasted!"
        self.sublconsole.debug('>>>check is modified')
        self.sublconsole.debug(attr)
        self.sublconsole.debug(server_meta)
        self.sublconsole.debug('File=%s, Id=%s, local : %s , server : %s' % (attr["file_key"], attr["id"], attr["lastModifiedDate"], server_meta["lastModifiedDate"]))
        if attr["lastModifiedDate"].replace('+0000', 'Z') != server_meta["lastModifiedDate"].replace('+0000', 'Z'):
            return "%s is modified by %s, %s, are you sure to update it?" % (server_meta["fileName"], server_meta["lastModifiedByName"], server_meta["lastModifiedDate"])
        return ""

    def get_web_url(self, sel_meta):
        self.sublconsole.debug(sel_meta)
        returl = ""
        if "type" in sel_meta:
            sel_category = sel_meta["type"]
            if sel_category == "Workflow":
                returl = '/01Q?setupid=WorkflowRules'
            elif sel_category == "CustomLabels":
                returl = '/101'
            elif sel_category == "AuraDefinition" and all (k in sel_meta for k in ("id", "DefType", "Format", "AuraDefinitionBundleId")):
                returl = '/_ui/common/apex/debug/ApexCSIPage?action=openFile&extent=AuraDefinition&Id=%s&AuraDefinitionBundleId=%s&DefType=%s&Format=%s' % (sel_meta["id"], sel_meta["AuraDefinitionBundleId"], sel_meta["DefType"],sel_meta["Format"])
            elif sel_meta and "id" in sel_meta and sel_meta["id"]:
                returl = '/' + sel_meta["id"]
            elif sel_category == "CustomObject":
                returl = '/p/setup/layout/LayoutFieldList?type=' + sel_meta["fullName"]

        return returl

    def open_in_web(self, sel_meta):
        returl = self.get_web_url(sel_meta)
        if returl:
            import urllib.parse
            # open in browser
            sf = sf_login(self.sf_basic_config)
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                        .format(instance=sf.sf_instance,
                                sid=sf.session_id,
                                returl=urllib.parse.quote(returl)))
            self.sublconsole.debug(login_url)
            open_in_default_browser(self.sf_basic_config, login_url)
        else:
            self.sublconsole.showlog("metadata is null!")

    def run_test(self, id_list):
        tooling_api = sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        status_code, result = tooling_api.runTestSynchronous(id_list)
        if "codeCoverageWarnings" in result: del result["codeCoverageWarnings"]
        if "codeCoverage" in result: del result["codeCoverage"]
        if "apexLogId" in result:
            log_status_code, log = tooling_api.getLog(result["apexLogId"])
        
        coverage_info = "\n".join(self.get_apex_coverage())

        file_name = datetime.now().strftime('Test_%Y%m%d_%H%M%S.log')
        split_str = "\n" + ("~" * 120) + "\n"
        test_result = split_str.join([ json.dumps(result, ensure_ascii=False, indent=4), coverage_info, log])
        self.sublconsole.save_and_open_in_panel(test_result, self.sf_basic_config.get_test_dir(), file_name , is_open=True)
    
    def get_apex_coverage(self):
        tooling_api = sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        ApexCodeCoverageAggregate = "SELECT ApexClassOrTrigger.Name, NumLinesCovered, NumLinesUncovered FROM ApexCodeCoverageAggregate ORDER BY ApexClassOrTrigger.Name"
        coverage_status_code, coverage_result = tooling_api.toolingQuery(ApexCodeCoverageAggregate)
        if not "records" in coverage_result: return []
        total_NumLinesCovered = 0
        total_NumLinesUncovered = 0
        LINE_SPLIT = "~" * 106
        coverage_info = [LINE_SPLIT, "Name".ljust(50) + "NumLinesCovered".ljust(22) + "NumLinesUncovered".ljust(22) + "Coverage%".ljust(22), LINE_SPLIT]
        for record in coverage_result["records"]:
            total_NumLinesCovered = total_NumLinesCovered + record["NumLinesCovered"]
            total_NumLinesUncovered = total_NumLinesUncovered + record["NumLinesUncovered"]
            lines = int(record["NumLinesCovered"]) + int(record["NumLinesUncovered"])
            coverage_percent = record["NumLinesCovered"]/lines if lines != 0 else 0
            coverage_percent_str = "%.2f%%" % (coverage_percent * 100)
            tmp = record["ApexClassOrTrigger"]["Name"].ljust(50) + str(record["NumLinesCovered"]).ljust(22) + str(record["NumLinesUncovered"]).ljust(22) + coverage_percent_str.ljust(22)
            coverage_info.append(tmp)
        coverage_info.append(LINE_SPLIT)

        total_lines = total_NumLinesCovered + total_NumLinesUncovered
        total_coverage_percent_str = "%.2f%%" % ((total_NumLinesCovered/total_lines if total_lines != 0 else 0) * 100)
        coverage_info.append("Overall".ljust(50) + str(total_NumLinesCovered).ljust(22) + str(total_NumLinesUncovered).ljust(22) + total_coverage_percent_str.ljust(22))
        return coverage_info

    def _del_meta(self, meta):
        all_cache = self.get_cache()
        del all_cache[meta["type"]][meta["fileName"]]
        self.sublconsole.debug("_del_meta")
        self.sublconsole.debug(meta)
        self.sublconsole.save_and_open_in_panel(json.dumps(all_cache, ensure_ascii=False, indent=4), self.save_dir, self.file_name , is_open=False)

    def _save_meta(self, server_meta):
        self.sublconsole.debug("_save_meta")
        all_cache = self.get_cache()
        print(server_meta)
        if server_meta and "type" in server_meta:
            if server_meta["type"] not in all_cache:
                all_cache[server_meta["type"]] = {}
            all_cache[server_meta["type"]][server_meta["fileName"]] = server_meta
            self.sublconsole.debug(server_meta)
            self.sublconsole.save_and_open_in_panel(json.dumps(all_cache, ensure_ascii=False, indent=4), self.save_dir, self.file_name , is_open=False)

    def _get_server_meta(self, full_path, id):
        attr = self.get_meta_attr(full_path)
        attr["id"] = id
        if attr["is_lux"]:
            return self._load_lux_cache(attr)
        else:
            soql = "SELECT Id, Name, CreatedDate, CreatedById, CreatedBy.Name, LastModifiedDate, LastModifiedById, LastModifiedBy.Name FROM %s Where Id = '%s'" % (attr["metadata_type"], id)
            tooling_api = sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
            result = tooling_api.query(soql)
            if 'records' in result and len(result['records']) > 0:
                record = result['records'][0]
                meta_cache_bean = {
                    "createdById": record["CreatedById"], 
                    "createdByName": record["CreatedBy"]["Name"] if record["CreatedBy"] else '', 
                    "createdDate": record["CreatedDate"], 
                    "fileName": attr["metadata_folder"] + "/" + attr["file_name"], 
                    "fullName": attr["name"], 
                    "id": record["Id"], 
                    "lastModifiedById": record["LastModifiedById"], 
                    "lastModifiedByName": record["LastModifiedBy"]["Name"] if record["LastModifiedBy"] else '', 
                    "lastModifiedDate": record["LastModifiedDate"], 
                    "manageableState": "", 
                    "type": attr["metadata_type"]
                }
                return meta_cache_bean
        return
    
    def update_metadata_cache_by_filename(self, full_path):
        # attr = self.get_meta_attr(full_path)
        sysio = SysIo()
        attr = sysio.get_file_attr(full_path)
        if attr["is_lux"] :
            self._save_meta(self._load_lux_cache(attr))
        else:
            if "metadata_type" not in attr or "name" not in attr: return
            if attr["metadata_type"] == "AuraDefinitionBundle":
                soql = "SELECT  Id, CreatedDate, CreatedById, CreatedBy.Name, LastModifiedDate, LastModifiedById, LastModifiedBy.Name FROM %s Where DeveloperName = '%s' limit 1" % (attr["metadata_type"], attr["name"])
            else:
                soql = "SELECT  Id, Name, CreatedDate, CreatedById, CreatedBy.Name, LastModifiedDate, LastModifiedById, LastModifiedBy.Name FROM %s Where Name = '%s' limit 1" % (attr["metadata_type"], attr["name"])
            tooling_api = sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
            result = tooling_api.query(soql)
            if 'records' in result and len(result['records']) > 0:
                record = result['records'][0]
                meta_cache_bean = {
                    "createdById": record["CreatedById"], 
                    "createdByName": record["CreatedBy"]["Name"] if record["CreatedBy"] else '', 
                    "createdDate": record["CreatedDate"], 
                    "fileName": attr["metadata_folder"] + "/" + attr["file_name"], 
                    "fullName": attr["name"], 
                    "id": record["Id"], 
                    "lastModifiedById": record["LastModifiedById"], 
                    "lastModifiedByName": record["LastModifiedBy"]["Name"] if record["LastModifiedBy"] else '',
                    "lastModifiedDate": record["LastModifiedDate"], 
                    "manageableState": "", 
                    "type": attr["metadata_type"]
                }
                self._save_meta(meta_cache_bean)
        return

    def update_lux_metas(self, AuraDefinition_records):
        all_cache = self.get_cache()
        if "AuraDefinition" not in all_cache:
            all_cache["AuraDefinition"] = {}
        all_cache["AuraDefinition"].update( self._covert_AuraDefinition_to_cache_dict(AuraDefinition_records) )
        self.sublconsole.save_and_open_in_panel(json.dumps(all_cache, ensure_ascii=False, indent=4), self.save_dir, self.file_name , is_open=False)


class SfDataUtil():
    def __init__(self, sf_basic_config = None):
        if sf_basic_config:
            self.sf_basic_config = sf_basic_config
        else:
            self.sf_basic_config = SfBasicConfig()
        self.tooling_api = sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
    
    def get_profiles(self):
        soql = "SELECT Name From Profile"
        status_code, result = self.tooling_api.toolingQuery(soql)
        if not "records" in result: return []
        return [ record["Name"] for record in result["records"] ]

class DownloadUtil(object):
    def __init__(self, sf_basic_config = None, is_auto_download=False):
        if sf_basic_config:
            self.sf_basic_config = sf_basic_config
        else:
            self.sf_basic_config = SfBasicConfig()
            
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.settings = self.sf_basic_config.get_setting()
        # v2.0.4 donot auto download
        if is_auto_download:
            self.download_jar()
    
    def download_jar(self):
        jar_home = self.sf_basic_config.get_default_jar_home()
        jar_full_path = self.get_jar_path()
        if not os.path.exists(jar_home):
            self.sublconsole.showlog("mkdir : " + jar_home)
            os.makedirs(jar_home)
        if not os.path.exists( jar_full_path ):
            self.sublconsole.showlog("download jar : " + jar_full_path)
            self._start_to_download_jar()
    
    def _start_to_download_jar(self):
        jar_full_path = self.get_jar_path()
        jar_name = self.get_jar_name()
        url = "http://salesforcexytools.com/mystatic/jar/" + jar_name
        import urllib.request
        try:
            with urllib.request.urlopen(url) as response, open(jar_full_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except Exception as e:
            help_msg = "please copy %s to %s" % (jar_name, self.sf_basic_config.get_default_jar_home())
            self.sublconsole.showlog( "download %s error, %s, \n%s" % (url, str(e), help_msg))
            pass

    def get_jar_url_path(self):
        url = "http://salesforcexytools.com/mystatic/jar/" + self.get_jar_name()
        return url

    def get_jar_path(self):
        jar_home = self.sf_basic_config.get_default_jar_home()
        jar_name = self.get_jar_name()
        return os.path.join(jar_home, jar_name)
    
    def get_jar_name(self):
        jar_name = ""
        return jar_name

class DataloaderUtil(DownloadUtil):
    def __init__(self, sf_basic_config = None):
        super(DataloaderUtil, self).__init__(sf_basic_config=sf_basic_config, is_auto_download=True)

    def getEncryptionPassword(self):
        password = ""
        try:
            dl_jar_path = self.get_jar_path()
            cmd = "java -cp %s com.salesforce.dataloader.security.EncryptionUtil -e %s" % (dl_jar_path, self.settings["password"])
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data, stderr_data = p.communicate()
            ret_data = stdout_data.split(self._get_split_code())[0].decode('utf-8')
            password = ret_data[-32:]
        except Exception as e:
            self.sublconsole.showlog("getEncryptionPassword exception: " + str(e))
        return password
    
    def _get_split_code(self):
        if sublime.platform() == "windows":
            return b"\r\n"
        else:
            return b"\n"
    
    def get_jar_name(self):
        jar_name = "dataloader-40.0.0-uber.jar"
        return jar_name

class MigrationToolUtil(DownloadUtil):
    def __init__(self, sf_basic_config = None, is_auto_download = False):
        super(MigrationToolUtil, self).__init__(sf_basic_config=sf_basic_config, is_auto_download=is_auto_download)
        self.sysio = SysIo()
    
    def get_jar_name(self):
        jar_name = "ant-salesforce.jar"
        return jar_name
    
    def _del_old_dir(self, deploy_root_dir):
        if os.path.exists(deploy_root_dir):
            shutil.rmtree(deploy_root_dir, ignore_errors=True)
            sleep(1)
    
    def _copy_folder_xml(self, org_file_path, save_full_path):
        file_path, file_name = os.path.split(org_file_path)
        xml_file_path = file_path + "-meta.xml"
        if os.path.isfile(xml_file_path):
            # shutil.copyfile(xml_file_path, save_full_path)
            self.copyfile(xml_file_path, save_full_path)
            self.copy_file_list.append((xml_file_path, save_full_path))
    
    def _copy_file_xml(self, org_file_path, deploy_dir):
        meta_xml = org_file_path + "-meta.xml"
        if os.path.isfile(meta_xml):
            # shutil.copyfile(meta_xml, deploy_dir)
            self.copyfile(meta_xml, deploy_dir)
            self.copy_file_list.append((meta_xml, deploy_dir))

### delete start: ant xml and copyfile.txt
#     def _build_ant_xml_copy_task(self, deploy_root_dir):
#         template = """<project name="SalesforceXyTools Migration tools" default="copyfile" basedir=".">
#     <target name="copyfile">
#         <delete dir="src" />
# {copy_task}
#     </target>
# </project>"""
#         template_copy_task = """        <copy preservelastmodified="true"
#               file="{from_file}"
#               tofile="{to_file}" />"""
#         copy_task = []
#         for from_file, to_file in self.copy_file_list:
#             copy_task.append(template_copy_task.format(from_file=from_file, to_file=to_file))
#         copy_task_str = template.replace("{copy_task}", "\n".join(copy_task))
        
#         save_path = os.path.join(deploy_root_dir, "build.copyfile.xml")
#         self.sysio.save_file(save_path, copy_task_str)
#     def _build_copy_files_md(self, deploy_root_dir):
#         copy_task = []
#         for from_file, to_file in self.copy_file_list:
#             copy_task.append(from_file)
#         save_path = os.path.join(deploy_root_dir, "copyfile.txt")
#         self.sysio.save_file(save_path, "\n".join(copy_task))
### delete end

    def _build_module_json(self, key, files):
        module_json = CacheLoader(file_name="module.json", always_reload=False, sf_basic_config = self.sf_basic_config)
        if module_json.is_exist():
            module_json_cache = module_json.get_cache()
        else:
            module_json_cache = {}
        module_json_cache[key] = {
                    "desc" : "",
                    "created" : str(datetime.now()),
                    "files" : files
            }
        module_json.save_dict(module_json_cache)
    
    def copyfile(self, file, to_file, encoding='utf-8'):
        with open(file, 'rU', encoding=encoding) as infile,                 \
             open(to_file, 'w', newline='\n', encoding=encoding) as outfile:
                 outfile.writelines(infile.readlines())

    def copy_deploy_files(self, file_list, deploy_root_dir, api_version="40.0"):
        self._del_old_dir(deploy_root_dir)
        
        copy_org_file_list = []
        self.copy_file_list = []
        for file in file_list:
            attr = self.sysio.get_file_attr(file)
            if not attr or not attr["is_sfdc_file"] or not attr["metadata_folder"]: continue
            metadata_folder = os.path.join(deploy_root_dir, "src", attr["metadata_folder"], attr["metadata_sub_folder"])

            # deploy lightning component folder

            if attr["is_lux"] or ("is_lwc" in attr and attr["is_lwc"]):
                if not os.path.exists(metadata_folder):
                    shutil.copytree(attr['file_path'] , metadata_folder)
                continue

            if not os.path.exists(metadata_folder):
                os.makedirs(metadata_folder, exist_ok=True)
            to_file = os.path.join(metadata_folder, attr["file_name"])
            # shutil.copyfile(file, to_file)
            self.copyfile(file, to_file)
            self.copy_file_list.append((file, to_file))
            # copy_org_file_list.append(os.path.join(".", "src", attr["metadata_folder"], attr["metadata_sub_folder"], attr["file_name"]))
            copy_org_file_list.append(file)

            self._copy_folder_xml(file, metadata_folder + "-meta.xml")
            self._copy_file_xml(file, os.path.join(metadata_folder, attr["file_name"] + "-meta.xml"))
        
        self._build_module_json(os.path.basename(deploy_root_dir), copy_org_file_list)
        # self._build_ant_xml_copy_task(deploy_root_dir)
        # self._build_copy_files_md(deploy_root_dir)
        self.build_package_xml(os.path.join(deploy_root_dir, "src", "package.xml"), file_list, api_version)

    def build_package_xml(self, save_path, file_list, api_version="40.0"):
        print('build package.xml to deploy')
        file_attr_map = {}
        for file in file_list:
            attr = self.sysio.get_file_attr(file)
            if not attr or not attr["is_sfdc_file"]: continue
            if attr["metadata_type"] in file_attr_map:
                file_attr_map[attr["metadata_type"]].append(attr)
            else:
                file_attr_map[attr["metadata_type"]] = [attr]
        packagexml = self._get_package_xml(file_attr_map, api_version)
        self.sysio.save_file(save_path, packagexml)
        return packagexml

    def _get_package_xml(self, file_attr_map, api_version="40.0"):
        packagexml_types = ""
        for metadata_type, file_attr_list in file_attr_map.items():
            members = []
            members_check = []
            for attr in file_attr_list:
                if ("is_lux" in attr and attr["is_lux"]) or ("is_lwc" in attr and attr["is_lwc"]):
                    member = attr["metadata_sub_folder"]
                else:
                    member = attr["name"] if not attr["metadata_sub_folder"] else "%s/%s" % (attr["metadata_sub_folder"],attr["name"])
                if member in members_check: continue
                members_check.append(member)
                members.append("""        <members>{member}</members>""".format(member=member))
            metadata_type = "AuraDefinitionBundle" if attr["is_lux"] else metadata_type
            packagexml_types = packagexml_types + PACKAGEXML_TYPE.format(members='\n'.join(members),name=metadata_type)
        packagexml = PACKAGE_XML.format(types=packagexml_types, version=api_version)
        return packagexml


PACKAGEXML_TYPE = """
    <types>
{members}
        <name>{name}</name>
    </types>"""

PACKAGE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
{types}
    <version>{version}</version>
</Package>
"""

class OsUtil():
    def __init__(self, sf_basic_config = None):
        if sf_basic_config:
            self.sf_basic_config = sf_basic_config
        else:
            self.sf_basic_config = SfBasicConfig()
            
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.settings = self.sf_basic_config.get_setting()

    def run_in_sublime_cmd(self, cmd_list):
        self.sublconsole.thread_run(target=self._run_cmd, args=(cmd_list,))
    
    def _run_cmd(self, cmd_list):
        self.sublconsole.showlog("*" * 80)
        cmd_str = self._get_cmd_str(cmd_list)
        process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        encoding = sys.getfilesystemencoding()
        # encoding = 'shift-jis'
        while True:
            line = process.stdout.readline()
            if line != '' and line != b'' :
                #the real code does filtering here
                try:
                    msg = line.rstrip().decode(encoding)
                except Exception as ex:
                    msg = line.rstrip()
                self.sublconsole.showlog(msg, show_time=False)
            else:
                break
        self.sublconsole.showlog("*" * 80)

    def os_run(self, cmd_list):
        if self.sf_basic_config.is_use_os_terminal():
            self.run_in_os_termial(cmd_list)
        else:
            self.run_in_sublime_cmd(cmd_list)

    def run_in_os_termial(self, cmd_list):
        if sublime.platform() == "windows":
            cmd_list.append("pause")
        cmd_str = self._get_cmd_str(cmd_list)
        thread = threading.Thread(target=os.system, args=(cmd_str,))
        thread.start()
    
    def _get_cmd_str(self, cmd_list):
        cmd_str = " & ".join(cmd_list)
        return cmd_str

    def get_cd_cmd(self, path):
        if sublime.platform() == "windows":
            return "cd /d " + path
        else:
            return "cd " + path


class DiffUtil():
    def __init__(self, sf_basic_config = None):
        if sf_basic_config:
            self.sf_basic_config = sf_basic_config
        else:
            self.sf_basic_config = SfBasicConfig()
            
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.settings = self.sf_basic_config.get_setting()
    
    def diff(self, local_file, server_file):
        self.sf_basic_config = SfBasicConfig()
        winmerge = self.sf_basic_config.get_winmerge()
        if winmerge and os.path.exists(winmerge):
            cmd = "%s %s %s" % (winmerge, local_file, server_file)
            subprocess.Popen(cmd)
        else:
            self._default_diff_util(local_file, server_file)
    
    def _default_diff_util(self, local_file, server_file):
        import difflib

        local_txt = self._read_file(local_file)
        server_txt = self._read_file(server_file)
        local_sign = "localfile"
        server_sign = "serverfile"
        diff = difflib.unified_diff(local_txt, server_txt, local_sign, server_sign, local_file, server_file, lineterm='')
        difftxt = u"\n".join(line for line in diff)
        if difftxt == "":
            self.sublconsole.showlog("There is no difference !")
        else:
            self.sublconsole.show_in_new_tab(difftxt, "local <-> server")
    
    def _read_file(self, file):
        f = open(file, "r", encoding='utf-8')
        file_txt = f.readlines()
        f.close()
        return file_txt

##########################################################################################
#browser Util
##########################################################################################
def open_in_browser(sf_basic_config, url, browser_name = '', browser_path = ''):
    settings =  sf_basic_config.get_setting()
    if not browser_path or not os.path.exists(browser_path) or browser_name == "default":
        webbrowser.open_new_tab(url)

    elif browser_name == "chrome-private":
        # os.system("\"%s\" --incognito %s" % (browser_path, url))
        browser = webbrowser.get('"' + browser_path +'" --incognito %s')
        browser.open(url)
        
    else:
        try:
            # show_in_panel("33")
            # browser_path = "\"C:\Program Files\Google\Chrome\Application\chrome.exe\" --incognito"
            webbrowser.register('chromex', None, webbrowser.BackgroundBrowser(browser_path))
            webbrowser.get('chromex').open_new_tab(url)
        except Exception as e:
            webbrowser.open_new_tab(url)

def open_in_default_browser(sf_basic_config, url):
    browser_map = sf_basic_config.get_default_browser()
    browser_name = browser_map['name']
    browser_path = browser_map['path']

    if not browser_path or not os.path.exists(browser_path) or browser_name == "default":
        webbrowser.open_new_tab(url)

    elif browser_map['name'] == "chrome-private":
        # chromex = "\"%s\" --incognito %s" % (browser_path, url)
        # os.system(chromex)
        browser = webbrowser.get('"' + browser_path +'" --incognito %s')
        browser.open(url)

        # os.system("\"%s\" -ArgumentList @('-incognito', %s)" % (browser_path, url))

    else:
        try:
            webbrowser.register('chromex', None, webbrowser.BackgroundBrowser(browser_path))
            webbrowser.get('chromex').open_new_tab(url)
        except Exception as e:
            webbrowser.open_new_tab(url)


##########################################################################################
#END
##########################################################################################
