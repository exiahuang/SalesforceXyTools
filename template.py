# Apex Test Class Template
def template_test_class():
    return '''/**
* @author {author}
*/
@isTest
private class {class_name}Test {{
{class_body}
}}
'''

# Apex Test Method Template
def template_test_method():
    return '''
    /**
     * This is a test method for {function_name}
     */
    static testMethod void test_{function_name}() {{

        // PageReference pageRef = Page.{page_name};
        // Test.setCurrentPage(pageRef);
        // pageRef.getParameters().put('param1', 'param1');

        Test.startTest();

{function_body}

        Test.stopTest();

        // Check
        // System.assert(ApexPages.hasMessages());
        // for(ApexPages.Message msg : ApexPages.getMessages()) {{
        //     System.assertEquals('Upload file is NULL', msg.getSummary());
        //     System.assertEquals(ApexPages.Severity.ERROR, msg.getSeverity());
        // }}
    }}

'''


# Apex Class Template
def template_class():
    return '''/**
* @author {author}
*/
public class {class_name}{class_type} {{
        public {class_name}{class_type}() {{
{constructor_body}
        }}
{class_body}
}}
'''


# Apex Class Without Constructor Template
def template_no_con_class():
    return '''/**
* @author {author}
*/
public class {class_name}{class_type} {{
{class_body}
}}
'''

# Apex Class Template
def template_class_with_sharing():
    return '''/**
* @author {author}
*/
public with sharing class {class_name}{class_type} {{
        public {class_name}{class_type}() {{
{constructor_body}
        }}
{class_body}
}}
'''


# constructor method
def template_constructor_fun():
    return '''
        public {class_name}({args}) {{
{constructor_body}
        }}
'''



# VisualForce table td Template
def template_html_table_content():
    return '''
    <tr>
        <th class="mythclass">
            <apex:outputPanel rendered="" >
                <span class="mod-icon-note">必須</span>
            </apex:outputPanel>
            <apex:outputText value="{th_body}" />
        </th>
        <td>
            {td_body}
        </td>
    </tr>
'''


# VisualForce table td Template
def template_html_table_content_with_validate():
    return '''
    <tr>
        <th class="mythclass">
            <apex:outputPanel rendered="" >
                <span class="mod-icon-note">必須</span>
            </apex:outputPanel>
            <apex:outputText value="{th_body}" />
        </th>
        <td>
            {td_body}
            <apex:outputPanel layout="block" rendered="{{!!ISBlank({td_body2})}}">
                <apex:outputText style="color:red;" value="{{!{td_body2}}}"/>
            </apex:outputPanel>
        </td>
    </tr>
'''

def template_list_vf_table_body():
    return '''
                            <tbody>
                                <tr>
{th_header}
                                </tr>
                                <apex:repeat value="{{!{list_dto_instance}}}" var="{dto_instance}" >
                                    <tr>
{table_body}
                                    </tr>
                                </apex:repeat>

                            </tbody>
'''

# VisualForce Template
def template_vf_inputform():
    return '''<apex:page showHeader="false" standardStylesheets="false" applyHtmlTag="false" applyBodyTag="false" sidebar="false" showChat="false" cache="false" docType="html-5.0" controller="{controller}">
    <html>
        <head>
            <meta charset="utf-8" />
            <meta name="format-detection" content="telephone=no" />
            <meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <title>{title}</title>
        </head>
        <style>
            .ul-search {{
                list-style-type: none;
            }}
            .li_search {{
                display: table;
                width: 100%;
                margin-bottom: 20px;
                
            }}
            .li_title {{
                width: 120px
            }}
            .li_title,
            .li_content {{
                display: table-cell;
                vertical-align: middle
            }}
            table.type1 {{
                border-collapse: separate;
                border-spacing: 1px;
                text-align: center;
                line-height: 1.5;
            }}
            table.type1 th {{
                width: 155px;
                padding: 10px;
                font-weight: bold;
                vertical-align: top;
                color: #fff;
                background: #036;
            }}
            table.type1 td {{
                width: 155px;
                padding: 10px;
                vertical-align: top;
                border-bottom: 1px solid #ccc;
                background: #eee;
            }}
        </style>
        <body>
            <apex:form id="mainform">

                <!-- START OF Edit Mode -->
                <apex:outputText rendered="{{!isEditMode}}">
                    {search_vf}
                    <div class="frame-wrapper">
                        <table class="type1">
                            {edit_table_body}
                        </table>
                    </div>
                    <div class="btn">
                        <apex:commandButton value="Return" action="{{!doBack}}" onclick=""/>
                        <apex:commandButton value="Next" action="{{!doNext}}" onclick=""/>
                    </div>
                </apex:outputText>
                <!-- END OF Edit Mode -->

                <!-- START OF View Mode -->
                <apex:outputText rendered="{{!isViewMode}}">
                    {search_vf}
                    <div class="frame-wrapper">
                        <table class="type1">
                            {view_table_body}
                        </table>
                    </div>
                    <div class="btn">
                        <apex:commandButton value="Return" action="{{!doBack}}" onclick=""/>
                        <apex:commandButton value="Next" action="{{!doNext}}" onclick=""/>
                        <apex:commandButton value="Save" action="{{!doSave}}" onclick=""/>
                    </div>
                </apex:outputText>
                <!-- END OF View Mode -->

                <!-- START OF Message Mode -->
                <apex:outputText rendered="{{!isMessageMode}}">
                    <div class="frame-wrapper">
                        Message Mode
                    </div>
                    <div class="btn">
                        <apex:commandButton value="Return" action="{{!doBack}}" onclick=""/>
                        <apex:commandButton value="Next" action="{{!doNext}}" onclick=""/>
                    </div>
                </apex:outputText>
                <!-- END OF Message Mode -->
            </apex:form>
        </body>
    </html>
</apex:page>
'''

# VisualForce Template
def template_vf_search():
    return '''
                    <div class="search">
                        <ul class="ul-search">
                            {search_vf_item}
                            <li class="li-search">
                                <div class="li_title">KeyWord</div>
                                <div class="li_content"><apex:input type="text" value="{{!keywords}}" /></div>
                            </li>
                            <li class="li-search">
                                <div class="li_title"></div>
                                <div class="li_content"><apex:commandButton value="Search" action="{{!search}}" onclick=""/></div>
                            </li>
                        </ul>                  
                    </div>
'''


# VisualForce Template
def template_search_snippet(data_type):
        vf_code = ""
        if data_type == 'picklist':
            vf_code = '''
                            <li class="li-search">
                                <div class="li_title">{field_label}</div>
                                <div class="li_content">
                                    <apex:selectList size="1" value="{{!{field_name}}}" >
                                            <apex:selectOptions value="{{!{field_name}List}}" />
                                    </apex:selectList>
                                </div>
                            </li>
'''
        return vf_code


def template_sfdcxycontroller():
    return '''/**
* @author {author}
*/
public virtual class SfdcXyController {{
        //　Return URL
        public String retUrl {{get;set;}}
        //　Return Current Url
        public String currentUrl {{get;set;}}

        //　Page Mode
        public Integer modeIndex {{get;set;}}
        public static final Integer MODE_EDIT = 0;
        public static final Integer MODE_VIEW = 1;
        public static final Integer MODE_MESSAGE = 2;

        public Boolean isEditMode {{
            get{{
                return (modeIndex == MODE_EDIT);
            }}
        }}
        
        public Boolean isViewMode {{
            get{{
                return (modeIndex == MODE_VIEW);
            }}
        }}

        public Boolean isMessageMode {{
            get{{
                return (modeIndex == MODE_MESSAGE);
            }}
        }}

        public SfdcXyController() {{
            this.modeIndex = MODE_EDIT;
            this.retUrl = ApexPages.currentPage().getParameters().get('retUrl');
            this.currentUrl = ApexPages.currentPage().getURL();
            this.retUrl = String.isBlank(this.retUrl) ? this.currentUrl : this.retUrl;
        }}

        /**
         * Go Next
         */
        public virtual PageReference doNext() {{
            Boolean result = doCheck();
            setNextMode(result);

            return null;
        }}

        /**
         * Go Back
         */
        public virtual PageReference doBack() {{
            Boolean result = true; 
            setBackMode(result);
            return null;
        }}

        /**
         * Go Cancel
         */
        public virtual PageReference doCancel() {{
            if (String.isBlank(retUrl)) {{
                retUrl = '/';
            }}

            PageReference nextPage = new PageReference(retUrl);
            nextPage.setRedirect(true);
            return nextPage;
        }}

        /**
         * do Check
         */
        public virtual Boolean doCheck() {{
            Boolean result = true;

            return result;
        }}

        /**
         * set next mode
         */
        public virtual void setNextMode(Boolean flg) {{
            if(!flg) return;
            if(modeIndex == MODE_EDIT) modeIndex = MODE_VIEW;
            else if(modeIndex == MODE_VIEW) modeIndex = MODE_MESSAGE;
            else if(modeIndex == MODE_MESSAGE) modeIndex = MODE_MESSAGE;
        }}

        /**
         * set back mode
         */
        public virtual void setBackMode(Boolean flg) {{
            if(!flg) return;
            if(modeIndex == MODE_EDIT) modeIndex = MODE_EDIT;
            else if(modeIndex == MODE_VIEW) modeIndex = MODE_EDIT;
            else if(modeIndex == MODE_MESSAGE) modeIndex = MODE_VIEW;
        }}
}}
'''

def template_controller_class():
    return '''/**
* @author {author}
*/
public with sharing class {controller} extends SfdcXyController {{

        // DTO Bean
        public {dto} {dto_instance} {{get;set;}}

        public {controller}() {{
            search();
        }}

        private void search(){{
            String id = ApexPages.currentPage().getParameters().get('id');
            if(String.isBlank(id)){{
                this.{dto_instance} = new {dto}();
            }}else{{
                this.{dto_instance} = new {dto}({dao}.get{sobj_api}ById(id));
            }}
        }}

        /**
         * upsert Dto
         */
        public PageReference doSave() {{
            Boolean result;

            Savepoint sp = Database.setSavepoint();
            try {{
                upsert {dto_instance}.getSobject();
                result = true;
            }} catch(DMLException e) {{
                Database.rollback(sp);
                System.debug('saveDto DMLException:' + e.getMessage());
                result = false;
            }} catch(Exception e) {{
                Database.rollback(sp);
                System.debug('saveDto Exception:' + e.getMessage());
                result = false;
            }}
            return null;
        }}

        /**
         * Go Next
         */
        public override PageReference doNext() {{
            Boolean result = doCheck();
            setNextMode(result);
            return null;
        }}

        /**
         * Go Back
         */
        public override PageReference doBack() {{
            Boolean result = true; 
            setBackMode(result);
            return null;
        }}

        /**
         * do Check
         */
        public override Boolean doCheck() {{
            Boolean result = true;

            return result;
        }}
}}
'''

def template_list_controller_class():
    return '''/**
* @author {author}
*/
public with sharing class {list_controller} extends SfdcXyController {{

        // DTO Bean
        public {list_dto} {list_dto_instance} {{get;set;}}
        // Search DTO Bean
        public {dto} searchDto {{get;set;}}
        // Search keywords
        public String keywords {{get;set;}}

        public {list_controller}() {{
            this.searchDto = new {dto}();
            search();
        }}

        public void search(){{
            this.{list_dto_instance} = new {list_dto}();
            for( {sobject__c} {sobj_api_low_cap} : {dao}.get{sobj_api}List(keywords,searchDto)){{
                this.{list_dto_instance}.add(new {dto}({sobj_api_low_cap}));
            }}
        }}

        /**
         * upsert Dto
         */
        public PageReference doSave() {{
            Boolean result;

            Savepoint sp = Database.setSavepoint();
            try {{

                List<{sobject__c}> {sobj_api_low_cap}List = new List<{sobject__c}>();
                for({dto} dto : this.{list_dto_instance}){{
                    {sobj_api_low_cap}List.add(dto.getSobject());
                }}
                update {sobj_api_low_cap}List;

                result = true;
            }} catch(DMLException e) {{
                Database.rollback(sp);
                System.debug('saveDto DMLException:' + e.getMessage());
                result = false;
            }} catch(Exception e) {{
                Database.rollback(sp);
                System.debug('saveDto Exception:' + e.getMessage());
                result = false;
            }}
            return null;
        }}

        /**
         * Go Next
         */
        public override PageReference doNext() {{
            Boolean result = doCheck();
            setNextMode(result);

            return null;
        }}

        /**
         * Go Back
         */
        public override PageReference doBack() {{
            Boolean result = true; 
            setBackMode(result);
            return null;
        }}

        /**
         * do Check
         */
        public override Boolean doCheck() {{
            Boolean result = true;

            return result;
        }}
}}
'''

def template_dao_class():
    return '''/**
* @author {author}
*/
public with sharing class {dao} {{
    /**
     * get soql query string
     */
    public static String getQueryField(){{
        String query_str = '';
{soql_src}
        return query_str;
    }}

    /**
    * get all {sobject__c}
    * @return list of {sobject__c} 
    */
    public static List<{sobject__c}> getAll{sobj_api}List(){{
        String query_str = getQueryField();
        query_str += ' limit 10000';
        List<{sobject__c}> {sobj_api_low_cap}List = Database.query(query_str);

        return {sobj_api_low_cap}List;
    }}

    /**
    * get {sobject__c} by Set<id>
    * @return list of {sobject__c} 
    */
    public static List<{sobject__c}> get{sobj_api}List(Set<String> ids){{
        String query_str = getQueryField();
        query_str += ' WHERE id IN:ids ';
        List<{sobject__c}> {sobj_api_low_cap}List = Database.query(query_str);

        return {sobj_api_low_cap}List;
    }}

    /**
    * get {sobject__c} by id
    * @return one of {sobject__c} 
    */
    public static {sobject__c} get{sobj_api}ById(String id){{
        String query_str = getQueryField();
        query_str += ' WHERE id =: id  ';
        query_str += ' limit 1  ';
        List<{sobject__c}> {sobj_api_low_cap}List = Database.query(query_str);

        if({sobj_api_low_cap}List.isEmpty())
            return null;
        else
            return {sobj_api_low_cap}List.get(0);
    }}

    /**
    * get {sobject__c} by keywords
    * @return list of {sobject__c} 
    */
    public static List<{sobject__c}> get{sobj_api}List(String keywords,{dto} searchDto){{

        String soql = getQueryField();
        String query_str = '';
        List<String> query_list = new List<String>();

        if(String.isNotBlank(keywords)){{
            String[] keywordsArr = keywords.replace('　',' ').split(' ');
            List<String> keywordsFilters = new List<String>();
            for(String f: keywordsArr){{
                if(String.isBlank(f)) continue;
                f = f.replace('%', '\\\\%').replace('_','\\\\_');
                keywordsFilters.add('%' + f + '%');
            }}

{keywords_conditions}
            query_list.add(query_str);
        }}

{searchDto_conditions}

        if(query_list.size() > 0){{
            soql += ' WHERE  ';
            soql += String.join(query_list, ' and ');
        }}
        soql += ' limit 10000';
        List<{sobject__c}> {sobj_api_low_cap}List = Database.query(soql);

        return {sobj_api_low_cap}List;
    }}
}}
'''


# def template_dao_class():
#     return '''/**
# * @author {author}
# */
# public with sharing class {dao} {{
#     /**
#     * get all {sobject__c}
#     * @return list of {sobject__c} 
#     */
#     public static List<{sobject__c}> getAll{sobj_api}List(){{
#         List<{sobject__c}> {sobj_api_low_cap}List = [
#             {soql_src}
#             limit 10000
#         ];

#         return {sobj_api_low_cap}List;
#     }}

#     /**
#     * get {sobject__c} by Set<id>
#     * @return list of {sobject__c} 
#     */
#     public static List<{sobject__c}> get{sobj_api}List(Set<String> ids){{
#         List<{sobject__c}> {sobj_api_low_cap}List = [
#             {soql_src}
#             WHERE id IN:ids
#         ];

#         return {sobj_api_low_cap}List;
#     }}

#     /**
#     * get {sobject__c} by id
#     * @return one of {sobject__c} 
#     */
#     public static {sobject__c} get{sobj_api}ById(String id){{
#         List<{sobject__c}> {sobj_api_low_cap}List = [
#             {soql_src}
#             WHERE id =: id 
#             limit 1
#         ];

#         if({sobj_api_low_cap}List.isEmpty())
#             return null;
#         else
#             return {sobj_api_low_cap}List.get(0);
#     }}

#     /**
#     * get {sobject__c} by keywords
#     * @return list of {sobject__c} 
#     */
#     public static List<{sobject__c}> get{sobj_api}List(String keywords){{
#         if(String.isBlank(keywords)) return getAll{sobj_api}List();
    
#         String[] keywordsArr = keywords.replace('　',' ').split(' ');
#         List<String> keywordsFilters = new List<String>();
#         for(String f: keywordsArr){{
#             if(String.isBlank(f)) continue;
#             f = f.replace('%', '\\\\%').replace('_','\\\\_');
#             keywordsFilters.add('%' + f + '%');
#         }}

#         List<{sobject__c}> {sobj_api_low_cap}List = [
#             {soql_src}
#             WHERE 
#                 {keywords_conditions}
#         ];

#         return {sobj_api_low_cap}List;
#     }}
# }}
# '''



def template_dto_class():
    return '''/**
* @author {author}
*/
public class {dto} {{

{class_body}

    public {dto}() {{
        init();
    }}

    public {dto}({sobject__c} sobj) {{
        init();
        if(sobj != null){{
{constructor_body}
        }}
    }}

    /**
     * init method
     */
    public void init(){{
{init_body}
    }}

    /**
    * Change the dto to sobject
    * get sobject {sobject__c} from dto
    * @return {sobject__c} 
    */
    public {sobject__c} getSobject(){{
        {sobject__c} sobj = new {sobject__c}();
{getSobject_body}
        return sobj;
    }}
}}
'''


def get_vf_edit_snippet(data_type):
    vf_code = ""
    if data_type == 'id' or data_type == 'ID' or data_type == 'reference':
        vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
    elif data_type == 'string':
        vf_code = '''<apex:input type="text" value="{{!{field_name}}}" />'''
    elif data_type == 'url' :
        vf_code = '''<apex:input type="text" value="{{!{field_name}}}" />'''
    elif data_type == 'email':
        vf_code = '''<apex:input type="email" value="{{!{field_name}}}" />'''
    elif data_type == 'phone':
        vf_code = '''<apex:input type="text" value="{{!{field_name}}}" />'''
    elif data_type == 'textarea':
        vf_code = '''<apex:inputTextarea value="{{!{field_name}}}" />'''
    elif data_type == 'picklist':
        vf_code = '''<apex:selectList size="1" value="{{!{field_name}}}" >
                            <apex:selectOptions value="{{!{field_name}List}}" />
                    </apex:selectList>'''
    elif data_type == 'multipicklist':
        vf_code = '''<apex:selectList size="10" value="{{!{field_name}}}" multiselect="true">
                         <apex:selectOptions value="{{!{field_name}List}}" />
                        </apex:selectList>'''
    elif data_type == 'int' or data_type == 'percent' or data_type == 'long' or data_type == 'currency' or data_type == 'double':
        vf_code = '''<apex:input type="number" value="{{!{field_name}}}" />'''
    elif data_type == 'boolean' or data_type == 'combobox':
        vf_code = '''<apex:inputCheckbox value="{{!{field_name}}}" />'''
    elif data_type == 'datetime' :
        vf_code = '''<apex:input type="datetime-local" value="{{!{field_name}}}" />'''
    elif data_type == 'date' :
        vf_code = '''<apex:input type="date" value="{{!{field_name}}}" />'''

    return vf_code



def get_vf_show_snippet(data_type):
    if data_type == 'id' \
        or data_type == 'ID'  \
        or data_type == 'reference' \
        or data_type == 'string' \
        or data_type == 'url' \
        or data_type == 'email' \
        or data_type == 'phone' \
        or data_type == 'picklist' \
        or data_type == 'int' or data_type == 'percent' \
        or data_type == 'long' or data_type == 'currency' or data_type == 'double' \
        or data_type == 'boolean' or data_type == 'combobox':
            vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''

    elif data_type == 'textarea':
        # white-space: pre; 
        vf_code = '''<div style="white-space: pre-wrap; word-break: break-all; ">
                        <apex:outputText value="{{!{field_name}}}" />
                    </div>'''
    elif data_type == 'multipicklist':
        vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
        # vf_code = '''<apex:selectList size="10" value="{{!{field_name}}}" multiselect="true">
        #                  <apex:selectOptions value="{{!{field_name}List}}" />
        #                 </apex:selectList>'''
    elif data_type == 'datetime' :
        vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
        # vf_code = '''<apex:input type="datetime-local" value="{{!{field_name}}}" />'''
    elif data_type == 'date' :
        vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
        # vf_code = '''<apex:input type="date" value="{{!{field_name}}}" />'''
    else :
        vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
    return vf_code
