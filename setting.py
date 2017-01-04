import sublime,sublime_plugin
import os,time,json

SFDC_HUANGXY_SETTINGS = "sfdc.huangxy.sublime-settings"

def load():
    # Load all settings
    settings = {}

    # Load sublime-settings
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    settings["default_project"] = s.get("default_project")
    settings["default_api_version"] = s.get("default_api_version")
    settings["debug_levels"] = s.get("debug_levels")
    settings["use_mavensmate_setting"] = s.get("use_mavensmate_setting")
    settings["xyfloder"] = s.get("xy_output_floder")
    settings["dataloader_encoding"] = s.get("dataloader_encoding")
    settings["soql_select_limit"] = s.get("soql_select_limit")
    settings["projects"] = projects = s.get("projects")
    settings["projects"] = projects
    settings["browsers"] = s.get("browsers")

    if settings["use_mavensmate_setting"]:
        mm_settings = load_mavensmate_setting()
        settings.update(mm_settings)
        return settings

    usernames = []
    for project_key in projects.keys():
        project_value = projects[project_key]
        if project_key == settings['default_project']: 
            settings["default_project_value"] = project_value
        else:
            usernames.append(project_value["username"])

    if not settings["default_project_value"]:
        return

    # print(settings["default_project_value"])
    default_project_value = settings["default_project_value"]

    settings["loginUrl"] = default_project_value["loginUrl"]
    settings["password"] = default_project_value["password"]
    settings["security_token"] = default_project_value["security_token"]
    settings["username"] = default_project_value["username"]
    settings["workspace"] = default_project_value["workspace"]
    if "api_version" in default_project_value:
        settings["api_version"] = default_project_value["api_version"]
    else:
        settings["api_version"] = settings["default_api_version"]
        

    # url bug???
    settings["soap_login_url"] = settings["loginUrl"] + "/services/Soap/s/{0}".format(settings["api_version"])
    settings["base_url"] = settings["loginUrl"] + "/services/data/v{0}".format(settings["api_version"])
    settings["apex_url"] = settings["loginUrl"] + "/services/apexrest/v{0}".format(settings["api_version"])

    # if settings["loginUrl"] == "https://login.salesforce.com":
    #     isSandbox = False
    settings["is_sandbox"] = default_project_value["is_sandbox"]

    print('------->load end')
    return settings



def load_mavensmate_setting(window=None):
    # Load all settings
    settings = {}

    if window == None:
        window = sublime.active_window()

    mm_session_path = os.path.join(window.folders()[0], "config", ".session")
    if os.path.isfile(mm_session_path):
        mm_session = parse_json_from_file(mm_session_path)
        settings.update(mm_session)
    else:
        raise Exception('mavensmate session file is missing')

    mm_settings_path = os.path.join(window.folders()[0], "config", ".settings")
    if os.path.isfile(mm_settings_path):
        mm_setting = parse_json_from_file(mm_settings_path)
        settings.update(mm_setting)
    else:
        raise Exception('mavensmate settings file is missing')

    mm_debug_path = os.path.join(window.folders()[0], "config", ".debug")
    if os.path.isfile(mm_debug_path):
        mm_setting = parse_json_from_file(mm_debug_path)
        settings.update(mm_setting)
    # else:
    #     raise Exception('mavensmate debug file is missing')
        
    if "environment" in settings:
        settings["is_sandbox"] = (settings["environment"] == "sandbox") 

    if "accessToken" in settings:
        settings["sessionId"] = settings["accessToken"]
    else:
        raise Exception('session error!! login again,please.')

    # if "sid" in settings:
    #     settings["sessionId"] = settings["sid"]
        
    if "projectName" in settings:
        settings["default_project"] = settings["projectName"]

    if "api_version" not in settings:
        settings["api_version"] = "37.0"

    # if "password" not in settings:
    #     settings["password"] = ""

    # if "security_token" not in settings:
    #     settings["security_token"] = ""

    # print(settings)

    return settings

def get_browser_setting():
    dirs = []
    settings = load()
    for browser in settings["browsers"]:
        broswer_path = settings["browsers"][browser]
        if os.path.exists(broswer_path):
            dirs.append([browser,broswer_path])
    if settings["browsers"]["chrome"]:
        broswer_path = settings["browsers"]["chrome"]
        if os.path.exists(broswer_path):
            dirs.append(["chrome-private",broswer_path])
    # default browser
    if not dirs:
        dirs.append(["default",""])
    return dirs


def mm_project_directory(window=None):
    if window == None:
        window = sublime.active_window()
    folders = window.folders()
    if len(folders) > 0:
        return window.folders()[0]


def get_project_settings(window=None):
    if window == None:
        window = sublime.active_window()
    try:
       return parse_json_from_file(os.path.join(window.folders()[0],"config",".settings"))
    except:
        # raise BaseException("Could not load project settings")
        print("Could not load project settings")


def parse_json_from_file(location):
    try:
        json_data = open(location)
        data = json.load(json_data)
        json_data.close()
        return data
    except:
        return {}

