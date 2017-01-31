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
TMP_LIST_CONTROLLER_CLASS = 'template_list_controller_class'
TMP_SFDCXYCONTROLLER = 'template_sfdcxycontroller'
# Visualforce page input form template
TMP_VF_INPUTFORM = 'template_vf_inputform'
TMP_VF_SEARCH = 'template_vf_search'
TMP_LIST_VF_TABLE_BODY = 'template_list_vf_table_body'
TMP_CONTROLLER_BASE_METHOD = 'template_controller_base_method'

CS_INSTANCE = 'INSTANCE'
CS_CALL_FUN = 'CALL_FUN'
CS_CALL_VOID_FUN = 'CALL_VOID_FUN'
CS_COMMENT = 'CS_COMMENT'
CS_DECLARE = 'CS_DECLARE'

NO_NEED_FIELDS = {'ownerid','isdeleted','createddate','createdbyid','lastmodifieddate','lastmodifiedbyid','systemmodstamp','lastactivitydate','lastvieweddate','lastreferenceddate'}


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
    sfdc_name_map['sobject__c'] = sobject_name
    sfdc_name_map['sobject'] = get_api_name(sobject_name)
    sfdc_name_map['sobj_api'] = util.cap_upper(get_api_name(sobject_name))
    sfdc_name_map['sobj_api_low_cap'] = util.cap_low(sfdc_name_map['sobj_api'])

    sfdc_name_map['controller'] = sfdc_name_map['sobj_api'] + 'Controller'
    sfdc_name_map['dto'] = sfdc_name_map['sobj_api'] + 'Dto'
    sfdc_name_map['dao'] = sfdc_name_map['sobj_api'] + 'Dao'
    sfdc_name_map['vf'] = sfdc_name_map['sobj_api']

    sfdc_name_map['list_controller'] = sfdc_name_map['sobj_api'] + 'ListController'
    sfdc_name_map['list_dto'] = 'List<' + sfdc_name_map['dto'] + '>'
    sfdc_name_map['list_vf'] = sfdc_name_map['sobj_api'] + 'List'

    sfdc_name_map['dto_instance'] = util.cap_low(sfdc_name_map['dto'])
    sfdc_name_map['dao_instance'] = util.cap_low(sfdc_name_map['dao'])
    sfdc_name_map['controller_instance'] = util.cap_low(sfdc_name_map['controller'])


    sfdc_name_map['list_dto_instance'] = sfdc_name_map['dto_instance'] + 'List'
    # sfdc_name_map['list_dao_instance'] = util.cap_low(sfdc_name_map['dao'])
    # sfdc_name_map['list_controller_instance'] = util.cap_low(sfdc_name_map['controller'])
    
    sfdc_name_map['dto_file'] = sfdc_name_map['dto'] + '.cls'
    sfdc_name_map['dao_file'] = sfdc_name_map['dao'] + '.cls'
    sfdc_name_map['vf_file'] = sfdc_name_map['vf'] + '.page'
    sfdc_name_map['controller_file'] = sfdc_name_map['controller'] + '.cls'
    sfdc_name_map['list_vf_file'] = sfdc_name_map['list_vf'] + '.page'
    sfdc_name_map['list_controller_file'] = sfdc_name_map['list_controller'] + '.cls'


    sfdc_name_map['test_class'] = sfdc_name_map['sobj_api'] + 'Test'
    sfdc_name_map['test_class_file'] = sfdc_name_map['test_class'] + '.cls'

    return sfdc_name_map


def get_testclass(src_str):
    src_str = util.del_comment(src_str)

    className = get_class_name(src_str)
    sfdc_name_map = get_sfdc_namespace(className)

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
                tmpValue['return_name'] = 'result' + util.cap_upper(function_name)
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
                tmpValue['return_name'] = 'result' + util.cap_upper(function_name)
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

    return re_test_code,sfdc_name_map


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

        if is_custom_only and field_name.lower() in NO_NEED_FIELDS:
            # print('---->no need field : '+ field_name.lower())
            continue

        # if is_custom_only and not field["custom"]:
        #     if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
        #         continue

        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        # comment
        comment = util.xstr(field['label']) + ' , ' + util.xstr(field['type'])
        class_body += get_code_snippet(CS_COMMENT, comment)
        # define
        class_body += get_code_snippet(CS_DECLARE, tmpVal)
        
        # constructor function
        constructor_body += ('\t\t\tthis.%s = sobj.%s;\n' % (field_name, util.xstr(field['name'])))
        
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

        # 'reference'
        if util.xstr(field['type']) == 'reference':
            tmpVal = {}
            ref_sbj = field['referenceTo'][0]
            ref_sbj_namespace = get_sfdc_namespace(ref_sbj)
            ref_sbj_namespace['dto_relationship_name'] = field['relationshipName']
            tmpVal['declare_type'] = ref_sbj_namespace['dto']
            tmpVal['declare_name'] = ref_sbj_namespace['dto_instance']
            # comment
            comment = 'reference to sobject : ' + ref_sbj
            class_body += get_code_snippet(CS_COMMENT, comment)
            # define
            class_body += get_code_snippet(CS_DECLARE, tmpVal)

            # init DTO at init()
            init_body += "\n";
            init_body += ("\t\tthis.{dto_instance} = new {dto}();\n").format(**ref_sbj_namespace);
            
            # constructor 'reference'
            constructor_body += ('\t\t\tthis.{dto_instance} = new {dto}(sobj.{dto_relationship_name});\n').format(**ref_sbj_namespace);


        # if picklist or multipicklist
        # add List<SelectOption>
        # add define init
        if util.xstr(field['type']) == 'picklist' or util.xstr(field['type']) == 'multipicklist':
            # print(field)
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

            # init List<SelectOption>class_body at init()
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



    sfdc_name_map['class_body'] = class_body
    sfdc_name_map['getSobject_body'] = dto_to_sobj_body
    sfdc_name_map['constructor_body'] = constructor_body
    sfdc_name_map['init_body'] = init_body
    src_code = get_template(TMP_DTO_CLASS).format(**sfdc_name_map)
    return src_code, class_name

def get_controller_class(class_name):
    sobj_name = class_name

    sfdc_name_map = get_sfdc_namespace(class_name)
    class_name = sfdc_name_map['sobject']

    cls_source = get_template(TMP_CONTROLLER_CLASS).format(**sfdc_name_map)

    return cls_source, class_name


def get_list_controller_class(class_name):
    sobj_name = class_name

    sfdc_name_map = get_sfdc_namespace(class_name)
    class_name = sfdc_name_map['sobject']

    cls_source = get_template(TMP_LIST_CONTROLLER_CLASS).format(**sfdc_name_map)

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


        if field_name.lower() == 'id' or field['autoNumber']:
            continue

        if is_custom_only and not field["custom"]:
            if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                continue


        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        #start of view table boday
        data_type = util.xstr(field['type'])
        vf_edit_snippet = template.get_vf_show_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        view_td_body = vf_edit_snippet.format(field_name=field_name_with_dto)

        if include_validate:
            view_table_body += get_template(TMP_HTML_TABLE_CONTENT2).format(th_body=util.xstr(field['label']),
                                                                        td_body=view_td_body,
                                                                        td_body2= field_name_with_dto + 'Msg'
                                                                        )
        else:
            view_table_body += get_template(TMP_HTML_TABLE_CONTENT).format(th_body=util.xstr(field['label']),
                                                                        td_body=view_td_body)
        #end of view table boday
       
        #start of edit table boday
        data_type = util.xstr(field['type'])
        vf_edit_snippet = template.get_vf_edit_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        edit_td_body = vf_edit_snippet.format(field_name=field_name_with_dto)

        if include_validate:
            edit_table_body += get_template(TMP_HTML_TABLE_CONTENT2).format(th_body=util.xstr(field['label']),
                                                                        td_body=edit_td_body,
                                                                        td_body2= field_name_with_dto + 'Msg'
                                                                        )

        else:
            edit_table_body += get_template(TMP_HTML_TABLE_CONTENT).format(th_body=util.xstr(field['label']),
                                                                        td_body=edit_td_body)
        #end of edit table boday


    vf_param = {}
    vf_param['title'] = sfdc_name_map['vf'] + ' Input Form'
    vf_param['controller'] = sfdc_name_map['controller']
    vf_param['edit_table_body'] = edit_table_body
    vf_param['view_table_body'] = view_table_body
    vf_param['search_vf'] = ''

    source_code = get_template(TMP_VF_INPUTFORM).format(**vf_param)
    return source_code, class_name

def get_list_vf_class(class_name, fields, is_custom_only=False, include_validate=False):

    sobj_name = class_name
    view_th_header = ''
    edit_th_header = ''
    edit_td = ''
    view_td = ''

    constructor_body = ''

    sfdc_name_map = get_sfdc_namespace(class_name)

    class_name = sfdc_name_map['sobj_api']

    # name, label, type, length, scale
    for field in fields:
        field_name = util.cap_low( get_api_name(util.xstr(field['name'])) )
        field_type = sobj_to_apextype(util.xstr(field['type']))
        
        tmpVal = {}
        tmpVal['declare_type'] = field_type
        tmpVal['declare_name'] = field_name

        if field_name.lower() == 'id':
            continue

        if is_custom_only and not field["custom"]:
            if not (field_name.lower() == 'id' or field_name.lower() == 'name') :
                continue

        data_type = util.xstr(field['type'])
        vf_show_snippet = template.get_vf_show_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        view_td_body = vf_show_snippet.format(field_name=field_name_with_dto)
        view_th_header += ('''\t\t\t\t\t<th>%s</th>\n''' % (util.xstr(field['label'])))
        view_td += ('''\t\t\t\t\t<td>%s</td>\n''' % (view_td_body))
        

        vf_edit_snippet = template.get_vf_edit_snippet(data_type)
        field_name_with_dto = sfdc_name_map['dto_instance']  + "." + field_name
        edit_td_body = vf_edit_snippet.format(field_name=field_name_with_dto)
        edit_th_header += ('''\t\t\t\t\t<th>%s</th>\n''' % (util.xstr(field['label'])))
        edit_td += ('''\t\t\t\t\t<td>%s</td>\n''' % (edit_td_body))

    vf_param = {}
    vf_param['title'] = sfdc_name_map['list_vf'] + ' Input Form'
    vf_param['controller'] = sfdc_name_map['list_controller']
    vf_param['edit_table_body'] = get_template(TMP_LIST_VF_TABLE_BODY).format(th_header=edit_th_header,table_body=edit_td,**sfdc_name_map)
    vf_param['view_table_body'] = get_template(TMP_LIST_VF_TABLE_BODY).format(th_header=view_th_header,table_body=view_td,**sfdc_name_map)
    vf_param['search_vf'] = get_template(TMP_VF_SEARCH)

    source_code = get_template(TMP_VF_INPUTFORM).format(**vf_param)
    return source_code, class_name

def get_dao_class(class_name, fields, sf_login_instance, is_custom_only=False):
    class_body = ''
    soql_src = get_soql_src(class_name, fields, sf_login_instance, 
                            condition='', has_comment=True , is_custom_only=is_custom_only, 
                            include_relationship=True,
                            is_apex_code=True)

    sfdc_name_map = get_sfdc_namespace(class_name)
    sfdc_name_map['soql_src'] = soql_src

    # search by keyword condition
    conditions = []
    tmp_index = 0
    for field in fields:
        if (field['type'] == 'textarea'):
            continue
        if field['custom'] or field['name'].lower() == 'name':
            # conditions.append((' %s like :keywordsFilters\n' % (field['name'])))

            if tmp_index == 0:
                tmp_soql = (' ( %s like :keywordsFilters' % (field['name']))
            else:
                tmp_soql = (' or %s like :keywordsFilters' % (field['name']))
            tmp_index += 1

            tmp_apex_soql = ("\t\tquery_str += ' %s ';" % tmp_soql)
            conditions.append(tmp_apex_soql)

    # sfdc_name_map['keywords_conditions'] = '\t\t\tor'.join(conditions)
    sfdc_name_map['keywords_conditions'] = '\n'.join(conditions)
    sfdc_name_map['keywords_conditions'] += "\n\t\tquery_str += ' ) ';\n"

    src_code = get_template(TMP_DAO_CLASS).format(**sfdc_name_map)

    return src_code

def get_sfdcxycontroller():
    sfdc_name_map = get_sfdc_namespace('')

    src_code = get_template(TMP_SFDCXYCONTROLLER).format(**sfdc_name_map)

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


##########################################################################################
#SOQL String Util
##########################################################################################
def get_soql_src(sobject, fields, sf_login_instance, condition='', has_comment=False, 
                is_custom_only=False, updateable_only=False, include_relationship=False
                ,is_apex_code=False):
    soql_scr = ""
    fields_str = "\n"
    tmp_fields = []
    tmp_fields.append('')

    nocomment_tmp_fields = []
    nocomment_fields_str = ""

    for field in fields:
        field_name = util.xstr(field["name"])

        if is_custom_only and field_name.lower() in NO_NEED_FIELDS:
            continue

        if updateable_only and not field["updateable"]:
            continue

        if is_apex_code:
            tmp_fields_str = ("\t\t\tquery_str += ' %s, ';\t\t\t\t// %s" % (util.xstr(field["name"]), util.xstr(field["label"] )))
        else:
            tmp_fields_str = "\t\t\t" + util.xstr(field["name"]) + ",\t\t\t\t//" + util.xstr(field["label"])
        tmp_fields.append(tmp_fields_str)

        nocomment_tmp_fields.append(util.xstr(field["name"]))

        if include_relationship and util.xstr(field['type']) == 'reference':
            ref_sbj = field['referenceTo'][0]
            ref_sbj_namespace = get_sfdc_namespace(ref_sbj)
            ref_sbj_namespace['dto_relationship_name'] = field['relationshipName']
            ref_sftype = sf_login_instance.get_sobject(ref_sbj)
            ref_sftypedesc = ref_sftype.describe()
            for ref_field in ref_sftypedesc["fields"]:
                if is_custom_only and util.xstr(ref_field["name"]).lower() in NO_NEED_FIELDS:
                    continue
                if updateable_only and not field["updateable"]:
                    continue
                loop_tmp_field = {}
                loop_tmp_field['dto_relationship_name']  = field['relationshipName']
                loop_tmp_field['field_name']  = util.xstr(ref_field["name"])
                loop_tmp_field['label']  = util.xstr(ref_field["label"])
                loop_tmp_field['sobj']  = ref_sbj

                # if updateable_only and not field["updateable"]:
                #     continue
                if is_apex_code:
                   tmp_fields_str = ("\t\t\tquery_str += ' {dto_relationship_name}.{field_name}, ';\t\t\t\t// {label}").format(**loop_tmp_field)
                else:    
                    tmp_fields_str = ("\t\t\t{dto_relationship_name}.{field_name},\t\t\t\t// {label}").format(**loop_tmp_field)

                tmp_fields.append(tmp_fields_str)

                nocomment_tmp_fields_str = ("{dto_relationship_name}.{field_name}").format(**loop_tmp_field)
                nocomment_tmp_fields.append(nocomment_tmp_fields_str)

    if len(tmp_fields) > 0:
        tmp_fields[-1] = tmp_fields[-1].replace(',', '')
    fields_str = '\n'.join(tmp_fields)

    nocomment_fields_str = ','.join(nocomment_tmp_fields)

    if is_apex_code:
        apex_soql = "\t\tquery_str += ' SELECT ';\n"
        apex_soql += fields_str
        apex_soql += ("\n\t\tquery_str += ' FROM %s ';\n" % sobject)
        if condition:
            apex_soql += ("\t\tquery_str += ' %s ';\n" % condition)
        return apex_soql

    if has_comment:
        soql_scr = ("select %s\nfrom %s\n%s" % (fields_str, sobject, condition))
    else:
        soql_scr = ("select %s\nfrom %s\n%s" % (nocomment_fields_str, sobject, condition))

    return soql_scr
