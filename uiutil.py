# special
import sublime
import sublime_plugin
import os,datetime
import threading
import subprocess
from .salesforce.myconsole import MyConsole


##########################################################################################
#some base util for ui
##########################################################################################
def xstr(s):
    if s is None:
        return ''
    else:
        return str(s)


##########################################################################################
#Sublime Panel class
##########################################################################################
class XyPanel(object):
    panels = {}

    def __init__(self, name):
        self.name = name

    def scroll_to_bottom(self, panel):
        size = panel.size()
        sublime.set_timeout(lambda : panel.show(size, True), 2)

    @classmethod
    def show_in_panel(cls, window, panel_name, message_str):
        panel = cls.panels.get(panel_name)
        if not panel:
            panel = window.get_output_panel(panel_name)
            panel.settings().set('syntax', 'Packages/Java/Java.tmLanguage')
            panel.settings().set('word_wrap', True)
            panel.settings().set('gutter', True)
            panel.settings().set('line_numbers', True)
            cls.panels[panel_name] = panel

        window.run_command('show_panel', {
                'panel': 'output.' + panel_name
        })
        if message_str:
            message_str += '\n'

        panel.run_command("append", {
                "characters": message_str
        })

        size = panel.size()
        sublime.set_timeout(lambda : panel.show(size, True), 2)



##########################################################################################
#MyConsole
##########################################################################################
class SublConsole(MyConsole):
    def __init__(self, sf_basic_config):
        self.sf_basic_config = sf_basic_config
        self.window = sf_basic_config.window
        self.window_id = str(self.window.id())
        # start_str = ">" * 80
        # self.showlog(start_str)

    def showlog(self, obj, type='info', show_time=True):
        panel_name = "salesforcexytools-log-" + self.window_id
        if show_time:
            now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            now = now + "[" + type + "] "
            msg = now + str(obj)
        else:
            msg = str(obj)
        XyPanel.show_in_panel(self.window, panel_name, msg)

    def debug(self, obj):
        print(obj)
        # SFDC_HUANGXY_SETTINGS = "sfdc.huangxy.sublime-settings"
        # s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
        # if s.get("is_debug"):
        #     self.showlog(obj, 'debug')

    # def debug(self, msg):
    #     # debug(msg)
    #     print(msg)

    def log(self, msg):
        self.showlog(msg)

    def show_in_dialog(self, message_str):
        sublime.message_dialog(xstr(message_str))

    def status(self, msg, thread=False):
        if not thread:
            self.window.status_message(msg)
        else:
            sublime.set_timeout(lambda: self.status(msg), 0)

    def handle_thread(self, thread, msg=None, counter=0, direction=1, width=8):
        if thread.is_alive():
            next = counter + direction
            if next > width:
                direction = -1
            elif next < 0:
                direction = 1
            bar = [' '] * (width + 1)
            bar[counter] = '='
            counter += direction
            self.status('%s [%s]' % (msg, ''.join(bar)))
            sublime.set_timeout(lambda: self.handle_thread(thread, msg,  counter,
                                direction, width), 100)
        else:
            self.status(' ok ')

    def open_file(self, file_path):
        if os.path.isfile(file_path): 
            self.window.open_file(file_path)

    def save_and_open_in_panel(self, message_str, save_dir, save_file_name , is_open=True):
        print('----->save_file_name ' + save_file_name)
        print('----->is_open ' + xstr(is_open))
        save_path =  os.path.join(save_dir, save_file_name)
        self.debug(save_dir)
        self.debug(save_file_name)
        self.showlog("save file : " + save_path)

        # delete old file
        if os.path.isfile(save_path): 
            os.remove(save_path)

        # save file
        self.save_file(save_path, message_str)
        if is_open: 
            self.open_file(save_path)
        return save_path

    def save_file(self, full_path, content, encoding='utf-8'):
        if not os.path.exists(os.path.dirname(full_path)):
            self.showlog("mkdir: " + os.path.dirname(full_path))
            os.makedirs(os.path.dirname(full_path))
        try:
            fp = open(full_path, "w", encoding=encoding)
            fp.write(content)
        except Exception as e:
            self.showlog('save file error! ' + full_path)
            self.showlog(e)
        finally:
            fp.close()

    def show_in_new_tab(self, message_str, name=None):
        view = self.window.new_file()
        if name:
            view.set_name(name)
        view.run_command("insert_snippet", 
            {
                "contents": xstr(message_str)
            }
        )

    def open_project(self, open_path):
        executable_path = sublime.executable_path()
        if sublime.platform() == 'osx':
            app_path = executable_path[:executable_path.rfind(".app/") + 5]
            executable_path = app_path + "Contents/SharedSupport/bin/subl"

        if sublime.platform() == "windows":
            subprocess.Popen('"{0}" --project "{1}"'.format(executable_path, open_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            process = subprocess.Popen([executable_path, '--project', open_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = process.communicate()
            self.debug(stdout)
            self.showlog(stderr)

    def open_in_new_tab(self, message, tab_name):
        view = self.window.new_file()
        view.run_command("new_view", {
            "name": tab_name,
            "input": message
        })

    def insert_str(self, message_str):
        self.window.run_command("insert_snippet", 
            {
                "contents": xstr(message_str)
            }
        )

    def thread_run(self, group=None, target=None, name=None, args=()):
        thread = threading.Thread(target=target, args=args, name=name)
        thread.start()
        self.handle_thread(thread)
        return thread
    
    def close_views(self, main_path):
        for _view in self.window.views():
            file_name = _view.file_name()
            if file_name and main_path in file_name:
                _view.close()
