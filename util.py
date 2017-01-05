import sublime
import sublime_plugin
import datetime
import os,sys,xdrlib
import json
import re
import webbrowser
import random
import platform

from .salesforce import *
from . import setting
from . import template

##########################################################################################
#Salesforce Util
##########################################################################################
def sf_login(project_name='', Soap_Type=Soap):
    try:
        settings = setting.load()

        if project_name:
            projects = settings["projects"]
            project = projects[project_name]

            if "api_version" in project:
                api_version = project["api_version"]
            else:
                api_version = settings["default_api_version"]
                
            sf = Soap_Type(username=project["username"], 
                        password=project["password"], 
                        security_token=project["security_token"], 
                        sandbox=project["is_sandbox"],
                        version=api_version,
                        settings=settings
                        )

        elif settings["use_mavensmate_setting"]:
            sf = Soap_Type(username=settings["username"],
                            session_id=settings["sessionId"] ,
                            instance_url=settings["instanceUrl"],
                            sandbox=settings["is_sandbox"],
                            version=settings["api_version"],
                            client_id=settings["id"],
                            settings=settings
                            # password=None,
                            # security_token=None,
                            # instance=None,
                            # organizationId=None,
                            # proxies=None,
                            # session=None,
                            # settings=None
                            )
        else:
            sf = Soap_Type(username=settings["username"], 
                        password=settings["password"], 
                        security_token=settings["security_token"], 
                        sandbox=settings["is_sandbox"],
                        version=settings["api_version"],
                        settings=settings
                        )

        sf.settings = settings
        # print(sf)
        # print(sf.session_id)
        # print('------->')
        return sf
    except Exception as e:
        # print(e)
        show_in_dialog('Login Error! ' + xstr(e))
        return


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


def get_api_name(api_name):
    return api_name.replace('__c','')

def cap_low(str):
    strlen = len(str)
    if strlen == 0:
        return str.lower()
    return str[0].lower() + str[1:strlen]

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


def jsonstr(json_str):
    try:
        ret = json_str.json()
    except Exception:
        ret = json_str.text

    return ret

def get_default_floder(iscreate=False):
    settings = setting.load()
    fullpath = os.path.join(settings["workspace"], settings["default_project"], settings["xyfloder"])
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
        soql = soql.strip().replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ')
        result1, number = re.subn("//.*", "", soql)
        result, number = re.subn("/\*([\s|\S]*?)\*/", "", result1, flags=re.M)
        result = result.strip()
    # show_in_panel(result)

    return result


def get_soql_sobject(soql_str):
    soql = del_comment(soql_str)
    # match = re.match(""select\s+\*\s+from[\s\t]+\w+"", soql.strip(), re.IGNORECASE)
    # TODO
    match = re.match("select\s+\*\s+from[\s\t]+(\w+)([\t\s\S]*)", soql, re.I|re.M)
    sobject = ""
    if match:
        sobject = match.group(1)
    return sobject


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
        counter = 0
        for field in fields:
            counter += 1
            
            field_name = xstr(field["name"])
            if is_custom_only and not field["custom"]:
                if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                    continue

            if counter == len(fields):
                fields_str += "\t\t\t" + xstr(field["name"]) + "\t\t\t\t//" + xstr(field["label"])
            else:
                fields_str += "\t\t\t" + xstr(field["name"]) + ",\t\t\t\t//" + xstr(field["label"]) + "\n"
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

def save_file(full_path, content):
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path))

    # fp = open(full_path, "w")
    # print(content)
    # fp.write(content)
    # fp.close()

    try:
        fp = open(full_path, "w")
        fp.write(content)
    except Exception as e:
        show_in_dialog('save file error!\n' + full_path)
        print(e)
    finally:
        fp.close()


##########################################################################################
#Apex String Util
##########################################################################################
def get_functionList(src_str):
    
    en_src_str = encode_map_str(src_str)

    # pattern = r'(public[^(){}]*)\(([^)]*)\)[^{]'
    pattern = r'(public[^(){};]*)\(([^)]*)\)\s*{'
    match = re.findall(pattern, en_src_str, re.I|re.M)


    functionList = []
    for m in match: 
        f={}
        f['function_name'] = m[0].split()[-1]
        f['return_type'] = decode_map_str(m[0].split()[-2])
        f['is_void'] = ( f['return_type'] == 'void' )
        
        # args' format is like map<id###obj>,
        # it will need to decode 
        f['args'] = decode_map_str(m[1].strip().split(','))

        f['is_static'] = ( xstr(m[0]).find("static") > -1 )
        # show_in_panel(f)
        functionList.append(f)
        # functionName = m[0].split()[-1]
        # functionArgs = m[1].strip().split(',')
        # functionList[functionName] = functionArgs
    return functionList

# replace map<id, obj> to map<id###obj>
def encode_map_str(str):
    result = str

    # replace map<id, obj>mapName to map<id, obj> mapName
    # insert a space
    pattern = r'>[\S]'
    match = re.findall(pattern, str, re.I|re.M)
    for m in match: 
        tmp_map_str = m.replace('>', '> ')
        result = result.replace(m, tmp_map_str)

    # replace map<id, obj> to map<id###obj>
    pattern = r'map<[^>]*>'
    match = re.findall(pattern, str, re.I|re.M)
    for m in match: 
        tmp_map_str = m.replace(',', '##').replace(' ', '')
        result = result.replace(m, tmp_map_str)

    return result

# replace map<id###obj> to map<id, obj>
def decode_map_str(map_str):
    if isinstance(map_str, str):
        result = map_str.replace('##', ',')
        return result
    elif isinstance(map_str, list):
        result = []
        for s in map_str:
            result.append(s.replace('##', ','))
        return result
    else:
        return str


def get_class_name(src_str):
    pattern = r'public[\s|\w]*class([^{]*){'
    match = re.search(pattern, src_str, re.I|re.M)
    className = ''
    if match:
        # show_in_panel(match.group(1))
        className = match.group(1).split()[0]
        # show_in_panel(className)
    return className


def get_testclass(src_str):
    src_str = del_comment(src_str)

    className = get_class_name(src_str)
    page_name = className.replace('Controller', '')
    
    class_body = ''
    test_in_all = ''
    test_in_all_flg = True

    for item in get_functionList(src_str):
        function_name = item['function_name']
        args = item['args']

        function_body = ''
        instance_name = cap_low(className)
        
        argList = []
        paramsStr = ''
        for arg in args:
            if arg == '':
                continue

            argName = arg.strip().split()
            argList.append(argName[1])

            paramsStr += ("\t\t{paramStr} = {testValue};\n"
                          .format(paramStr=arg.strip(),
                                 testValue=random_data(data_type=decode_map_str(argName[0]), isLoop = False)))
        argsStr = ','.join(argList)

        # define Test Paramters
        function_body += paramsStr
        test_in_all += paramsStr

        # call static method
        if item['is_static']:
            if item['is_void']:
                tmpValue = {}
                tmpValue['instance_name'] = className
                tmpValue['function_name'] = function_name
                tmpValue['args'] = argsStr
                codeSnippet = get_code_snippet(CS_CALL_VOID_FUN, tmpValue) 
                # codeSnippet = ("\t\t{class_name}.{function_name}({args});\n"
                #               .format(class_name=className,
                #                      function_name=function_name,
                #                      args=argsStr))
            else:
                tmpValue = {}
                tmpValue['return_type'] = item['return_type']
                tmpValue['return_name'] = 'result' + function_name.capitalize()
                tmpValue['instance_name'] = className
                tmpValue['function_name'] = function_name
                tmpValue['args'] = argsStr
                codeSnippet = get_code_snippet(CS_CALL_FUN, tmpValue) 

                # codeSnippet = ("\t\t{return_type} result = {class_name}.{function_name}({args});\n"
                #               .format(return_type=item['return_type'],
                #                      class_name=className,
                #                      function_name=function_name,
                #                      args=argsStr))
            function_body += codeSnippet
            test_in_all += get_code_snippet(CS_COMMENT, " test " + function_name) 
            test_in_all += codeSnippet + "\n"

        # call constructor method
        elif className == function_name:
            tmpValue = {}
            tmpValue["class_name"] = className
            tmpValue["instance_name"] = instance_name
            tmpValue["args"] = argsStr
            codeSnippet = get_code_snippet(CS_INSTANCE, tmpValue)
            # codeSnippet = ("\t\t{class_name} {instance_name} = new {class_name}({args});\n"
            #                   .format(instance_name=instance_name,
            #                      class_name=className,
            #                      args=argsStr))
            function_body += codeSnippet
            test_in_all += get_code_snippet(CS_COMMENT, " test " + function_name) 
            test_in_all += codeSnippet + "\n"

        # call other apex method
        else:
            tmpValue = {}
            tmpValue["class_name"] = className
            tmpValue["instance_name"] = instance_name
            tmpValue["args"] = ''
            codeSnippet = get_code_snippet(CS_INSTANCE, tmpValue)
            # codeSnippet = ("\t\t{class_name} {instance_name} = new {class_name}();\n"
            #                   .format(instance_name=instance_name,
            #                      class_name=className))
            
            # new Instance for call apex method
            # test_in_all is not need
            function_body += codeSnippet
            if test_in_all_flg:
                test_in_all += codeSnippet + "\n"
                test_in_all_flg = False

            if item['is_void']:
                tmpValue = {}
                tmpValue['instance_name'] = instance_name
                tmpValue['function_name'] = function_name
                tmpValue['args'] = argsStr
                codeSnippet = get_code_snippet(CS_CALL_VOID_FUN, tmpValue) 
                # codeSnippet = ("\t\t{instance_name}.{function_name}({args});\n"
                #               .format(instance_name=instance_name,
                #                      function_name=function_name,
                #                      args=argsStr))
            else:
                tmpValue = {}
                tmpValue['return_type'] = item['return_type']
                tmpValue['return_name'] = 'result' + function_name.capitalize()
                tmpValue['instance_name'] = instance_name
                tmpValue['function_name'] = function_name
                tmpValue['args'] = argsStr
                codeSnippet = get_code_snippet(CS_CALL_FUN, tmpValue) 
                # codeSnippet = ("\t\t{return_type} result = {instance_name}.{function_name}({args});\n"
                #               .format(return_type=item['return_type'],
                #                     instance_name=instance_name,
                #                      function_name=function_name,
                #                      args=argsStr))
            function_body += codeSnippet
            test_in_all += get_code_snippet(CS_COMMENT, " test " + function_name) 
            test_in_all += codeSnippet + "\n"

        function_template = get_template(TMP_TEST_METHOD).format(function_name=function_name,
                                                            function_body=function_body,
                                                            page_name=page_name)
        class_body += function_template

    # create Test for all method
    class_body += get_template(TMP_TEST_METHOD).format(function_name='all',
                                                    function_body=test_in_all,
                                                    page_name=page_name)
    
    re_test_code = get_template(TMP_TEST_CLASS).format(author=AUTHOR,class_name=className,class_body=class_body)

    return re_test_code


def get_dto_class(class_name, fields, is_custom_only=False):

    class_body = ''
    # name, label, type, length, scale
    for field in fields:
        field_name = cap_low( get_api_name(xstr(field['name'])) )
        field_type = sobj_to_apextype(xstr(field['type']))

        if is_custom_only and not field["custom"]:
            if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                continue

        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        # comment
        comment = xstr(field['label']) + ' , ' + xstr(field['type'])
        class_body += get_code_snippet(CS_COMMENT, comment)
        # define
        class_body += get_code_snippet(CS_DECLARE, tmpVal)

    class_name = get_api_name(class_name)
    dto_class = get_template(TMP_CLASS).format(author=AUTHOR,class_name=class_name,class_type='Dto', class_body=class_body)
    return dto_class

def get_dao_class(class_name, fields, is_custom_only=False):
    class_body = ''
    soql_src = get_soql_src(class_name, fields, condition='', has_comment=True , is_custom_only=is_custom_only)
    class_body += get_template(TMP_DAO_METHOD).format(sobject=class_name,
                                                     instance_name=get_api_name(class_name),
                                                     instance_name_cap_low=cap_low(get_api_name(class_name)),
                                                     soql_src=soql_src)

    class_body += get_template(TMP_DAO_METHOD_GETBYID).format(sobject=class_name,
                                                     instance_name=get_api_name(class_name),
                                                     instance_name_cap_low=cap_low(get_api_name(class_name)),
                                                     soql_src=soql_src)

    src_code = get_template(TMP_NO_CON_CLASS).format(author=AUTHOR,
                                                     class_name=get_api_name(class_name),
                                                     class_type='Dao', 
                                                     class_body=class_body)
   
    return src_code




def sobj_to_apextype(data_type):
    atype = data_type

    if data_type == 'id' or data_type == 'string' or data_type == 'textarea' or data_type == 'url' or data_type == 'phone' or data_type == 'email' or data_type == 'ID' or data_type == 'picklist' or data_type == 'multipicklist' or data_type == 'reference':
        atype = 'String' 
    elif data_type == 'int' or data_type == 'percent':
        atype = 'Integer'
    elif data_type == 'long' :
        atype = 'Long'
    elif data_type == 'currency' or data_type == 'double' :
        atype = 'Decimal'
    elif data_type == 'boolean' or data_type == 'combobox':
        atype = 'Boolean'
    elif data_type == 'datetime' or data_type == 'date' :
        atype = data_type

    return atype


##########################################################################################
#Salesforce Template
##########################################################################################
AUTHOR = 'huangxy'
TMP_CLASS = 'template_class'
TMP_NO_CON_CLASS = 'template_no_con_class'
TMP_DAO_METHOD = 'template_apex_dao_method'
TMP_DAO_METHOD_GETBYID = 'template_apex_dao_method_getbyid'
TMP_TEST_METHOD = 'template_test_method'
TMP_TEST_CLASS = 'template_test_class'

CS_INSTANCE = 'INSTANCE'
CS_CALL_FUN = 'CALL_FUN'
CS_CALL_VOID_FUN = 'CALL_VOID_FUN'
CS_COMMENT = 'CS_COMMENT'
CS_DECLARE = 'CS_DECLARE'

def get_code_snippet(type, value):
    codeSnippet = ''
    if type == CS_INSTANCE:
        codeSnippet = ("\t\t{class_name} {instance_name} = new {class_name}({args});\n"
                          .format(instance_name=value["instance_name"],
                             class_name=value["class_name"],
                             args=value["args"]))
    elif type == CS_CALL_FUN:
        codeSnippet = ("\t\t{return_type} {return_name} = {instance_name}.{function_name}({args});\n"
                              .format(return_type=value['return_type'],
                                     return_name=value['return_name'],
                                     instance_name=value['instance_name'],
                                     function_name=value['function_name'],
                                     args=value['args']))
    elif type == CS_CALL_VOID_FUN:
        codeSnippet = ("\t\t{instance_name}.{function_name}({args});\n"
                              .format(instance_name=value['instance_name'],
                                      function_name=value['function_name'],
                                      args=value['args']))
    elif type == CS_COMMENT:
        codeSnippet = "\t\t// " + value + "\n"
    elif type == CS_DECLARE:
        # codeSnippet = ("\t\tpublic {declare_type} {declare_name} {{get;set;}}\n\n"
        codeSnippet = ("\t\tpublic {declare_type} {declare_name} {{get;set;}}\n\n"
                            .format(declare_type=value['declare_type'],
                                      declare_name=value['declare_name']))


    return codeSnippet;


def get_template(name=''):
    if not name:
        return '';
    method = getattr(template, name)
    tmp_str = method()
    return tmp_str

    # path = os.path.join(get_plugin_path(), TEM_FOLDER, name)
    # template_arr = ''
    # if os.path.isfile(path): 
    #     f = open(path)
    #     template_arr = f.readlines()
    #     f.close()
    # template = ''.join(template_arr)
    # return template


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


##########################################################################################
#END
##########################################################################################
