import os,sys
import json
import re
import random
import platform
import shutil
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from .const import sfTypeSwitcher

def debug(msg):
    print(msg)

def showlog(msg):
    print(msg)

##########################################################################################
#Python base Util
##########################################################################################
def get_plugin_path():
    from os.path import dirname, realpath
    return dirname(realpath(__file__))

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


def jsonstr(json_str):
    try:
        ret = json_str.json()
    except Exception:
        ret = json_str.text

    return ret

def makedir(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

##parse_json_from_file is from mavensmate util
def parse_json_from_file(location):
    try:
        json_data = open(location)
        data = json.load(json_data)
        json_data.close()
        return data
    except:
        return {}

##get_friendly_platform_key is from mavensmate util
def get_friendly_platform_key():
    friendly_platform_map = {
        'darwin': 'osx',
        'win32': 'windows',
        'linux2': 'linux',
        'linux': 'linux'
    }
    return friendly_platform_map[sys.platform]    


##get_file_name_no_extension is from mavensmate util
def get_file_name_no_extension(path):
    base=os.path.basename(path)
    return os.path.splitext(base)[0]


def save_file(full_path, content, encoding='utf-8'):
    if not os.path.exists(os.path.dirname(full_path)):
        showlog("mkdir: " + os.path.dirname(full_path))
        os.makedirs(os.path.dirname(full_path))
    try:
        fp = open(full_path, "w", encoding=encoding)
        fp.write(content)
    except Exception as e:
        showlog('save file error!\n' + full_path)
    finally:
        fp.close()

# 次の文字は、ファイル名の一部としては使用できません: 不等号 (< >)、アスタリスク (*)、疑問符 (?)、二重引用符 (")、縦線またはパイプ (|)、コロン (:)、スラッシュ (/)、または角かっこ ([])。
def get_excel_sheet_name(worksheet_name):
    can_not_use_list = ['<','>','*','?','"','|',':','/','[',']']
    for aTag in can_not_use_list:
        worksheet_name = worksheet_name.replace(aTag, '')
    if len(worksheet_name) > 31:
        worksheet_name = (worksheet_name)[0:31]
    return worksheet_name

def clear_comment(src):
    C_Rule = "(///*(/s|.)*?/*//)|(////.*)"
    src = re.sub(C_Rule, "", src) 
    return src


##########################################################################################
#SfdcString Util
##########################################################################################
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
    debug(match)
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

# def search_soql_to_list(soql_str, soql_result):
#     table = []
#     headers = get_soql_fields(soql_str)

#     for record in soql_result['records']:
#         row = []
#         for header in headers:
#             row_value = record

#             # relation soql query
#             for _header in header.split("."):
#                 field_case_mapping = {}
#                 for k in row_value:
#                     field_case_mapping[k.lower()] = k

#                 row_value = row_value[field_case_mapping[_header.lower()]]
#                 if not isinstance(row_value, dict):
#                     break

#             value = xstr(row_value)
#             row.append(value)
#         table.append(row)
#     return table


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

    sobj_name = soql_result['records'][0]['attributes']['type']

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



class SysIo():
    def get_file_list(self, path):
        file_list = []
        for (root, dirs, files) in os.walk(path):
            for file in files:
                # パスセパレータは\\より/の方が好きなので置換
                file_list.append( os.path.join(root,file))
            
        return file_list

    # print file path
    def print_files_path(self, dir, is_full_path):
        file_list = []
        for (root, sub_dirs, files) in os.walk(dir):
            for file in files:
                # パスセパレータは\\より/の方が好きなので置換
                if is_full_path:
                    full_path = os.path.join(root,file).replace("\\", "/")
                    file_list.append( full_path )
                    debug( full_path )
                else:
                    debug( file )


    # mk an sub sfdc project
    def mk_sub_project(self, root, sub_project_name):
        os.mkdir(os.path.join(root,sub_project_name))
        os.mkdir(os.path.join(root,sub_project_name, 'src'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'aura'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'classes'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'objects'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'pages'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'triggers'))
        os.mkdir(os.path.join(root,sub_project_name, 'src', 'components'))

    # copy lightning component
    def copy_lightning(self, lightning_src_path, new_lightning_basename):
        root = os.path.dirname(lightning_src_path)
        lightning_src_basename = os.path.basename(lightning_src_path)
        new_lightning_path = os.path.join(root, new_lightning_basename)
        os.mkdir(new_lightning_path)
        for file in os.listdir(lightning_src_path):
            srcFile = os.path.join(lightning_src_path, file)
            new_file = file.replace(lightning_src_basename, new_lightning_basename)
            targetFile = os.path.join(new_lightning_path, new_file)
            shutil.copyfile(srcFile, targetFile)

    def _get_specil_metadata_type(self, metadata_folder):
        folder_to_metadata_type_dict = {
            "aura" : "AuraDefinitionBundle",
            "reports" : "Report",
            "dashboards" : "Dashboard",
            "documents" : "Document",
            "email" : "EmailTemplate",
        }
        return folder_to_metadata_type_dict[metadata_folder]

    def get_file_attr(self, full_file_path):
        try:
            attr = {}
            # dir_path = os.path.dirname(full_file_path)
            # dir_name = os.path.basename(dir_path)
            file_path, file_name = os.path.split(full_file_path)
            name, file_extension = os.path.splitext(file_name)
            attr["file_path"] = file_path
            attr["file_name"] = file_name
            attr["dir"] = os.path.basename(file_path)
            attr["p_dir"] = os.path.basename(os.path.dirname(file_path))
            attr["name"] = name
            attr["extension"] = file_extension.replace('.','')
            attr["metadata_type"] = ''
            attr["metadata_folder"] = ''
            attr["metadata_sub_folder"] = ''
            attr["is_sfdc_file"] = True

            if attr["p_dir"] in ["aura", "reports", "dashboards", "documents", "email"]:
                attr["metadata_sub_folder"] = attr["dir"]
                attr["metadata_folder"] = attr["p_dir"]
                attr["metadata_type"] = self._get_specil_metadata_type(attr["p_dir"])
            elif attr["dir"] in ["aura", "reports", "dashboards", "documents", "email"]:
                attr["metadata_sub_folder"] = ""
                attr["metadata_folder"] = attr["dir"]
                attr["metadata_type"] = self._get_specil_metadata_type(attr["p_dir"])
            elif attr["extension"] in sfTypeSwitcher:
                attr["metadata_type"] = sfTypeSwitcher[attr["extension"]]
                if attr["p_dir"] in ["reports", "dashboards", "documents", "email"]:
                    attr["metadata_sub_folder"] = attr["dir"]
                    attr["metadata_folder"] = attr["p_dir"]
                else:
                    attr["metadata_folder"] = attr["dir"]
            else:
                attr["is_sfdc_file"] = False

            if attr["metadata_sub_folder"]:
                attr["file_key"] = "%s/%s/%s" % (attr["metadata_folder"], attr["metadata_sub_folder"], attr["file_name"])
            else:
                attr["file_key"] = "%s/%s" % (attr["metadata_folder"], attr["file_name"])
            return attr
        except Exception as e:
            return None

    def save_file(self, full_path, content, encoding='utf-8'):
        if not os.path.exists(os.path.dirname(full_path)):
            showlog("mkdir: " + os.path.dirname(full_path))
            os.makedirs(os.path.dirname(full_path))
        try:
            fp = open(full_path, "w", encoding=encoding)
            fp.write(content)
        except Exception as e:
            showlog('save file error!\n' + full_path)
        finally:
            fp.close()


class SfdcXml():
    def __init__(self, api_version="40.0"):
        self.api_version = api_version

    def namespace(self, element):
        m = re.match('\{.*\}', element.tag)
        return m.group(0) if m else ''

    # sf fileName to sf type
    def getType(self, fileName):
        fileNamesplit = fileName.split(".")
        filetype = str(fileNamesplit[-1])
        filetype = filetype.replace("\n","")
        return sfTypeSwitcher.get(filetype,"")
        
    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, encoding='UTF-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    ######################################################################
    #<?xml version="1.0" encoding="UTF-8"?>
    #<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    #    <types>
    #        <members>MyCustomObject__c.MyCustomField__c</members>
    #        <name>CustomField</name>
    #    </types>
    #    <types>
    #        <members>Account.SLA__c</members>
    #        <members>Account.Phone</members>
    #        <name>CustomField</name>
    #    </types>
    #    <version>37.0</version>
    #</Package>
    ######################################################################
    def build_customfiled_xml(self, lines):
        top = Element('Package', {"xmlns": "http://soap.sforce.com/2006/04/metadata"})
        types = SubElement(top, 'types')

        for line in lines:
            content  = line
            if not content:
                continue
            members = SubElement(types, 'members')
            members.text = content
        
        name = SubElement(types, 'name')
        name.text = 'CustomField'

        version = SubElement(top, 'version')
        version.text = self.api_version

        return self.prettify(top)

    def build_package_xml(self, files, api_version="40.0"):
        packageFileContent = "<?xml version='1.0' encoding='UTF-8'?><Package xmlns='http://soap.sforce.com/2006/04/metadata'>"
        for line in files:
            sfTypeName = self.getType(line)
            #print(sfTypeName)
            if (sfTypeName != ""):
                entity = (((line.split("/"))[-1]).split("."))[0]
                debug(entity)
                if (packageFileContent.find(sfTypeName + "<") == -1):
                    packageFileContent = packageFileContent + "<types><members>" + entity + "</members><name>" + sfTypeName + "</name></types>"
                else:
                    location = packageFileContent.find("<name>" + sfTypeName + "</name></types>")
                    packageFileContent = packageFileContent[:location] + "<members>" + entity + "</members>" + packageFileContent[location:]
        packageFileContent = packageFileContent + "<version>" + api_version + "</version></Package>"
        return packageFileContent

    def get_fields_list_CSV(self, root):
        header_row=['fullName','label','externalId','type', 'formula','formulaTreatBlanksAs', 'unique', 'required', 'referenceTo', 'relationshipName','relationshipLabel']
        writer = []
        for e in root.iter('{http://soap.sforce.com/2006/04/metadata}fields'):
            field_row = {}
            for m in e:
                val = {m.tag[41:]:m.text}
                field_row.update(val)
            writer.append(field_row)
        return writer

    def get_fields_from_object_xml(self, contents):
        field_list = []
        contents = contents.replace('xmlns="http://soap.sforce.com/2006/04/metadata"', '')
        elem = ElementTree.fromstring(contents)
        for aField in elem.findall('fields'):

            myField = {
                'fullName' : aField.find('fullName').text if aField.find('fullName') is not None else '',
                'label' : aField.find('label').text if aField.find('label') is not None else '',
                'type' : aField.find('type').text if aField.find('type') is not None else '',
                'formula' : aField.find('formula').text if aField.find('formula') is not None else ''
            }

            field_list.append(myField)
        return field_list

    def object_xml_to_fieldPermissions(self, object_name, contents):
        field_list = self.get_fields_from_object_xml(contents)

        top = Element('Profile', {"xmlns": "http://soap.sforce.com/2006/04/metadata"})
        
        for aField in field_list:
            if not aField['fullName'] or not aField['label'] :
                continue

            types = SubElement(top, 'fieldPermissions')
            editable = SubElement(types, 'editable')
            if aField['formula']:
                editable.text = 'false'
            else:
                editable.text = 'true'
            field = SubElement(types, 'field')
            field.text = object_name + '.' + aField['fullName']
            readable = SubElement(types, 'readable')
            readable.text = 'true'

        return self.prettify(top)
