import sublime
import sublime_plugin
import os, re
import json
from .setting import SfBasicConfig
from .uiutil import SublConsole
from . import util

SFDX_SETTINGS = "sfdx.sublime-settings"

class OpenSfdxSettingCommand(sublime_plugin.WindowCommand):
    def run(self):
        SETTING_PATH = os.path.join(sublime.packages_path(), "User", SFDX_SETTINGS)
        if not os.path.exists(SETTING_PATH):
            s = sublime.load_settings(SFDX_SETTINGS)
            tasks = s.get("tasks")
            custom_env = s.get("custom_env")
            s.set("tasks", tasks)
            s.set("custom_env", custom_env)
            sublime.save_settings(SFDX_SETTINGS)
        self.window.run_command("open_file", {
            "file": SETTING_PATH
        })


class SfdxCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.window = sublime.active_window()
        self.osutil = util.OsUtil(self.sf_basic_config)

        s = sublime.load_settings(SFDX_SETTINGS)
        tasks = s.get("tasks")
        
        self.env = s.get("custom_env")
        self.env.update(DxEnv().get_env())
        self.env.update(CommandEnv(self.window, self.sf_basic_config.get_project_dir()).get_env())
        self.sel_keys = [task["label"] for task in tasks]
        self.sel_vals = [task for task in tasks]

        self.window.show_quick_panel(self.sel_keys, self.panel_done, sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.sel_keys):
            return
        self.task = self.sel_vals[picked]
        is_os_termial = "os_termial" in self.task and self.task["os_termial"]

        if "SFDX_ALIAS" in self.task["command"]:
            if not self.env["SFDX_ALIAS"] or len(self.env["SFDX_ALIAS"]) == 0:
                self.sublconsole.showlog("sfdx alias empty! please check it!")
        Cmder().run(self.window, self.env, self.task["command"], console=self.sublconsole.showlog, is_os_termial=is_os_termial, encoding='UTF-8')

class DxEnv():
    def get_env(self):
        return {
            "SFDX_ALIAS" : self.__get_alias(),
        }

    def __get_alias(self):
        return list(self.__get_alias_dict().keys())

    def __get_alias_dict(self):
        home = os.path.expanduser("~")
        dx_alias_file = os.path.join(home, ".sfdx", "alias.json")
        alias = {}
        try:
            if os.path.exists(dx_alias_file):
                f = open(dx_alias_file)
                data = json.load(f)
                alias = data["orgs"]
                f.close()
        except Exception as ex:
            pass
        return alias

class CommandEnv():
    def __init__(self, window, workspaceFolder):
        self.window = window
        self.workspaceFolder = workspaceFolder

    def get_env(self):
    	# // ${selectedText} - the current selected text in the active file
        file = self.window.active_view().file_name()
        if file is None : file = ""
        fileBasenameNoExtension, fileExtname = os.path.splitext(os.path.basename(file))
        env = {
            "cwd" : self.workspaceFolder,
            "workspaceFolder" : self.workspaceFolder,
            "workspaceFolderBasename" : os.path.basename(self.workspaceFolder),
            "file" : file,
            "fileBasenameNoExtension": fileBasenameNoExtension,
            "fileExtname": fileExtname,
            "relativeFile" : file.replace(self.workspaceFolder, ""),
            "fileBasename": os.path.basename(file),
            "fileDirname" : os.path.dirname(file),
            "selectedText" : self.__get_sel_text(),
        }
        # print(env)
        return env

    def __get_sel_text(self):
        try:
            view = self.window.active_view()
            sel = view.sel()
            region1 = sel[0]
            selectionText = view.substr(region1)
            return selectionText
        except Exception as ex:
            pass
            return ""


class Cmder():
    def run(self, window, command_env, command, console=print, is_os_termial=False, encoding='UTF-8'):
        self.index = 0
        self.window = window
        self.console = console
        self.encoding = encoding
        self.is_os_termial = is_os_termial
        self.env = command_env
        self.command = command
        self.params = self.__get_command_params(command)
        self.osutil = util.OsUtil()
        UiWizard(command_params=self.params, 
                window=self.window, 
                callback=self.on_wizard_done).run()
    
    def on_wizard_done(self, user_params):
        command = self.command

        for key, val in self.env.items():
            if type(val) is str:
                command = command.replace("${%s}" % key, val)

        msgs = []
        for param in self.__get_sys_env(command):
            command = command.replace(param["param"], param["value"])
            if not param["value"]: msgs.append("%s is null! please check it." % param["param"])
        for param in user_params:
            command = command.replace(param["param"], param["value"])
            if not param["value"]: msgs.append("%s is null! please check it." % param["param"])
        
        if len(msgs) > 0:
            self.console("\n".join(msgs))
        else:
            self.console(command)
            cmds = [self.osutil.get_cd_cmd(self.env["workspaceFolder"]), command]
            if self.is_os_termial:
                self.osutil.run_in_os_termial(cmds)
            else:
                self.osutil.run_in_sublime_cmd(cmds, encoding=self.encoding)

    def __get_sys_env(self, command):
        pattern = r"\${(env)(\s)*:(\s)*([^} ]+)(\s)*}"
        matchedList = re.findall(pattern, command)
        sys_env = []
        if matchedList:
            for param in matchedList:
                key = param[3]
                sys_env.append({
                    "param" : "${%s%s:%s%s%s}" % param,
                    "key" : key,
                    "value" : os.getenv(key, default=""),
                    "type" : param[0]
                })
        return sys_env

    def __get_command_params(self, command):
        pattern = r"\${(input|select)(\s)*:(\s)*([^} ]+)(\s)*}"
        matchedList = re.findall(pattern, command)
        params = []
        if matchedList:
            for param in matchedList:
                key = param[3]
                data = {
                        "param" : "${%s%s:%s%s%s}" % param,
                        "key" : key,
                        "value" : "",
                        "type" : param[0]
                    }
                if data["type"] == "input":
                    if key in self.env:
                        data["value"] = str(self.env[key])
                elif data["type"] == "select":
                    data["option"] = data["option-v"] = []
                    if key in self.env:
                        if isinstance(self.env[key], list):
                            data["option"] = data["option-v"] = self.env[key]

                params.append(data)
        return params


class UiWizard():
    def __init__(self, command_params, window, callback):
        self.index = 0
        self.command_params = command_params
        self.window = window
        self.callback = callback

    def run(self, args=None):
        if self.index > 0:
            pre_data = self.command_params[self.index-1]
            ui_type = pre_data["type"]
            if ui_type == "input":
                pre_data["value"] = args
            elif ui_type == "select":
                if 0 <= args and args < len(pre_data["option-v"]):
                    pre_data["value"] = pre_data["option-v"][args]

        if self.index < len(self.command_params):
            curr_data = self.command_params[self.index]
            if curr_data["type"] == "input":
                caption = "Please Input your %s: " % curr_data["key"]
                self.window.show_input_panel(caption, curr_data["value"], self.run, None, None)
            elif curr_data["type"] == "select":
                show_opts = curr_data["option"]
                self.window.show_quick_panel(show_opts, self.run, sublime.MONOSPACE_FONT)
            self.index = self.index + 1
        else:
            self.callback(self.command_params)


class XyOpenUrlCommand(sublime_plugin.ApplicationCommand):
    def run(command, url):
        import webbrowser
        webbrowser.open_new_tab(url)
