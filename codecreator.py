import re

from . import util
from . import template

##########################################################################################
#Salesforce Template
##########################################################################################
AUTHOR = 'huangxy'
TMP_CLASS = 'template_class'
TMP_CLASS_WITH_SHARING = 'template_class_with_sharing'
TMP_HTML_TABLE_CONTENT = 'template_html_table_content'
TMP_HTML_TABLE_CONTENT2 = 'template_html_table_content_with_validate'
TMP_NO_CON_CLASS = 'template_no_con_class'
TMP_TEST_METHOD = 'template_test_method'
TMP_TEST_CLASS = 'template_test_class'
TMP_DAO_CLASS = 'template_dao_class'
TMP_DTO_CLASS = 'template_dto_class'
TMP_CONTROLLER_CLASS = 'template_controller_class'
# Visualforce page input form template
TMP_VF_INPUTFORM = 'template_vf_inputform'
TMP_CONTROLLER_BASE_METHOD = 'template_controller_base_method'

CS_INSTANCE = 'INSTANCE'
CS_CALL_FUN = 'CALL_FUN'
CS_CALL_VOID_FUN = 'CALL_VOID_FUN'
CS_COMMENT = 'CS_COMMENT'
CS_DECLARE = 'CS_DECLARE'



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

        f['is_static'] = ( util.xstr(m[0]).find("static") > -1 )
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


def get_api_name(api_name):
    return api_name.replace('__c','')

def get_sfdc_namespace(sobject_name):
    sfdc_name_map = {}
    sfdc_name_map['author'] = AUTHOR
    sfdc_name_map['sobject'] = sobject_name
    sfdc_name_map['sobj_api'] = get_api_name(sobject_name).capitalize()
    sfdc_name_map['sobj_api_low_cap'] = util.cap_low(sfdc_name_map['sobj_api'])

    sfdc_name_map['controller'] = sfdc_name_map['sobj_api'] + 'Controller'
    sfdc_name_map['dto'] = sfdc_name_map['sobj_api'] + 'Dto'
    sfdc_name_map['dao'] = sfdc_name_map['sobj_api'] + 'Dao'
    sfdc_name_map['vf'] = sfdc_name_map['sobj_api']

    sfdc_name_map['dto_instance'] = util.cap_low(sfdc_name_map['dto'])
    sfdc_name_map['dao_instance'] = util.cap_low(sfdc_name_map['dao'])
    sfdc_name_map['controller_instance'] = util.cap_low(sfdc_name_map['controller'])
    
    sfdc_name_map['dto_file'] = sfdc_name_map['dto'] + '.cls'
    sfdc_name_map['dao_file'] = sfdc_name_map['dao'] + '.cls'
    sfdc_name_map['vf_file'] = sfdc_name_map['vf'] + '.page'
    sfdc_name_map['controller_file'] = sfdc_name_map['controller'] + '.cls'
    return sfdc_name_map


def get_testclass(src_str):
    src_str = util.del_comment(src_str)

    className = get_class_name(src_str)
    page_name = className.replace('Controller', '')
    
    class_body = ''
    test_in_all = ''
    test_in_all_flg = True

    for item in get_functionList(src_str):
        function_name = item['function_name']
        args = item['args']

        function_body = ''
        instance_name = util.cap_low(className)
        
        argList = []
        paramsStr = ''
        for arg in args:
            if arg == '':
                continue

            argName = arg.strip().split()
            argList.append(argName[1])

            paramsStr += ("\t\t{paramStr} = {testValue};\n"
                          .format(paramStr=arg.strip(),
                                 testValue=util.random_data(data_type=decode_map_str(argName[0]), isLoop = False)))
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
            # test_in_all += ' // call static method\n'
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

            if test_in_all_flg:
                # test_in_all += ' // call constructor method\n'
                test_in_all += get_code_snippet(CS_COMMENT, " test " + function_name) 
                test_in_all += codeSnippet + "\n"
                test_in_all_flg = False

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

            # test_in_all += ' // call other apex method\n'
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


def get_dto_class(class_name, fields, is_custom_only=False, include_validate=False):

    sobj_name = class_name
    class_body = ''
    constructor_body = ''
    init_body = ''

    #dto to sobject
    dto_to_sobj_body = ''
    
    sfdc_name_map = get_sfdc_namespace(class_name)

    # name, label, type, length, scale
    for field in fields:
        field_name = util.cap_low( get_api_name(util.xstr(field['name'])) )
        field_type = sobj_to_apextype(util.xstr(field['type']))

        if is_custom_only and not field["custom"]:
            if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                continue

        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        # comment
        comment = util.xstr(field['label']) + ' , ' + util.xstr(field['type'])
        class_body += get_code_snippet(CS_COMMENT, comment)
        # define
        class_body += get_code_snippet(CS_DECLARE, tmpVal)

        # include validate string
        if include_validate:
            tmpVal = {}
            tmpVal['declare_type'] = 'transient String'
            tmpVal['declare_name'] = field_name + 'Msg'
            # comment
            comment = 'Validate string For ' + util.xstr(field['label']) 
            class_body += get_code_snippet(CS_COMMENT, comment)
            # define
            class_body += get_code_snippet(CS_DECLARE, tmpVal)

        # picklist
        if util.xstr(field['type']) == 'picklist':
            print(field)
            tmpVal = {}
            tmpVal['declare_type'] = 'List<SelectOption>'
            tmpVal['declare_name'] = field_name + 'List'
            # comment
            comment = 'picklist SelectOption For ' + util.xstr(field['label']) 
            class_body += get_code_snippet(CS_COMMENT, comment)
            # define
            class_body += get_code_snippet(CS_DECLARE, tmpVal)

            # TODO
            # init_body += ('\t\t\tthis.%s = CommonUtil.getSelectOptionList(%s.%s.getDescribe(),true);\n' % (tmpVal['declare_name'],sobj_name,util.xstr(field['name'])) )
            picklistValues = field['picklistValues']

            init_body += "\n";
            init_body += ("\t\tthis.%s = new List<SelectOption>();\n" % (tmpVal['declare_name']));
            init_body += ("\t\tthis.%s.add(new SelectOption('', '--None--'));\n" % (tmpVal['declare_name']));
            for pick in picklistValues:
                label = pick['label']
                value = pick['value']
                init_body += ("\t\tthis.%s.add(new SelectOption('%s', '%s'));\n" % (tmpVal['declare_name'], value,label));

        # Dto To Sobject
        if field["updateable"] or field_name.lower() == 'id':
            dto_to_sobj_body += ('\t\tsobj.%s = %s;\n' % (util.xstr(field['name']),field_name))
        constructor_body += ('\t\t%s = sobj.%s;\n' % (field_name, util.xstr(field['name'])))

    sfdc_name_map['class_body'] = class_body
    sfdc_name_map['getSobject_body'] = dto_to_sobj_body
    sfdc_name_map['constructor_body'] = constructor_body
    sfdc_name_map['init_body'] = init_body
    src_code = get_template(TMP_DTO_CLASS).format(**sfdc_name_map)
    return src_code, class_name

def get_controller_class(class_name):
    sobj_name = class_name
    class_name = get_api_name(class_name)

    sfdc_name_map = get_sfdc_namespace(class_name)

    cls_source = get_template(TMP_CONTROLLER_CLASS).format(**sfdc_name_map)

    return cls_source, class_name


def get_vf_class(class_name, fields, is_custom_only=False, include_validate=False):

    sobj_name = class_name
    edit_table_body = ''
    view_table_body = ''
    constructor_body = ''

    sfdc_name_map = get_sfdc_namespace(class_name)

    class_name = sfdc_name_map['sobj_api']

    # name, label, type, length, scale
    for field in fields:
        field_name = util.cap_low( get_api_name(util.xstr(field['name'])) )
        field_type = sobj_to_apextype(util.xstr(field['type']))

        if field_name.lower() == 'id':
            continue

        if is_custom_only and not field["custom"]:
            if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                continue

        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        print('---> ' )
        print('--->field_type ' + field_type)
        print('--->field_name ' + field_name)

        data_type = util.xstr(field['type'])
        vf_edit_snippet = template.get_vf_edit_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        edit_td_body = vf_edit_snippet.format(field_name=field_name_with_dto)

        data_type = util.xstr(field['type'])
        vf_edit_snippet = template.get_vf_show_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        view_td_body = vf_edit_snippet.format(field_name=field_name_with_dto)

        if include_validate:
            edit_table_body += get_template(TMP_HTML_TABLE_CONTENT2).format(th_body=util.xstr(field['label']),
                                                                        td_body=edit_td_body,
                                                                        td_body2= field_name_with_dto + 'Msg'
                                                                        )
            view_table_body += get_template(TMP_HTML_TABLE_CONTENT2).format(th_body=util.xstr(field['label']),
                                                                        td_body=view_td_body,
                                                                        td_body2= field_name_with_dto + 'Msg'
                                                                        )
        else:
            edit_table_body += get_template(TMP_HTML_TABLE_CONTENT).format(th_body=util.xstr(field['label']),
                                                                        td_body=edit_td_body)
            view_table_body += get_template(TMP_HTML_TABLE_CONTENT).format(th_body=util.xstr(field['label']),
                                                                        td_body=view_td_body)



    title = sfdc_name_map['vf'] + ' Input Form'
    source_code = get_template(TMP_VF_INPUTFORM).format(controller=sfdc_name_map['controller'], 
                                                        title=title,
                                                        edit_table_body=edit_table_body,
                                                        view_table_body=view_table_body)
    return source_code, class_name

def get_dao_class(class_name, fields, is_custom_only=False):
    class_body = ''
    soql_src = util.get_soql_src(class_name, fields, condition='', has_comment=True , is_custom_only=is_custom_only)

    sfdc_name_map = get_sfdc_namespace(class_name)
    sfdc_name_map['soql_src'] = soql_src

    src_code = get_template(TMP_DAO_CLASS).format(**sfdc_name_map)

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



def get_code_snippet(type, value):
    codeSnippet = ''
    # apex code snippet
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