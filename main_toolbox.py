import sublime
import sublime_plugin
import os,subprocess,threading
from .setting import SfBasicConfig
from .templates import AntConfig
from .uiutil import SublConsole
from . import baseutil
from . import util
from .salesforce import MetadataApi

#deploy open files
class DeployDirCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        files = baseutil.SysIo().get_file_list(dirs[0])
        self.window.run_command("run_ant_migration_tool", {
            "deploy_file_list" : files
        })

#Migration Tool
class RunAntMigrationToolCommand(sublime_plugin.TextCommand):
    def run(self, edit, deploy_file_list=None):
        self.window = sublime.active_window()
        if deploy_file_list:
            self.open_files = deploy_file_list
            self.current_file = None
            self.sel_type_list = ["Deploy Directory", "Deploy Directory To Server(check only)"]
            self.sel_type_key_list = ["DeployOpenFiles", "CheckDeployOpenFiles"]
        else:
            self.open_files = [ _view.file_name() for _view in self.window.views()]
            self.current_file = self.view.file_name()
            self.sel_type_list = ["Build Ant Metadata Tool", "Backup Metadata", "Deploy Open Files To Server", "Deploy Open Files To Server(check only)"]
            self.sel_type_key_list = ["Build", "Backup", "DeployOpenFiles", "CheckDeployOpenFiles"]

        if self.current_file:
            file_path, file_name = os.path.split(self.current_file)
            self.sel_type_list.append("Deploy Current File To Server : %s" % file_name)
            self.sel_type_list.append("Deploy Current File To Server : %s (check only)" % file_name)
            self.sel_type_key_list.append("DeployOne")
            self.sel_type_key_list.append("CheckDeployOne")
        self.window.show_quick_panel(self.sel_type_list, self.panel_done, sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_type_key_list):
            return
        sel_type = self.sel_type_key_list[picked]
        if self.current_file and sel_type in ["DeployOne", "CheckDeployOne"]:
            self.open_files = [self.current_file]

        self.window.run_command("migration_tool_builder", {
            "type" : sel_type,
            "file_list" : self.open_files
        })

#Migration Tool
class MigrationToolBuilderCommand(sublime_plugin.WindowCommand):
    def run(self, type=None, file_list=None, copy_to_dir=None):
        try:
            self.ant_cmd_map = {
                "CheckDeployOpenFiles" : "ant deployCodeCheckOnly",
                "DeployOpenFiles" : "ant deployCodeNoTestLevelSpecified",
                "DeployOne" : "ant deployCodeNoTestLevelSpecified",
                "CheckDeployOne" : "ant deployCodeCheckOnly"
            }
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.save_dir =  self.sf_basic_config.get_ant_migration_tool_dir()
            self.type = type
            self.copy_to_dir = copy_to_dir
            self.osutil = util.OsUtil(self.sf_basic_config)
            if self._is_not_exist():
                message = "Do you want to build ant migration tool first?"
                if not sublime.ok_cancel_dialog(message, "Yes!"):
                    return
                self.sublconsole.thread_run(target=self.build_migration_tools, args=(self.save_dir, ))
                return

            if type == "Backup":
                self.run_it()
            elif type == "Build":
                self.sublconsole.thread_run(target=self.build_migration_tools, args=(self.save_dir, ))
            elif type == "CopyFiles":
                self.sublconsole.thread_run(target=self.copy_open_files, args=(file_list, ))
            elif type in self.ant_cmd_map:
                self.deploy_open_files(file_list, type)
        except Exception as ex:
            self.sublconsole.showlog(ex)
            pass

    def _is_not_exist(self):
        prop = os.path.join(self.save_dir, "build.properties")
        xml = os.path.join(self.save_dir, "build.xml")
        if not os.path.exists(prop) or not os.path.exists(xml):
            return True
        return False

    def copy_open_files(self, file_list):
        migration_util = util.MigrationToolUtil()
        if self.copy_to_dir:
            deploy_root_dir = self.copy_to_dir
        else:
            deploy_root_dir = self.sf_basic_config.get_deploy_tmp_dir()
        migration_util.copy_deploy_files(file_list, deploy_root_dir, str(self.settings["api_version"]))
        self.sublconsole.showlog("Copy Files Done ! " + deploy_root_dir)
    
    def deploy_open_files(self, file_list, type):
        message = "Are you sure to deploy files?"
        self.sublconsole.showlog("Ready to deploy : \n" + "\n".join(file_list))
        if not sublime.ok_cancel_dialog(message, "Yes!"):
            self.sublconsole.showlog("Cancel deploy !")
            return
        self.copy_open_files(file_list)
        
        cmd = [self.osutil.get_cd_cmd(self.save_dir), self._get_deploy_cmd(type)]
        self.osutil.os_run(cmd)
    
    def _get_deploy_cmd(self, type):
        return self.ant_cmd_map[type]

    def build_migration_tools(self, args):
        # download ant-salesforce.jar
        migration_util = util.MigrationToolUtil()

        self.sublconsole.showlog('start to build migration tool')
        config_data = {
            "username" : self.settings["username"],
            "password" : self.settings["password"],
            "serverurl" : self.settings["loginUrl"],
            "jar_path" : migration_util.get_jar_path()
        }
        ant_config = AntConfig()
        ant_config.build_migration_tools(save_path=args, config_data=config_data)

        save_path = os.path.join(args, "package.xml")
        meta_api = util.sf_login(self.sf_basic_config, Soap_Type=MetadataApi)
        packagexml = meta_api.buildPackageXml()
        self.sublconsole.save_and_open_in_panel(packagexml, "", save_path , is_open=False)
        self.sublconsole.showlog('build migration tool success!')
        # self.run_it()

    def run_it(self):
        if os.path.exists(self.save_dir):
            cmd = [self.osutil.get_cd_cmd(self.save_dir), "metadata-backup"]
            self.osutil.os_run(cmd)


#Run Dataloader
class RunAntDataloaderCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command("dataloader_config", {
            "is_run": True
        })

#Dataloader Config
class DataloaderConfigCommand(sublime_plugin.WindowCommand):
    def run(self, is_run=False):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sobject_util = util.SobjectUtil()
        self.picked_list = []
        self.save_dir = os.path.join(self.sf_basic_config.get_work_dir(), "AntDataloader")
        self.is_run = is_run
        self.osutil = util.OsUtil(self.sf_basic_config)
        if self.is_run:
            self.run_it()
            return
        self._show_panel()

    def _show_panel(self):
        self.sobject_name_list, self.sobject_show_list = self._get_sobject_panel_data()
        self.window.show_quick_panel(self.sobject_show_list, self.panel_done,sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sobject_name_list):
            return
        sel_data = self.sobject_name_list[picked]
        if picked > 1:
            self.sublconsole.showlog(sel_data)
            self._set_select_list(sel_data)
            self._show_panel()
        elif picked == 0:
            self.sublconsole.thread_run(target=self._build_dataloader)
            # self._build_dataloader_ant_xml()

    def _build_dataloader(self):
        self.sublconsole.showlog("start to build dataloader")
        self.sublconsole.showlog(self.picked_list)
        sobject_info_list = self.sobject_util.get_sobject_info_list(self.picked_list)
        ANT_TMP_STR = """<export file="%s" object="%s" soql="%s"/>"""
        self.ant_xml_list = [ ANT_TMP_STR % (sobject_info["name"],sobject_info["name"],sobject_info["soql"]) for sobject_info in sobject_info_list ]
        self._build_ant_dataloader()
        self.run_it()
        
    def _build_ant_dataloader(self):
        self.dlutil = util.DataloaderUtil(self.sf_basic_config)
        encryptionPassword = self.dlutil.getEncryptionPassword()
        self.sublconsole.showlog('Salesforce URL : ' + self.settings["loginUrl"])
        self.sublconsole.showlog('Salesforce EncryptionPassword : ' + encryptionPassword)
        self.sublconsole.showlog('Dataloader Jar Path : ' + self.dlutil.get_jar_path())
        config_data = {
            "username" : self.settings["username"],
            "EncryptionPassword" : encryptionPassword,
            "serverurl" : self.settings["loginUrl"],
            "dataloader_jar_path" : self.dlutil.get_jar_path(),
            "ant_export_xml" : "\n        ".join(self.ant_xml_list)
        }
        ant_config = AntConfig()
        ant_config.build_ant_dataloader(save_path=self.save_dir, config_data=config_data)
        self.sublconsole.showlog('build ant dataloader success! path : %s' % self.save_dir)

    def _set_select_list(self, sel_data):
        if sel_data in self.picked_list:
            self.picked_list.remove(sel_data)
        else:
            self.picked_list.append(sel_data)

    def _get_sobject_panel_data(self):
        all_sobject = self.sobject_util.get_cache()
        sobject_name_list = ["__Start__", "__Select_Soject__"]
        sobject_show_list = ["Start To Config", "Select Soject"]
        for sobject_info in all_sobject["sobjects"].values():
            sel_sign_str = "✓" if str(sobject_info["name"]) in self.picked_list else "X"
            sobject_show_list.append( "    [%s] %s , %s" % (sel_sign_str, str(sobject_info["name"]), str(sobject_info["label"])))
            sobject_name_list.append(str(sobject_info["name"]))
        return sobject_name_list,sobject_show_list
        
    def run_it(self):
        if self.is_run and os.path.exists(self.save_dir):
            cmd = [self.osutil.get_cd_cmd(self.save_dir), "ant"]
            self.osutil.os_run(cmd)


class CopyAuraCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.showlog('Copy Salesforce Lightning Component, Please input your new compent Name.')
        self.sublconsole.showlog('path: ' + dirs[0])
        self.window.show_input_panel("Please Input FullPath of fileName: " , 
            '', self.on_input, None, None)
        self.dir = dirs[0]

    def on_input(self, args):
        self.sublconsole.showlog('New Lightning compent Name : ' + args)
        sysio = baseutil.SysIo()
        sysio.copy_lightning(self.dir, args)
    
    def is_enabled(self, dirs):
        if len(dirs) == 0: return False
        dir_path = os.path.dirname(dirs[0])
        dir_name = os.path.basename(dir_path)
        return dir_name == "aura"

class OpenAntDataloaderXmlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)
        file_path = os.path.join(self.sf_basic_config.get_work_dir(), "AntDataloader", "build.xml")
        self.sublconsole.open_file(file_path)


class OpenWithCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        apps = self.sf_basic_config.get_apps()

        self.sel_type_list = list(apps.keys())
        self.sel_type_key_list = list(apps.values())
        self.sf_basic_config.window.show_quick_panel(self.sel_type_list, self.panel_done, sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_type_key_list):
            return
        app_name = self.sel_type_key_list[picked]
        
        file_name = self.view.file_name()
        print(file_name)
        cmd = app_name.replace("{file_dir}", os.path.dirname(file_name)).replace("{file_name}", file_name)
        print(cmd)
        subprocess.Popen(cmd)

    def is_visible(self):
        return sublime.platform() == "windows"

class OpenCopyFilesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        txt = self.view.substr(sublime.Region(0, self.view.size()))
        file_list = txt.split("\n")
        window = sublime.active_window()
        for file_name in file_list:
            if os.path.isfile(file_name) and not file_name.endswith("-meta.xml"): 
                window.open_file(file_name)

    def is_enabled(self):
        if not self.view: return False
        if not self.view.file_name(): return False
        return self.view.file_name().endswith("copyfile.txt")

class OpenShellCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        cmd = ["cmd /k cd /d " + self.sf_basic_config.get_work_dir()]
        util.OsUtil(self.sf_basic_config).run_in_os_termial(cmd)

    def is_visible(self):
        return sublime.platform() == "windows"

class TestxCommand(sublime_plugin.WindowCommand):
    def run(self):
        # subprocess.Popen
        import subprocess, sys
        winmerge = """C:\\Program Files (x86)\\WinMerge\\WinMergeU.exe"""
        cmd = "cmd"
        # os.system(cmd)
        subprocess.Popen(cmd)
