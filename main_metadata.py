import sublime
import sublime_plugin
import os,json,re
from datetime import datetime
from time import sleep
import shutil

from . import baseutil
from . import util
from .setting import SfBasicConfig
from . import xlsxwriter
from .requests.exceptions import RequestException
from .salesforce import (
    SalesforceMoreThanOneRecord,
    SalesforceMalformedRequest,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceError,
    ToolingApi,
    MetadataApi
    )
from .templates import Template
from .uiutil import SublConsole
from .const import AURA_DEFTYPE_EXT, SF_FLODER_TO_TYPE


##########################################################################################
#MetaData
# Apexclass Trigger VisualForce Component
##########################################################################################
class NewApexclassCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("new_metadata", {
            "type": "ApexClass"
        })

class NewApextriggerCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("open_sobject_in_browser", {
            "view_type": "create_trigger"
        })

class NewApexcomponentCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("new_metadata", {
            "type": "ApexComponent"
        })

class NewApexpageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("new_metadata", {
            "type": "ApexPage"
        })

class NewMetadataCommand(sublime_plugin.WindowCommand):
    def run(self, type=None, object_name=None):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.type = type
            self.attr = self.get_attr(self.type)
            self.save_dir = self.sf_basic_config.get_src_dir(sub_folder=self.attr["folder"])
            self.template = Template()
            self.template_config_dict = self.template.load_config_dict(self.type)
            self.template_config_list = list(self.template_config_dict.keys())
            self.object_name = object_name
            self.window.show_quick_panel(self.template_config_list, self.panel_done,sublime.MONOSPACE_FONT)
        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def get_attr(self,type):
        attr = {}
        if type == "ApexClass":
            attr = {"ext" : ".cls", "folder" : "classes"}
        elif type == "ApexTrigger":
            attr = {"ext" : ".trigger", "folder" : "triggers"}
        elif type == "ApexComponent":
            attr = {"ext" : ".component", "folder" : "components"}
        elif type == "ApexPage":
            attr = {"ext" : ".page", "folder" : "pages"}
        return attr
    
    def get_default_file_name(self, sel_template_name):
        file_name = ""
        if self.type == "ApexTrigger":
            file_name = self.object_name.replace("__c", "") + "Trigger"
        elif self.type == "ApexComponent":
            file_name = "NameOfApexComponent"
        elif self.type == "ApexClass":
            tmp_name = sel_template_name.replace(" ", "")
            file_name = "NameOfApex_" + tmp_name
        elif self.type == "ApexPage":
            file_name = "NameOfVfPage"
        return file_name + self.attr["ext"]

    def panel_done(self, picked):
        if 0 > picked < len(self.template_config_list):
            return
        self.sel = self.template_config_list[picked]
        save_file_name = self.get_default_file_name(self.sel)
        show_save_path = os.path.join(self.save_dir, save_file_name )
        self.window.show_input_panel("Please Input your %s Name: " % self.type , 
            show_save_path, self.on_input, None, None)
        self.sublconsole.thread_run(target=self.on_input)

    def on_input(self, args):
        if os.path.exists(args):
            self.sublconsole.showlog("Error ! %s is exist !" % args)
            return
        self.sublconsole.thread_run(target=self.main_handle, args=(args, ))

    def main_handle(self, args = ''):
        file_path, file_name = os.path.split(args)
        api_name, file_extension = os.path.splitext(file_name)
        
        template_config = self.template_config_dict[self.sel]
        data = {
            "api_name" : api_name,
            "object_name" : self.object_name
        }
        self.template_src = self.template.get_src(self.type, template_config["file_name"], data)
        # self.sublconsole.show_in_new_tab(self.template_src)
        save_file_name = api_name + self.attr["ext"]
        self.sublconsole.save_and_open_in_panel(self.template_src, file_path, save_file_name , is_open=True)

        self.sublconsole.showlog('create %s : %s ' % (self.type, api_name)) 
        # self.sublconsole.debug('>>>start to create apex')
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        try:
            if self.type == "ApexClass":
                status_code, result = tooling_api.createApexClass(api_name, self.template_src)
            elif self.type == "ApexTrigger":
                status_code, result = tooling_api.createTrigger(self.object_name, api_name, self.template_src)
            elif self.type == "ApexComponent":
                status_code, result = tooling_api.createMetadata("ApexComponent", {
                    'MasterLabel' : api_name,
                    'name' : api_name,
                    'markup' : self.template_src
                })
            elif self.type == "ApexPage":
                status_code, result = tooling_api.createMetadata("ApexPage", {
                    'MasterLabel' : api_name,
                    'name' : api_name,
                    'markup' : self.template_src
                })

            self.sublconsole.showlog(result)
            if result["success"]:
                self.sublconsole.showlog('>>>create success')
                self._update_meta_cache(save_file_name, result["id"])
                # meta_cache = util.MetadataUtil(self.sf_basic_config)
                # api_name = os.path.join(self.save_dir, save_file_name)
                # meta_cache.update_metadata_cache(api_name, result["id"])
                
                self._build_meta_xml(args, api_name)
            else:
                self.sublconsole.showlog('>>>error code ' + status_code)
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')
    
    def _build_meta_xml(self, full_path, api_name):
        if self.type in ["ApexClass", "ApexTrigger"]:
            meta_xml = "\n".join([
                            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                            "<{0} xmlns=\"http://soap.sforce.com/2006/04/metadata\">",
                            "    <apiVersion>{1}</apiVersion>",
                            "    <status>Active</status>",
                            "</{0}>"
                    ]).format(self.type, self.settings["api_version"])
        elif self.type in ["ApexPage", "ApexComponent"]:
            meta_xml = "\n".join([
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                        "<{0} xmlns=\"http://soap.sforce.com/2006/04/metadata\">",
                        "    <apiVersion>{1}</apiVersion>",
                        "    <label>{2}</label>",
                        "</{0}>"
                ]).format(self.type, self.settings["api_version"], api_name)
        baseutil.SysIo().save_file(full_path=full_path+"-meta.xml", content=meta_xml)
        
    def _update_meta_cache(self, save_file_name, result_id):
        meta_cache = util.MetadataUtil(self.sf_basic_config)
        api_name = os.path.join(self.save_dir, save_file_name)
        meta_cache.update_metadata_cache(api_name, result_id)


class ReloadMetadataCacheCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.thread_run(target=self.reload)

    def reload(self):
        try:
            metadata_cache = util.MetadataUtil(self.sf_basic_config)
            self.sublconsole.showlog('start to reload metadata cache')
            metadata_cache.reload()
            self.sublconsole.showlog('reload metadata cache done!')
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')


class DeleteMetadataCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("search_metadata", {
            "action_type": "delete"
        })

class SearchMetadataCommand(sublime_plugin.WindowCommand):
    def run(self, action_type=None, sel_category=None):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.action_type = action_type
            self.metadata_cache = util.MetadataUtil(self.sf_basic_config)
            thread = self.sublconsole.thread_run(target=self.metadata_cache.get_cache)
            self.open_category_panel(thread, sel_category, 0)
        except Exception as e:
            self.sublconsole.showlog(e)
            return
    
    def open_category_panel(self, thread, sel_category, timeout=200):
        if thread.is_alive():
            self.sublconsole.showlog("loading metadata , please wait...")
            timeout=200
            sublime.set_timeout(lambda: self.open_category_panel(thread, sel_category, timeout), timeout)
            return
        self.sublconsole.showlog("load metadata ok!")

        try:
            self.sel_category_list = self.metadata_cache.get_meta_category()
            if sel_category and sel_category in self.sel_category_list:
                self.open_detail_panel(sel_category)
            else:
                self.window.show_quick_panel(self.sel_category_list, self.panel_done, sublime.MONOSPACE_FONT)
        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_category_list):
            return
        sel_category = self.sel_category_list[picked]
        self.open_detail_panel(sel_category)
    
    def open_detail_panel(self, sel_category):
        self.sel_category = sel_category
        self.catory_meta_dict = self.metadata_cache.get_meta_by_category(sel_category)
        self.sel_meta_list = self.metadata_cache.get_meta_namelist(sel_category)
        self.window.show_quick_panel(self.sel_meta_list, self.panel_meta_done, sublime.MONOSPACE_FONT)

    def panel_meta_done(self, picked):
        if 0 > picked < len(self.sel_meta_list):
            return
        self.sel_meta_fullName = self.sel_meta_list[picked]
        sel_meta = self.catory_meta_dict[self.sel_meta_fullName]
        if self.action_type == "delete":
            self.delete_meta(sel_meta)
        else:
            self.metadata_cache.open_in_web(sel_meta)

    def delete_meta(self, sel_meta):
        self.sublconsole.debug('>>>delete meta')
        self.sublconsole.debug(sel_meta)
        message = "Are you sure to delete %s?  id=%s " % (sel_meta["fileName"], sel_meta["id"])
        if not sublime.ok_cancel_dialog(message, "Delete!!"): 
            self.sublconsole.showlog('cancel delete metadata: ' + sel_meta["fileName"])
            return
        self.sublconsole.showlog('start to delete metadata : ' + sel_meta["fileName"])
        if sel_meta["id"]:
            self.sel_meta = sel_meta
            self.sublconsole.thread_run(target=self.delete_meta_process)
        else:
            self.sublconsole.showlog('the id is empty : ' + sel_meta["fileName"])
        return
        
    def delete_meta_process(self):
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        # status_code, result = tooling_api.deleteApexClass(self.sel_meta["id"])
        status_code, result = tooling_api.deleteMetadata(self.sel_meta["metadata_type"], self.sel_meta["id"])
        self.sublconsole.showlog(status_code)
        self.sublconsole.showlog(result)


class BuildPackageCommand(sublime_plugin.WindowCommand):
    def run(self, save_path=None, is_open=True, build_type="FromServer"):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.is_open = is_open
        self.build_type = build_type
        if save_path:
            self.save_path = save_path
            self.on_input(self.save_path)
        else:
            tstr = datetime.now().strftime('%Y%m%d_%H%M%S')
            if self.build_type == "CopyFiles":
                self.save_path = os.path.join(self.sf_basic_config.get_sfdc_module_dir() , "src_%s" % tstr)
            else:
                self.save_path = os.path.join(self.sf_basic_config.get_sfdc_module_dir() , "package.%s.xml" % tstr)
            self.window.show_input_panel("Input your save path: " , 
                self.save_path, self.on_input, None, None)
            self.sublconsole.thread_run(target=self.on_input)

    def on_input(self, args):
        self.save_path = args
        self.sublconsole.thread_run(target=self.buildPackage)

    def buildPackage(self):
        if self.build_type == "FromServer":
            self._buildPackageFromServer()
        elif self.build_type == "FromLocal":
            self._buildPackageFromFiles()
        elif self.build_type == "CopyFiles":
            open_files = [ _view.file_name() for _view in self.sf_basic_config.window.views()]
            if len(open_files) > 0:
                self.window.run_command("migration_tool_builder", {
                    "type" : "CopyFiles",
                    "file_list" : open_files,
                    "copy_to_dir" : self.save_path
                })
            else:
                self.sublconsole.showlog("Nothing to do!")

    def _buildPackageFromFiles(self):
        open_files = [ _view.file_name() for _view in self.sf_basic_config.window.views()]
        migration_util = util.MigrationToolUtil(sf_basic_config=self.sf_basic_config, is_auto_download=False)
        migration_util.build_package_xml(self.save_path, open_files, self.settings["api_version"])

    def _buildPackageFromServer(self):
        meta_api = util.sf_login(self.sf_basic_config, Soap_Type=MetadataApi)
        packagexml = meta_api.buildPackageXml()
        self.sublconsole.save_and_open_in_panel(packagexml, "", self.save_path , is_open=self.is_open)
    
class RetrieveZipCommand(sublime_plugin.WindowCommand):
    def run(self, retrieve_type=None):

        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.retrieve_type = retrieve_type
        self.meta_api = util.sf_login(self.sf_basic_config, Soap_Type=MetadataApi)

        describeMetadataResult = self.meta_api.describeMetadata()
        self.describeMetadataResult = describeMetadataResult["metadataObjects"]
        self._init_default_picked_list()
        self.is_picked_all = False
        self.sublconsole.thread_run(target=self.main)

    def main(self):
        tstr = datetime.now().strftime('%Y%m%d%H%M%S')
        if self.retrieve_type == "src":
            # self.file_name = "src_" + datetime.now().strftime('%Y%m%d_%H%M%S')
            self.file_name = ""
            self.save_path = save_dir =  self.sf_basic_config.get_src_root()
            self.sublconsole.thread_run(target=self._show_panel)
        else:
            self.file_name = "%s_%s_src.zip" % (self.sf_basic_config.get_project_name() , tstr)
            save_dir =  self.sf_basic_config.get_zip_dir()
            self.full_path = os.path.join(save_dir, self.file_name)
            self.window.show_input_panel("Please Input your save path: " , 
                self.full_path, self.on_input, None, None)

    def _init_default_picked_list(self):
        self.current_picked_list = []
        for data in self.describeMetadataResult:
            if data["xmlName"] in ["ApexClass", "ApexComponent", "ApexPage", "ApexTrigger", "ApexPage", "CustomObject", "AuraDefinitionBundle"]:
                self.current_picked_list.append(data)

    def on_input(self, args):
        self.save_path = args
        self.sublconsole.thread_run(target=self._show_panel)

    def _show_panel(self):
        self.sel_key_list, self.sel_show_list = self._get_sel_data()
        self.window.show_quick_panel(self.sel_show_list, self.panel_done,sublime.MONOSPACE_FONT)

    def _set_sel_data(self, sel_data):
        if sel_data in self.current_picked_list:
            self.current_picked_list.remove(sel_data)
        else:
            self.current_picked_list.append(sel_data)
            
    def _get_sel_data(self):
        all_data = self.describeMetadataResult
        sel_key_list = ["__Start_To_Retrive__", "__Select_MetaData__"]
        sel_show_list = ["Start To Retrive", "Select/Unselect All"]
        sel_key_list2 = []
        sel_show_list2 = []
        for data in all_data:
            if data in self.current_picked_list:
                sel_sign_str = "✓" 
                sel_show_list.append( "    [%s] %s" % (sel_sign_str, str(data["xmlName"])))
                sel_key_list.append(data)
            else:
                sel_sign_str = "X"
                sel_show_list2.append( "    [%s] %s" % (sel_sign_str, str(data["xmlName"])))
                sel_key_list2.append(data)
        sel_show_list.extend(sel_show_list2)
        sel_key_list.extend(sel_key_list2)
        return sel_key_list,sel_show_list

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_key_list):
            return
        sel_data = self.sel_key_list[picked]
        if picked > 1:
            self._set_sel_data(sel_data)
            self._show_panel()
        elif picked == 1:
            self.is_picked_all = not self.is_picked_all
            if self.is_picked_all:
                self.current_picked_list = [data for data in self.describeMetadataResult]
            else:
                self.current_picked_list = []
            self._show_panel()
        elif picked == 0:
            self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        self.sublconsole.showlog('start to retrieve source')
        self.zipfile_path = self.save_path
        if self.retrieve_type == "src":
            self.zipfile_path = os.path.join(self.save_path, "package.zip")

        try:
            self._backup_src(self.save_path)
            self.meta_api.retrieveZip(zip_file_name=self.zipfile_path, retrive_metadata_objects=self.current_picked_list)
            if self.retrieve_type == "src":
                self.meta_api.unzipfile(self.zipfile_path, self.save_path, self.settings["src_dir"])
                os.remove(self.zipfile_path)
                self.window.run_command("reload_metadata_cache")
        except Exception as e:
            self.sublconsole.showlog(e)
            return
    
    def _backup_src(self, root_path):
        if self.retrieve_type == "src":
            src_path = self.sf_basic_config.get_src_dir()
            if os.path.exists(src_path):
                backup_dir = os.path.join(root_path, "src_backup")
                new_src_name = "src_" + datetime.now().strftime('%Y%m%d_%H%M%S')
                new_src_path = os.path.join(backup_dir, new_src_name)
                message = "The src folder is exist. Start to backup the src to %s ?" % (new_src_name)
                if sublime.ok_cancel_dialog(message, "OK!"): 
                    self.sublconsole.close_views(src_path)
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    self.sublconsole.showlog('start to backup source')
                    shutil.copytree(src_path, new_src_path)
                    self.sublconsole.showlog('start to delete src folder')
                    if os.path.exists(src_path):
                        shutil.rmtree(src_path)

class RetrieveSrcCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("retrieve_zip", {
            "retrieve_type": "src"
        })


##########################################################################################
# Metadata File Operation
##########################################################################################
class DeleteThisMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        if file_name is None:
            return
        DeleteMetadataHelper().run_delete_meta(file_name)

# delete_aura
class DeleteAuraCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        if len(dirs) == 0: return False
        aura_name = os.path.basename(dirs[0])
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        if dir_name != "aura":
            self.sublconsole.showlog("It seems not a lightinig component! ")
            return

        DeleteMetadataHelper().run_delete_meta(dirs[0])
 
    def is_enabled(self, dirs):
        if len(dirs) == 0: return False
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        return dir_name == "aura"

class DeleteMetadataHelper:
    def run_delete_meta(self, file_name):
        self.file_name = file_name
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.meta_attr = self.metadata_util.get_meta_attr(self.file_name)
        if not self.meta_attr or "id" not in self.meta_attr :
            self.sublconsole.show_in_dialog("can not find metadata id")
            return
        self._delete_meta()

    def _delete_meta(self):
        sel_meta = self.meta_attr
        message = "Are you sure to delete %s?  id=%s " % (sel_meta["fileName"], sel_meta["id"])
        if not sublime.ok_cancel_dialog(message, "Delete!!"): 
            self.sublconsole.showlog('cancel delete metadata: ' + sel_meta["fileName"])
            return
        self.sublconsole.showlog('start to delete metadata : ' + sel_meta["fileName"])
        if sel_meta["id"]:
            self.sel_meta = sel_meta
            self.sublconsole.thread_run(target=self._delete_from_server)
        else:
            self.sublconsole.showlog('the id is empty : ' + sel_meta["fileName"])
        return

    def _delete_from_server(self):
        self.sublconsole.showlog("delete server file: id=%s" % (self.meta_attr["id"]))
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        try:
            status_code, result = tooling_api.deleteMetadata(self.sel_meta["metadata_type"], self.sel_meta["id"])
            self.sublconsole.debug(status_code)
            if status_code == 204:
                self.sublconsole.showlog('delete file done!')
                self._delete_metadata_cache()
                self._delete_local_file()
            else:
                self.sublconsole.showlog('delete error code ' + str(status_code))
                self.sublconsole.showlog(result)
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')
    
    def _delete_local_file(self):
        if os.path.isdir(self.file_name):
            message = "Do you want to delete local lightning files?  %s" % (self.file_name)
            if sublime.ok_cancel_dialog(message, "Delete!!"): 
                self.sublconsole.showlog("delete local file start: " + self.file_name)
                shutil.rmtree(self.file_name)
                self.sublconsole.showlog("delete local file done! ")
        elif os.path.isfile(self.file_name):
            os.remove(self.file_name)
            self.sublconsole.showlog("delete local file done! " + self.file_name)

    def _delete_metadata_cache(self):
        self.metadata_util.delete_metadata_cache(self.file_name)

# open_metadata_in_browser
# open_in_browser
class OpenMetadataInBrowserCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.file_name = file_name = self.view.file_name()
        if file_name is None:
            return
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.sublconsole.showlog("select file: " + file_name)
        self.meta_attr = self.metadata_util.get_meta_attr(file_name)
        # if self.meta_attr['metadata_type'] == 'AuraDefinitionBundle':
        #     self.meta_attr = self.metadata_util.get_meta_attr(os.path.dirname(file_name))
        self.sublconsole.debug(self.meta_attr)
        self.metadata_util.open_in_web(self.meta_attr)

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        return True


# open_aura
class OpenAuraCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        if len(dirs) == 0: return False
        aura_name = os.path.basename(dirs[0])
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        if dir_name != "aura":
            self.sublconsole.showlog("It seems not a lightinig component! ")
            return
        
        file_name = dirs[0]
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.sublconsole.showlog("select file: " + file_name)
        self.meta_attr = self.metadata_util.get_meta_attr(file_name)
        self.sublconsole.debug(self.meta_attr)
        self.metadata_util.open_in_web(self.meta_attr)

    def is_enabled(self, dirs):
        if len(dirs) == 0: return False
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        return dir_name == "aura"


class UpdateMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.file_name = file_name = self.view.file_name()
        if file_name is None:
            return
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.meta_attr = self.metadata_util.get_meta_attr(file_name)

        self.sublconsole.showlog("select file: " + file_name)
        self.sublconsole.debug(self.meta_attr)
        self.sublconsole.thread_run(target=self.updateMeta)
    
    def updateMeta(self, deep=0):
        if not self.meta_attr or "id" not in self.meta_attr or not self.meta_attr["id"]:
            if deep < 1:
                self.sublconsole.showlog("metadata id not found, start to refresh cache...")
                self.metadata_util.update_metadata_cache_by_filename(self.file_name)
                self.meta_attr = self.metadata_util.get_meta_attr(self.file_name)
                deep = deep + 1
                self.updateMeta(deep)
                return
            self.sublconsole.showlog("metadata id not found, please check it!")
            # self.sublconsole.showlog(self.meta_attr)
            return
        self.sublconsole.showlog("start to update metadata : Id=%s, Name=%s, Type=%s." % (self.meta_attr["id"], self.meta_attr["file_name"], self.meta_attr["type"]))

        msg = self.metadata_util.is_modified(self.file_name, self.meta_attr["id"])
        if msg:
            self.sublconsole.showlog(msg)
            if not sublime.ok_cancel_dialog(msg, "Update!"):
                msg = 'Do you want to show the different betweent sfdc server?'
                if sublime.ok_cancel_dialog(msg, "Show Different"):
                    self.sublconsole.showlog("start to show different")
                    self.view.run_command("refresh_metadata", {"is_diff": True})
                return
        
        if self.meta_attr["is_lux"]:
            self._updateLux()
        else:
            self._update_meta_to_server()
    
    # Lightning update
    def _updateLux(self):
        body = self.view.substr(sublime.Region(0, self.view.size()))
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        status_code, result = tooling_api.updateLux(self.meta_attr["id"], {"Source" : body})
        if status_code > 300:
            self.sublconsole.showlog(result, type="error")
        else:
            self.metadata_util.update_metadata_cache(self.file_name, self.meta_attr["id"])
            self.sublconsole.showlog("update metadata done: Id=%s, Name=%s, Type=%s." % (self.meta_attr["id"], self.meta_attr["file_name"], self.meta_attr["type"]))

    # apex, visualforce, trigger, component update
    def _update_meta_to_server(self):
        body = self.view.substr(sublime.Region(0, self.view.size()))
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        result = tooling_api.updateMetadata(self.meta_attr["type"], self.meta_attr["id"], body)
        self.sublconsole.showlog(result)

        if not result["is_success"]:
            self._show_err_popuo(result)
        else:
            self.metadata_util.update_metadata_cache(self.file_name, self.meta_attr["id"])
            self.sublconsole.showlog("update metadata done: Id=%s, Name=%s, Type=%s." % (self.meta_attr["id"], self.meta_attr["file_name"], self.meta_attr["type"]))

    def _show_err_popuo(self, result):
        self.view.run_command("goto_line", {"line": result["lineNumber"]})
        self.view.run_command("expand_selection", {"to":"line"})
        msg = """<div><h4>Compile %s</h4>
                        <p style="color: red">
                        <b>%s</b> at line <b>%s</b> column <b>%s</b>
                        </p>
                    </div>
                """ % (result["problemType"], result["problem"], result["lineNumber"],result["columnNumber"])
        self.view.show_popup(msg)

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        
        attr = baseutil.SysIo().get_file_attr(file_name)
        return attr["is_lux"] or attr["is_src"]

class RefreshMetadataCommand(sublime_plugin.TextCommand):
    def run(self, edit, is_diff=False):
        self.org_file_full_path = file_name = self.view.file_name()
        if file_name is None:
            return
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.meta_attr = self.metadata_util.get_meta_attr(file_name)
        
        self.sublconsole.showlog("select file: " + file_name)
        self.sublconsole.debug(self.meta_attr)
        
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole.thread_run(target=self.refreshMeta)

        self.is_diff = is_diff
        if self.is_diff:
            self.save_file_full_path = os.path.join(self.sf_basic_config.get_tmp_dir(), self.meta_attr["file_name"])
        else:
            self.save_file_full_path = file_name

    def refreshMeta(self, deep=0):
        if not self.meta_attr or "id" not in self.meta_attr or not self.meta_attr["id"]:
            if deep < 1:
                self.sublconsole.showlog("metadata id not found, start to refresh cache...")
                self.metadata_util.update_metadata_cache_by_filename(self.org_file_full_path)
                self.meta_attr = self.metadata_util.get_meta_attr(self.org_file_full_path)
                deep = deep + 1
                self.refreshMeta(deep)
                return
            self.sublconsole.showlog("metadata id not found, please check it!")
            # self.sublconsole.showlog(self.meta_attr)
            return
        self.sublconsole.showlog("start to refresh metadata : Id=%s, Name=%s, Type=%s." % (self.meta_attr["id"], self.meta_attr["file_name"], self.meta_attr["type"]))
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        try:
            status_code, result = tooling_api.getMetadata(self.meta_attr["type"], self.meta_attr["id"])
            # self.sublconsole.showlog(result)
            if status_code == 200:
                self.sublconsole.showlog('refresh success')
                if self.meta_attr["type"] in ["ApexClass", "ApexTrigger"]:
                    content_key = "Body"
                elif self.meta_attr["type"] in ["ApexPage", "ApexComponent"]:
                    content_key = "Markup"
                elif self.meta_attr["type"] in ["AuraDefinition"]:
                    content_key = "Source"
                self.sublconsole.save_file(self.save_file_full_path, result[content_key])

                if self.is_diff:
                    util.DiffUtil(self.sf_basic_config).diff(self.org_file_full_path, self.save_file_full_path)
                else:
                    self.metadata_util.update_metadata_cache(self.save_file_full_path, self.meta_attr["id"])
            else:
                self.sublconsole.showlog('refresh error code ' + str(status_code))
                self.sublconsole.showlog(result)
        except Exception as ex:
            self.sublconsole.showlog(ex, 'error')

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False

        attr = baseutil.SysIo().get_file_attr(file_name)
        return attr["is_src"] or attr["is_lux"]


# refresh_aura
class RefreshAuraCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)

        if len(dirs) == 0: return False
        aura_name = os.path.basename(dirs[0])
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        if dir_name != "aura":
            self.sublconsole.showlog("It seems not a lightinig component! ")
            return
        
        self.aura_dir = dirs[0]
        self.sublconsole.thread_run(target=self._refresh_aura)
    
    def _refresh_aura(self):
        attr = baseutil.SysIo().get_file_attr(self.aura_dir)
        aura_soql = "SELECT Id, CreatedDate, CreatedById, CreatedBy.Name, LastModifiedDate, LastModifiedById, LastModifiedBy.Name, AuraDefinitionBundle.DeveloperName, AuraDefinitionBundleId, DefType, Format, Source FROM AuraDefinition"
        aura_soql = aura_soql + " Where AuraDefinitionBundle.DeveloperName = '%s'" % (attr["file_name"])
        tooling_api = util.sf_login(self.sf_basic_config, Soap_Type=ToolingApi)
        result = tooling_api.query(aura_soql)
        if 'records' in result and len(result['records']) > 0:
            for file in os.listdir(self.aura_dir):
                if not "-meta.xml" in file:
                    os.remove( os.path.join(self.aura_dir, file) )
            for AuraDefinition in result['records']:
                if AuraDefinition["DefType"] in AURA_DEFTYPE_EXT:
                    fileName = attr["file_name"] + AURA_DEFTYPE_EXT[AuraDefinition["DefType"]]
                    self.sublconsole.save_file( os.path.join(self.aura_dir, fileName), AuraDefinition["Source"])
            self.metadata_util.update_lux_metas(result['records'])
            self.sublconsole.showlog("Refresh lightinig ok! ")
        else:
            self.sublconsole.showlog("Refresh lightinig error! ", type="error")

    def is_enabled(self, dirs):
        if len(dirs) == 0: return False
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        return dir_name == "aura"

##########################################################################################
# Apex Test
##########################################################################################
class RunTestClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.file_name = file_name = self.view.file_name()
        if file_name is None:
            return
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.meta_attr = self.metadata_util.get_meta_attr(file_name)
        
        if self.meta_attr and "id" in self.meta_attr:
            self.sublconsole.thread_run(target=self.metadata_util.run_test, args=([self.meta_attr["id"]], ))
        else:
            self.sublconsole.showlog('can not found id!')

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        contents = self.view.substr(sublime.Region(0, self.view.size()))

        check = os.path.isfile(file_name) and \
                file_name.find(".cls") > -1  and \
                (( contents.find("@isTest") > -1 ) or \
                 ( contents.find("testMethod") > -1 )
                )
        return check

class ShowCodeCoverageCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.metadata_util = util.MetadataUtil(self.sf_basic_config)
        self.sublconsole.thread_run(target=self._main)

    def _main(self):
        apex_coverage = "\n".join(self.metadata_util.get_apex_coverage())
        file_name = datetime.now().strftime('ApexCoverage_%Y%m%d_%H%M%S.log')
        self.sublconsole.save_and_open_in_panel(apex_coverage, self.sf_basic_config.get_test_dir(), file_name , is_open=True)


##########################################################################################
# Sobject
##########################################################################################
class OpenSobjectInBrowserCommand(sublime_plugin.WindowCommand):
    def run(self, view_type="data_list"):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.sobject_util = util.SobjectUtil(self.sf_basic_config)
            self.view_type = view_type
            thread = self.sublconsole.thread_run(target=self.sobject_util.get_cache)
            self.open_category_panel(thread, 0)
        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def open_category_panel(self, thread, timeout=200):
        if thread.is_alive():
            self.sublconsole.showlog("loading sobject cache , please wait...")
            timeout=200
            sublime.set_timeout(lambda: self.open_category_panel(thread, timeout), timeout)
            return
        self.sublconsole.showlog("load sobject cache ok!")
        self.sobject_show_list, self.sobject_name_list = self.sobject_util.get_sobject_name_list_for_sel()
        self.window.show_quick_panel(self.sobject_show_list, self.panel_done, sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sobject_name_list):
            return
        sel_sobject = self.sobject_name_list[picked]
        self.sublconsole.debug(sel_sobject)
        if self.view_type == "create_trigger":
            self._create_trigger(sel_sobject)
        else:
            self.sobject_util.open_in_web(sel_sobject)

    def _create_trigger(self, sel_sobject):
        self.window.run_command("new_metadata", {
            "type": "ApexTrigger",
            "object_name" : sel_sobject
        })

class PreviewLightningAppCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        full_path = self.view.file_name()
        if full_path != None:
            str_list = full_path.split(baseutil.get_slash())
            file_name = str(str_list[-1])

            self.sf_basic_config = SfBasicConfig()
            sf = util.sf_login(self.sf_basic_config)
            returl = '/c/' + file_name
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                        .format(instance=sf.sf_instance,
                                sid=sf.session_id,
                                returl=returl))
            util.open_in_default_browser(self.sf_basic_config, login_url)

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        return os.path.isfile(file_name) and file_name.find(".app") > -1 

class PreviewVfCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        full_path = self.view.file_name()
        if full_path != None:
            str_list = full_path.split(baseutil.get_slash())
            file_name = str(str_list[-1])

            self.sf_basic_config = SfBasicConfig()
            sf = util.sf_login(self.sf_basic_config)
            returl = '/apex/' + file_name.replace('.page', '')
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                        .format(instance=sf.sf_instance,
                                sid=sf.session_id,
                                returl=returl))
            util.open_in_default_browser(self.sf_basic_config, login_url)

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        return os.path.isfile(file_name) and file_name.find(".page") > -1 


##########################################################################################
# Side bar : Refresh sf metadata
# TODO
##########################################################################################
class RefreshDirCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        if not dirs: 
            self.sublconsole.showlog("It seems not a directory! ")
            return
        
        dir_name = os.path.basename(dirs[0])
        if dir_name not in SF_FLODER_TO_TYPE: 
            self.sublconsole.showlog("Not support type : %s ." % (dir_name))
            return
        
        self.meta_type = SF_FLODER_TO_TYPE[dir_name]
        self.sublconsole.thread_run(target=self.main)

    def main(self):
        self.sublconsole.showlog("start to refresh %s..." % (self.meta_type))
        # self.settings.get_tmp_dir()
        # self.meta_api.retrieveZip(zip_file_name=tmp, retrive_metadata_objects=self.current_picked_list)