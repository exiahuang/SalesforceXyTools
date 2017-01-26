import sublime
import sublime_plugin
import datetime
import os,sys,xdrlib
import json
import webbrowser
import random
import platform
import re

from .salesforce import *
from . import setting

##########################################################################################
#Salesforce Util
##########################################################################################
def sf_login(project_name='', Soap_Type=Soap):
    settings = setting.load()

    try:
        project = {}
        if project_name:
            projects = settings["projects"]
            project = projects[project_name]
        else:
            project = settings["default_project_value"]

        # print('settings--->')
        # print(json.dumps(settings, indent=4))
        print('project--->')
        print(json.dumps(project, indent=4))


        if project_name:
            # TODO
            sf = Soap_Type(username=project["username"], 
                        password=project["password"], 
                        security_token=project["security_token"], 
                        sandbox=project["is_sandbox"],
                        version=project["api_version"],
                        settings=settings
                        )

        elif settings["use_mavensmate_setting"] or settings["use_oauth2"]:
            sf = Soap_Type( session_id=project["access_token"] ,
                            instance_url=project["instance_url"],
                            sandbox=project["is_sandbox"],
                            version=project["api_version"],
                            settings=settings
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
            sf = Soap_Type(username=project["username"], 
                        password=project["password"], 
                        security_token=project["security_token"], 
                        sandbox=project["is_sandbox"],
                        version=project["api_version"],
                        settings=settings
                        )

        sf.settings = settings
        print(sf)
        print(sf.session_id)
        print('------->')
        return sf
    except Exception as e:
        if settings["use_oauth2"]:
            print('----->sf_login error')
            print(e)
            sf_oauth2()
        else:
            show_in_dialog('Login Error! ' + xstr(e))
        return


from .libs import server
sfdc_oauth_server = None

def re_auth():
    settings = setting.load()
    if settings["use_oauth2"]:
        sf_oauth2()

def sf_oauth2():
    from .libs import auth
    settings = setting.load()
    default_project_value = settings["default_project_value"]
    is_sandbox = default_project_value["is_sandbox"]

    if refresh_token():
        return

    server_info = sublime.load_settings("sfdc.server.sublime-settings")
    client_id = server_info.get("client_id")
    client_secret = server_info.get("client_secret")
    redirect_uri = server_info.get("redirect_uri")
    oauth = auth.SalesforceOAuth2(client_id, client_secret, redirect_uri, is_sandbox)
    authorize_url = oauth.authorize_url()
    print('authorize_url-->')
    print(authorize_url)
    start_server()
    open_in_default_browser(authorize_url)

def start_server():
    global sfdc_oauth_server
    if sfdc_oauth_server is None:
        sfdc_oauth_server = server.Server()

def stop_server():
    global sfdc_oauth_server
    if sfdc_oauth_server is not None:
        sfdc_oauth_server.stop()
        sfdc_oauth_server = None
        
def refresh_token():
    from .libs import auth
    settings = setting.load()

    if not settings["use_oauth2"]:
        return False

    default_project_value = settings["default_project_value"]
    is_sandbox = default_project_value["is_sandbox"]

    if "refresh_token" not in default_project_value:
        print("refresh token missing")
        return False

    server_info = sublime.load_settings("sfdc.server.sublime-settings")
    client_id = server_info.get("client_id")
    client_secret = server_info.get("client_secret")
    redirect_uri = server_info.get("redirect_uri")
    oauth = auth.SalesforceOAuth2(client_id, client_secret, redirect_uri, is_sandbox)
    refresh_token = default_project_value["refresh_token"]
    print(refresh_token)
    response_json = oauth.refresh_token(refresh_token)
    print(response_json)

    if "error" in response_json:
        return False

    if "refresh_token" not in response_json:
        response_json["refresh_token"] = refresh_token

    save_session(response_json)
    print("------->refresh_token ok!")
    return True


##########################################################################################
#Sublime Util
##########################################################################################


def insert_str(message_str):
    view = sublime.active_window()
    view.run_command("insert_snippet", 
        {
            "contents": xstr(message_str)
        }
    )

# def append_str(message_str):
#     view = sublime.active_window()
#     view.run_command("append", 
#         {
#             "contents": xstr(message_str)
#         }
#     )

def show_in_new_tab(message_str):
    view = sublime.active_window().new_file()
    view.run_command("insert_snippet", 
        {
            "contents": xstr(message_str)
        }
    )

def show_in_dialog(message_str):
    sublime.message_dialog(xstr(message_str))


def show_in_status(message_str):
    sublime.status_message(xstr(message_str))


def show_in_panel(message_str):
    # sublime.message_dialog(message_str)
    XyPanel.show_in_panel("xypanel", xstr(message_str))


def open_file(file_path):
    if os.path.isfile(file_path): 
        sublime.active_window().open_file(file_path)

def save_and_open_in_panel(message_str, save_file_name , is_open=True, sub_folder='' ,default_path='' ):
    print('----->save_file_name ' + save_file_name)
    print('----->is_open ' + xstr(is_open))
    if not default_path:
        default_path=get_default_floder()
    save_path =  os.path.join(default_path, sub_folder, save_file_name)

    # delete old file
    if os.path.isfile(save_path): 
        os.remove(save_path)

    # save file
    save_file(save_path, message_str)
    if is_open: 
        open_file(save_path)
    return save_path


class XyPanel(object):
    panels = {}

    def __init__(self, name):
        self.name = name

    @classmethod
    def show_in_panel(cls, panel_name, message_str):
        panel = cls.panels.get(panel_name)

        window = sublime.active_window()
        if not panel:
            panel = window.get_output_panel(panel_name)
            panel.settings().set('syntax', 'Packages/Java/Java.tmLanguage')
            panel.settings().set('color_scheme', 'Packages/Color Scheme - Default/Monokai.tmTheme')
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

def status(msg, thread=False):
    if not thread:
        sublime.status_message(msg)
    else:
        sublime.set_timeout(lambda: status(msg), 0)
        
def handle_thread(thread, msg=None, counter=0, direction=1, width=8):
    if thread.is_alive():
        next = counter + direction
        if next > width:
            direction = -1
        elif next < 0:
            direction = 1
        bar = [' '] * (width + 1)
        bar[counter] = '='
        counter += direction
        status('%s [%s]' % (msg, ''.join(bar)))
        sublime.set_timeout(lambda: handle_thread(thread, msg,  counter,
                            direction, width), 100)
    else:
        status(' ok ')

# # Code lifted from https://github.com/randy3k/ProjectManager/blob/master/pm.py
# def subl(args=[]):
#     # learnt from SideBarEnhancements
#     executable_path = sublime.executable_path()
#     print('executable_path: '+ executable_path)

#     if sublime.platform() == 'linux':
#         subprocess.Popen([executable_path] + [args])
#     if sublime.platform() == 'osx':
#         app_path = executable_path[:executable_path.rfind(".app/") + 5]
#         executable_path = app_path + "Contents/SharedSupport/bin/subl"
#         subprocess.Popen([executable_path] + args)
#     if sublime.platform() == "windows":
#         def fix_focus():
#             window = sublime.active_window()
#             view = window.active_view()
#             window.run_command('focus_neighboring_group')
#             window.focus_view(view)
#         sublime.set_timeout(fix_focus, 300)


##########################################################################################
#Python Util
##########################################################################################
def get_slash():
    sysstr = platform.system()
    if(sysstr =="Windows"):
        slash = "\\"
    else:
        slash = "/"
    return slash

def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str

def random_phone(randomlength=11):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str

def random_float(length=2, scale=0):
    val = round(random.random() * 10 ** (length-scale), scale)
    return val


def random_int(length=2):
    val = random_float(length, 0)
    return val

def random_data(data_type='string',length=8,scale=0, filed_name='', picklistValues=[], isLoop = True):
    data_type = data_type.lower()
    strLoop = " + string.valueof(i) "
    intLoop = ' + i '
    if not isLoop:
        strLoop = intLoop = ''

    if data_type == 'string' or data_type == 'textarea' or data_type == 'url':
        val = "'" + random_str(length-1) + "'" + strLoop
    elif data_type == 'phone':
        val = "'" + random_phone(10) + "'" + strLoop
    elif data_type == 'email':
        val = "'" + random_str(length) + "@" + random_str(length) + ".com' " + strLoop
    elif data_type == 'int':
        val = xstr(random_int(length - 1)) + intLoop
    elif data_type == 'currency':
        val = xstr(random_int(length - 1)) + intLoop
    elif data_type == 'double':
        val = xstr(random_float(length, scale)) + intLoop
    elif data_type == 'percent':
        val = xstr(random.randint(0, 90)) + intLoop
    elif data_type == 'boolean' or data_type == 'combobox':
        val = random.choice(['True', 'False'])
    elif data_type == 'datetime':
        val = 'DateTime.now()'
    elif data_type == 'date':
        val = 'Date.today()'
    elif data_type == 'ID':
        val = ''
    elif data_type == 'picklist':
        val = "'" + random.choice(picklistValues) + "'"
    elif data_type == 'multipicklist':
        val = "'" + random.choice(picklistValues) + "'"
    elif data_type == 'reference':
        val = get_obj_name(filed_name) + 'List[i].id'
    else:
        val = 'null'
    return val


def get_obj_name(sobj_name):
    str = sobj_name.replace('__c','').lower()
    return str
    # str = sobj_name.replace('__c','')
    # return cap_low(str)


def cap_low(str):
    strlen = len(str)
    if strlen == 0:
        return str.lower()
    return str[0].lower() + str[1:strlen]

def cap_upper(str):
    strlen = len(str)
    if strlen == 0:
        return str.upper()
    return str[0].upper() + str[1:strlen]

def xstr(s):
    if s is None:
        return ''
    else:
        return str(s)


def xformat(str, data_type='string'):

    if data_type == 'id' or data_type == 'string' or data_type == 'textarea' or data_type == 'url' or data_type == 'phone' or data_type == 'email' or data_type == 'ID' or data_type == 'picklist' or data_type == 'multipicklist' or data_type == 'reference':
        if str is None:
            val = ''
        else:
            val = "'" + str.replace('\r\n','\\n').replace('\n','\\n').replace('\r','\\n') + "'"

    elif data_type == 'int' or data_type == 'currency' or data_type == 'double' or data_type == 'percent' or data_type == 'boolean' or data_type == 'combobox':
        val = str
    elif data_type == 'datetime':
        # '2016-12-16T00:00:00.000+0000' formate
        try:
            tmpstr = str[0:19].split("T")
            a = tmpstr[0].split("-")
            b = tmpstr[1].split(":")
            val = "Datetime.newInstance(%s, %s, %s, %s, %s, %s)" % (a[0],a[1],a[2],b[0],b[1],b[2])
        except Exception:
            val = "DateTime.now()"

    elif data_type == 'date':
        try:
            a = str.split("-")
            val = "Date.newInstance(%s, %s, %s)" % (a[0],a[1],a[2])
        except Exception:
            val = "DateTime.now()"
        
    else:
        # val = 'null'
        val = str

    return val

def save_session(session_str):
    print('session_str--->')
    print(session_str)
    settings = setting.load()
    full_path = os.path.join(get_default_floder(), 'config', '.session')
    print('save .session path------->')
    print(full_path)
    content = json.dumps(session_str, indent=4)
    save_file(full_path, content)

def jsonstr(json_str):
    try:
        ret = json_str.json()
    except Exception:
        ret = json_str.text

    return ret

def get_default_floder(iscreate=False):
    settings = setting.load()
    # fullpath = os.path.join(settings["workspace"], settings["default_project"], settings["xyfloder"])
    fullpath = os.path.join(settings["default_project_value"]["workspace"], settings["xyfloder"])
    # fix windows slash 
    fullpath = os.path.normpath(fullpath)
    
    if iscreate:
        makedir(fullpath)
    return fullpath

def makedir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

def get_plugin_path():
    from os.path import dirname, realpath
    return dirname(realpath(__file__))

def del_comment(soql):
    result = soql
    if soql:
        # TODO
        # soql = soql.strip().replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ')
        soql = soql.strip().replace('\t', ' ')
        
        # delete // comment
        result1, number = re.subn("//.*", "", soql)
        # delete /**/ comment
        result, number = re.subn("/\*([\s|\S]*?)\*/", "", result1, flags=re.M)
        result = result.strip()
    # show_in_panel(result)

    return result


# get sobject name from soql
def get_soql_sobject(soql_str):
    soql = del_comment(soql_str)
    # match = re.match("select\s+\*\s+from[\s\t]+(\w+)([\t\s\S]*)", soql, re.I|re.M)
    match = re.match("select\\s+([\\w\\n,.:_\\s]*|\*)\\s+from[\s\t]+(\w+)([\t\s\S]*)", soql, re.I|re.M)
    sobject = ""
    if match:
        sobject = match.group(2)
        # print('------>' + match.group(0))
        # print('------>' + match.group(1))
        # print('------>' + match.group(2))
        # print('------>' + match.group(3))
    return sobject


# get soql fields from soql,return list
def get_soql_fields(soql):
    match = re.match("SELECT\\s+[\\w\\n,.:_\\s]*\\s+FROM", soql.strip(), re.IGNORECASE)
    show_in_panel(match)
    if match:
        fieldstr = match.group(0)[6:-4].replace(" ", "").replace("\n", "")
        return fieldstr.split(",")
    else:
        return ''

def get_simple_soql_str(sobject, fields, no_address=False,condition=''):
    soql = 'SELECT '
    fields_lst = []
    for field in fields:
        if no_address and (field["type"] == "address"):
            continue
        fields_lst.append(xstr(field["name"]))
    soql += ' , '.join(fields_lst)
    soql += ' FROM ' + sobject
    soql += condition
    return soql


def get_soql_src(sobject, fields, condition='', has_comment=False, is_custom_only=False, updateable_only=False):
    soql_scr = ""
    if has_comment:
        fields_str = "\n"
        tmp_fields = []
        tmp_fields.append('')
        for field in fields:
            field_name = xstr(field["name"])
            if is_custom_only and not field["custom"]:
                if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                    continue

            if updateable_only and not field["updateable"]:
                continue

            tmp_fields_str = "\t\t\t" + xstr(field["name"]) + ",\t\t\t\t//" + xstr(field["label"])
            tmp_fields.append(tmp_fields_str)

        if len(tmp_fields) > 0:
            tmp_fields[-1] = tmp_fields[-1].replace(',', '')
        fields_str = '\n'.join(tmp_fields)
    else:
        tmp_fields = []
        for field in fields:
            field_name = xstr(field["name"])
            if is_custom_only and not field["custom"]:
                if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                    continue
            tmp_fields.append(xstr(field["name"]))
        fields_str = ','.join(tmp_fields)

    soql_scr = ("select %s\nfrom %s\n%s" % (fields_str, sobject, condition))

    return soql_scr


def get_soql_result(soql_str, soql_result):
    message = 'totalSize: ' + xstr(soql_result['totalSize']) + "\n\n"
    if soql_result['totalSize'] == 0:
        message += 'no record!!'
        return message

    headers = get_soql_fields(soql_str)

    if not headers :
        return xstr(soql_result)


    rows = ",".join(['"%s"' % h for h in headers]) + "\n"

    for record in soql_result['records']:
        row = []
        for header in headers:
            row_value = record

            # relation soql query
            for _header in header.split("."):
                field_case_mapping = {}
                for k in row_value:
                    field_case_mapping[k.lower()] = k

                row_value = row_value[field_case_mapping[_header.lower()]]
                if not isinstance(row_value, dict):
                    break

            value = xstr(row_value)
            value = value.replace('"', '""')
            row.append('"%s"' % value)
        rows += ",".join(row) + "\n"

    message += xstr(rows)
    return message

def get_query_object_name(soql_result):
    try:
        sobj_name = soql_result['records'][0]['attributes']['type']
        return sobj_name
    except Exception as e:
        return ''

def get_soql_to_apex(sobj_fields, soql, soql_result):
    headers = get_soql_fields(soql)

           # print(field["name"])  
           # print(field["label"])  
           # print(field["type"])  
           # print(field["length"])  
           # print(field["scale"])  
           # 
    if soql_result['totalSize'] == 0:
        apex_code = '// no record'
        return apex_code

    # show_in_panel(soql_result)
    sobj_name = soql_result['records'][0]['attributes']['type']

    # show_in_panel( sobj_fields )

    table = []
    for record in soql_result['records']:
        row = []
        for header in headers:
            row_value = record
            

            # relation soql query
            for _header in header.split("."):
                field_case_mapping = {}
                for k in row_value:
                    field_case_mapping[k.lower()] = k

                row_value = row_value[field_case_mapping[_header.lower()]]
                if not isinstance(row_value, dict):
                    break

            value = xstr(row_value)
            field = {}
            field_name = header.lower()
            field["name"] = field_name
            if field_name in sobj_fields:
                fieldtype = sobj_fields[field_name]["type"]
            else:
                fieldtype = "string"

            # show_in_panel(field_name + ',' + fieldtype + '\n')
            field["value"] = xformat(value, fieldtype)
            field["label"] = sobj_fields[field_name]["label"]
            row.append(field)
        table.append(row)


    apex_code = get_sentence(sobj_name, table)
    return apex_code


def get_sentence(objectApiName, table):
    obj_name = get_obj_name(objectApiName)
    apex_sentence = ("\n\nList<{T}> {obj_name}List = new List<{T}>();\n"
                .format(T=objectApiName,
                        obj_name=obj_name))
    counter = 0
    for row in table:
        instance_name = obj_name + xstr(counter)
        counter += 1
        apex_sentence += ("{T} {instance_name} = new {T}();\n"
                    .format(T=objectApiName,
                            instance_name=instance_name))
        for field in row:
            if field['name'] == 'id' or field['value'] == '' or field['value'] == 'null' or field['value'] == '\'\'' :
                apex_sentence += ("// {instance_name}.{field} = {value};    // {label}\n"
                                     .format(instance_name=instance_name,
                                             field=field['name'],
                                             value=field['value'],
                                             label=field['label']))
            else:
                apex_sentence += ("{instance_name}.{field} = {value};   // {label}\n"
                                 .format(instance_name=instance_name,
                                         field=field['name'],
                                         value=field['value'],
                                         label=field['label']))

        apex_sentence += ("{obj_name}List.add({instance_name});\n\n"
                    .format(obj_name=obj_name,
                            instance_name=instance_name))

    apex_sentence += ("upsert {objName}List;\n\n"
                .format(objName=obj_name))

    return apex_sentence

##get_file_name_no_extension is from mavensmate util
def get_file_name_no_extension(path):
    base=os.path.basename(path)
    return os.path.splitext(base)[0]

##get_friendly_platform_key is from mavensmate util
def get_friendly_platform_key():
    friendly_platform_map = {
        'darwin': 'osx',
        'win32': 'windows',
        'linux2': 'linux',
        'linux': 'linux'
    }
    return friendly_platform_map[sys.platform]    

##parse_json_from_file is from mavensmate util
def parse_json_from_file(location):
    try:
        json_data = open(location)
        data = json.load(json_data)
        json_data.close()
        return data
    except:
        return {}

def save_file(full_path, content, encoding='utf-8'):
    if not os.path.exists(os.path.dirname(full_path)):
        print("mkdir: " + os.path.dirname(full_path))
        os.makedirs(os.path.dirname(full_path))

    # fp = open(full_path, "w")
    # print(content)
    # fp.write(content)
    # fp.close()

    try:
        fp = open(full_path, "w", encoding=encoding)
        fp.write(content)
    except Exception as e:
        show_in_dialog('save file error!\n' + full_path)
        print(e)
    finally:
        fp.close()




##########################################################################################
#browser Util
##########################################################################################
def open_in_browser(url, browser_name = '', browser_path = ''):
    if not browser_path or not os.path.exists(browser_path) or browser_name == "default":
        webbrowser.open_new_tab(url)

    elif browser_name == "chrome-private":
        os.system("\"%s\" --incognito %s" % (browser_path, url))

    else:
        try:
            # show_in_panel("33")
            # browser_path = "\"C:\Program Files\Google\Chrome\Application\chrome.exe\" --incognito"
            webbrowser.register('chromex', None, webbrowser.BackgroundBrowser(browser_path))
            webbrowser.get('chromex').open_new_tab(url)
        except Exception as e:
            webbrowser.open_new_tab(url)

def open_in_default_browser(url):
    browser_map = setting.get_default_browser()
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
