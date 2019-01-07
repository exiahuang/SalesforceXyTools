import sublime
import sublime_plugin
import os
import json
from datetime import datetime
from .baseutil import SysIo
from .setting import SfBasicConfig
from .uiutil import SublConsole



##########################################################################################
#Project Config
##########################################################################################
class ProjectConfigCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.showlog('open config: ' + self.sf_basic_config.get_project_config_path())
        self.sublconsole.open_file(self.sf_basic_config.get_project_config_path())


class NewXyProjectCommand(sublime_plugin.WindowCommand):
    def run(self, retrieve_type=None):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)

        home = self.sf_basic_config.get_user_home_dir()
        tstr = datetime.now().strftime('YourProjectName_%Y%m%d_%H%M%S')
        self.save_dir =  os.path.join(home, tstr)
        self.sublconsole.debug(self.window.extract_variables())
        self.window.show_input_panel("Please Input your save path: " , 
            self.save_dir, self.on_input, None, None)

    def on_input(self, args):
        self.sublconsole.debug(args)
        if not os.path.exists(args):
            os.makedirs(args)
        project_name = os.path.basename(args)
        sublime_settings_path = os.path.join(args, project_name + ".sublime-project")
        if not os.path.exists(sublime_settings_path):
            self._mk_project_file(args, sublime_settings_path)
        self.sublconsole.open_project(sublime_settings_path)
        self._open_config(args)
    
    def _mk_project_file(self, project_path, file_path):
        sysio = SysIo()
        self.sublconsole.debug("make project file")
        sublime_settings = {"folders":[{
            "file_exclude_patterns": [
                "*.*-meta.xml"
            ], 
            "folder_exclude_patterns": [
                self.sf_basic_config.get_xyfolder() + "/.tmp",
                self.sf_basic_config.get_xyfolder() + "/MetadataBackupTools/codepkg"
            ], 
            "path": project_path
        }]}
        sysio.save_file(file_path, json.dumps(sublime_settings, indent=4))

    def _open_config(self, project_dir):
        self.sf_basic_config = SfBasicConfig(project_dir=project_dir)
        self.sublconsole.showlog('open config: ' + self.sf_basic_config.get_project_config_path())
        # # TODO
        # self.sublconsole.open_file(self.sf_basic_config.get_project_config_path())
        # sublime.active_window().open_file(os.path.join(project_dir, ".xyconfig", "xyconfig.json"))
        # sublime.active_window().open_file(self.sf_basic_config.get_project_config_path())

#handles compiling to server on save
class SaveListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        sf_basic_config = SfBasicConfig()
        settings = sf_basic_config.get_setting()
        username = settings["username"]
        if username != 'input your username' and username != '':
            if sf_basic_config.get_auto_save_to_server():
                sf_basic_config.window.run_command("update_metadata")

class ProjectConfigWizardCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.showlog('start to config project')

        self._init_input_conf()
        self.on_input(None)

    def on_input(self, args):
        print(args)
        if self.input_index > 0:
            pre_conf = self.input_conf[self.input_index-1]
            ui_type = pre_conf["type"]
            if ui_type == "input":
                pre_conf["value"] = args
            elif ui_type == "select":
                if 0 <= args and args < len(pre_conf["option-v"]):
                    pre_conf["value"] = pre_conf["option-v"][args]

        if self.input_index < len(self.input_conf):
            current_conf = self.input_conf[self.input_index]
            if current_conf["type"] == "input":
                caption = "Please Input your %s: " % current_conf["key"]
                self.window.show_input_panel(caption, current_conf["value"], self.on_input, None, None)
            elif current_conf["type"] == "select":
                show_opts = current_conf["option"]
                self.window.show_quick_panel(show_opts, self.on_input, sublime.MONOSPACE_FONT)
            self.input_index = self.input_index + 1
        else:
            self._save_conf()

    def _init_input_conf(self):
        settings = self.sf_basic_config.get_setting()

        self.input_index = 0
        self.input_conf = (
            {"key" : "is_sandbox",
             "value" : settings["is_sandbox"],
             "type" : "select",
             "option" : [ "Is Sandbox ? True", "Is Sandbox ? False"],
             "option-v" : [True, False]
            },
            {"key" : "username",
             "value" : settings["username"],
             "type" : "input" },
            {"key" : "password",
             "value" : settings["password"],
             "type" : "input" },
            {"key" : "security_token",
             "value" : settings["security_token"],
             "type" : "input" },
            {"key" : "api_version",
             "value" : settings["api_version"],
             "type" : "select",
             "option" : ["45.0(pre-release)", "44.0", "43.0", "42.0", "41.0", "40.0", "39.0", "38.0", "37.0", "36.0"],
             "option-v" : [45.0, 44.0, 43.0, 42.0, 41.0, 40.0, 39.0, 38.0, 37.0, 36.0]
            },
            {"key" : "auto_save_to_server",
             "value" : self.sf_basic_config.get_auto_save_to_server(),
             "type" : "select",
             "option" : [ "Auto Save to Server ? No.", "Auto Save to Server ? Yes."],
             "option-v" : [False, True]
            },
            {"key" : "default_browser",
             "value" : settings["default_browser"],
             "type" : "select",
             "option" : self.sf_basic_config.get_browser_setting2(),
             "option-v" : [item[1] for item in self.sf_basic_config.get_browser_setting2()]
            }
        )

    def _save_conf(self):
        project_config = {}
        for a_conf in self.input_conf:
            project_config[a_conf["key"]] = a_conf["value"]
        self.sublconsole.debug(project_config)
        self.sf_basic_config.update_project_config(project_config)
        self.sublconsole.showlog('config project done!')


class ProxyConfigWizardCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.showlog('start to config proxy')

        self._init_input_conf()
        self.on_input(None)

    def on_input(self, args):
        print(args)
        if self.input_index > 0:
            pre_conf = self.input_conf[self.input_index-1]
            ui_type = pre_conf["type"]
            if ui_type == "input":
                pre_conf["value"] = args
            elif ui_type == "select":
                if 0 <= args and args < len(pre_conf["option-v"]):
                    pre_conf["value"] = pre_conf["option-v"][args]

        if self.input_index < len(self.input_conf):
            current_conf = self.input_conf[self.input_index]
            if current_conf["type"] == "input":
                caption = "Please Input your %s: " % current_conf["key"]
                self.window.show_input_panel(caption, current_conf["value"], self.on_input, None, None)
            elif current_conf["type"] == "select":
                show_opts = current_conf["option"]
                self.window.show_quick_panel(show_opts, self.on_input, sublime.MONOSPACE_FONT)
            self.input_index = self.input_index + 1
        else:
            self._save_conf()

    def _init_input_conf(self):
        proxy_config = self.sf_basic_config.get_proxy()

        self.input_index = 0
        self.input_conf = (
            {"key" : "use_proxy",
             "value" : proxy_config["use_proxy"],
             "type" : "select",
             "option" : [ "Use Proxy.", "Don't use Proxy."],
             "option-v" : [True, False]
            },
            {"key" : "proxyhost",
             "value" : proxy_config["proxyhost"],
             "type" : "input" },
            {"key" : "proxyport",
             "value" : proxy_config["proxyport"],
             "type" : "input" },
            {"key" : "proxypassword",
             "value" : proxy_config["proxypassword"],
             "type" : "input" },
            {"key" : "proxyuser",
             "value" : proxy_config["proxyuser"],
             "type" : "input"
            }
        )

    def _save_conf(self):
        proxy_config = {}
        for a_conf in self.input_conf:
            proxy_config[a_conf["key"]] = a_conf["value"]
        project_config = {}
        project_config["proxy"] = proxy_config
        self.sf_basic_config.update_project_config(project_config)
        self.sublconsole.showlog('config proxy done!')

