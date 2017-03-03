import sublime,sublime_plugin
import os,time,json

SFDC_HUANGXY_SETTINGS = "sfdc.huangxy.sublime-settings"
SFDC_CACHE_SETTINGS = "salesforcexytools.cache.sublime-settings"
AUTHENTICATION_OAUTH2 = "oauth2"
AUTHENTICATION_PASSWORD = "password"
AUTHENTICATION_MAVENSMATE = "mavensmate"

def load():
    # Load all settings
    settings = {}

    # Load sublime-settings
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    settings["default_project"] = s.get("default_project")
    settings["default_api_version"] = s.get("default_api_version")
    settings["debug_levels"] = s.get("debug_levels")
    settings["authentication"] = s.get("authentication")
    settings["xyfloder"] = s.get("xy_output_floder")
    settings["dataloader_encoding"] = s.get("dataloader_encoding")
    settings["soql_select_limit"] = s.get("soql_select_limit")
    settings["projects"] = projects = s.get("projects")
    settings["projects"] = projects
    settings["browsers"] = s.get("browsers")
    settings["default_browser"] = s.get("default_browser")
    settings["home_workspace"] = s.get("home_workspace")
    if not settings["home_workspace"]:
        settings["home_workspace"] = os.path.expanduser('~')
        # if os.name == 'nt':
        #     settings["home_workspace"] = os.path.expanduser('~')
        # else:
        #     settings["home_workspace"] = os.path.expandvars('$HOME')


    # settings["use_mavensmate_setting"] = s.get("use_mavensmate_setting")
    settings["use_oauth2"] = (settings["authentication"] == AUTHENTICATION_OAUTH2)
    settings["use_password"] = (settings["authentication"] == AUTHENTICATION_PASSWORD)
    settings["use_mavensmate_setting"] = (settings["authentication"] == AUTHENTICATION_MAVENSMATE)

    if not (settings["use_oauth2"] or settings["use_password"] or settings["use_mavensmate_setting"]):
        settings["use_oauth2"] = True
        update_authentication_setting()

    settings["default_project_value"] = {}

    print('------->load mm setting start')
    if settings["use_mavensmate_setting"]:
        mm_settings = load_mavensmate_setting()
        settings["default_project_value"] = mm_settings
        # print('------->load mm setting end')
        # print(json.dumps(settings, indent=4))
        # settings.update(mm_settings)
        # return settings
    print('------->load mm setting end')

    for project_key in projects.keys():
        project_value = projects[project_key]
        project_value['project_name'] = project_key
        if "api_version" not in project_value:
            project_value["api_version"] = settings["default_api_version"]

        # load session file
        session_path = os.path.join(project_value["workspace"],settings["xyfloder"], 'config', '.session')
        if os.path.isfile(session_path):
            session_json = parse_json_from_file(session_path)
            # print('session_json-->')
            # print(session_path)
            # print(session_json)
            project_value.update(session_json)

        # find default_project
        if project_key == settings['default_project'] and not settings["use_mavensmate_setting"]: 
            settings["default_project_value"] = project_value
    
    # print('------->load end')
    # print(json.dumps(settings, indent=4))
    return settings

# test = load()
# print(test)
# print(test["default_project_value"])

def load_mavensmate_setting(window=None):
    # Load all settings
    settings = {}

    if window == None:
        window = sublime.active_window()

    mm_session_path = os.path.join(window.folders()[0], "config", ".session")
    mm_credentials_path = os.path.join(window.folders()[0], "config", ".credentials")
    # mavensmate v0.0.11, oauth2
    if os.path.isfile(mm_credentials_path):
        mm_session = parse_json_from_file(mm_credentials_path)
        settings.update(mm_session)
    # mavensmate v0.0.10
    elif os.path.isfile(mm_session_path):
        mm_session = parse_json_from_file(mm_session_path)
        settings.update(mm_session)
    else:
        msg = 'mavensmate session file is missing,\n'
        msg += 'please re-auth again, Or Create project again!\n'
        msg += 'Re-auth:\n'
        msg += '\t\t「MavensMate -> Project -> Salesforce authentication.」\n'
        raise Exception(msg)

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
        
    # mavensmate v0.0.11, oauth2
    if "orgType" in settings:
        settings["is_sandbox"] = (settings["orgType"] == "sandbox") 
    # mavensmate v0.0.10
    elif "environment" in settings:
        settings["is_sandbox"] = (settings["environment"] == "sandbox") 
    else:
        raise Exception('mavensmate settings file error!!')

    if "accessToken" in settings:
        settings["access_token"] = settings["accessToken"]
    else:
        raise Exception('session error!! login again,please.')


    if "instanceUrl" in settings:
        settings["instance_url"] = settings["instanceUrl"]
        
    # if "sid" in settings:
    #     settings["sessionId"] = settings["sid"]

    # mavensmate v0.0.11, oauth2
    if "project_name" in settings:
        settings["default_project"] = settings["project_name"]
    # mavensmate v0.0.10
    elif "projectName" in settings:
        settings["default_project"] = settings["projectName"]
        settings["project_name"] = settings["projectName"]

    if "api_version" not in settings:
        settings["api_version"] = "37.0"


    if "workspace" in settings:
        settings["workspace"] = os.path.join(settings["workspace"], settings["default_project"])

    # if "password" not in settings:
    #     settings["password"] = ""

    # if "security_token" not in settings:
    #     settings["security_token"] = ""

    # print('load_mavensmate_setting over')
    # print(settings)

    return settings

def get_browser_setting():
    dirs = []
    settings = load()
    default_browser = settings["default_browser"]

    for browser in settings["browsers"]:
        broswer_path = settings["browsers"][browser]
        if os.path.exists(broswer_path):
            dirs.append([browser,broswer_path])
    if settings["browsers"]["chrome"]:
        broswer_path = settings["browsers"]["chrome"]
        if os.path.exists(broswer_path):
            browser = "chrome-private"
            dirs.append([browser,broswer_path])
    # default browser
    if not dirs:
        dirs.append(["default",""])
    return dirs

def get_browser_setting2():
    dirs = []
    settings = load()
    default_browser = settings["default_browser"]

    for browser in settings["browsers"]:
        broswer_path = settings["browsers"][browser]
        if os.path.exists(broswer_path):
            if default_browser == browser:
                browser_key = '[○]' + browser
            else:
                browser_key = '[X]' + browser
            dirs.append([browser_key,browser])
    if settings["browsers"]["chrome"]:
        broswer_path = settings["browsers"]["chrome"]
        if os.path.exists(broswer_path):
            browser = "chrome-private"
            if default_browser == browser:
                browser_key = '[○]' + browser
            else:
                browser_key = '[X]' + browser
            dirs.append([browser_key,browser])
    # default browser
    if not dirs:
        dirs.append(["[○]default","default"])
    return dirs


def get_default_browser():
    settings = load()
    default_browser = settings["default_browser"]
    browser_map = {}

    for browser in settings["browsers"]:
        broswer_path = settings["browsers"][browser]
        if os.path.exists(broswer_path):
            if default_browser == browser:
                browser_map['name'] = browser
                browser_map['path'] = broswer_path
                return browser_map
            elif default_browser == "chrome-private" and browser == "chrome":
                browser_map['name'] = "chrome-private"
                browser_map['path'] = broswer_path
                return browser_map

    browser_map['name'] = 'default'
    browser_map['path'] = ''
    return browser_map


def mm_project_directory(window=None):
    if window == None:
        window = sublime.active_window()
    folders = window.folders()
    if len(folders) > 0:
        return window.folders()[0]


# def get_project_settings(window=None):
#     if window == None:
#         window = sublime.active_window()
#     try:
#        return parse_json_from_file(os.path.join(window.folders()[0],"config",".settings"))
#     except:
#         # raise BaseException("Could not load project settings")
#         print("Could not load project settings")



def get_project_settings(project_name=''):
    settings = load()
    projects = settings["projects"]

    project = {}
    if project_name:
        projects = settings["projects"]
        if project_name in projects:
            project = projects[project_name]
    else:
        project = settings["default_project_value"]

    return project


def parse_json_from_file(location):
    try:
        json_data = open(location)
        data = json.load(json_data)
        json_data.close()
        return data
    except:
        return {}

def update_authentication_setting(auth_type=AUTHENTICATION_OAUTH2):
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    s.set("authentication", auth_type)
    sublime.save_settings(SFDC_HUANGXY_SETTINGS)



def update_default_browser(browser_name):
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    # Save the updated settings
    s.set("default_browser", browser_name)
    sublime.save_settings(SFDC_HUANGXY_SETTINGS)


def update_default_project(default_project):
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    # Save the updated settings
    s.set("default_project", default_project)
    sublime.save_settings(SFDC_HUANGXY_SETTINGS)


def update_project_session(default_project):
    s = sublime.load_settings(SFDC_HUANGXY_SETTINGS)
    # Save the updated settings
    s.set("default_project", default_project)
    sublime.save_settings(SFDC_HUANGXY_SETTINGS)