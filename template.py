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


# Apex Dao Method Template
def template_apex_dao_method():
    return '''
    /**
    * get {sobject} by Set<id>
    * @return list of {sobject} 
    */
    public static List<{sobject}> get{instance_name}List(Set<id> ids){{
        List<{sobject}> {instance_name_cap_low}List = [
            {soql_src}
            WHERE id IN:ids
            and deleted__c = false
        ];

        return {instance_name_cap_low}List;
    }}
'''


# Apex Dao Method Template
def template_apex_dao_method_getbyid():
    return '''
    /**
    * get {sobject} by id
    * @return one of {sobject} 
    */
    public static {sobject} get{instance_name}ById(Id id){{
        List<{sobject}> {instance_name_cap_low}List = [
            {soql_src}
            WHERE id =: id 
            and deleted__c = false
            limit 1
        ];

        if({instance_name_cap_low}List.isEmpty())
            return null;
        else
            return {instance_name_cap_low}List.get(0);
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
        <body>
            <apex:form id="mainform">

                <!-- START OF Edit Mode -->
                <apex:outputText rendered="{{!isEditMode}}">
                    <div class="frame-wrapper">
                        <table class="mod-base-table">
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
                    <div class="frame-wrapper">
                        <table class="mod-base-table">
                            {view_table_body}
                        </table>
                    </div>
                    <div class="btn">
                        <apex:commandButton value="Return" action="{{!doBack}}" onclick=""/>
                        <apex:commandButton value="Next" action="{{!doNext}}" onclick=""/>
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

def template_controller_constructor_body():
    return '''
            this.{dto_instance} = new {dto}();
            this.modeIndex = MODE_EDIT;
            this.retUrl = ApexPages.currentPage().getParameters().get('retUrl');
            this.currentUrl = ApexPages.currentPage().getURL();
            this.retUrl = String.isBlank(this.retUrl) ? this.currentUrl : this.retUrl;
'''

def template_controller_base_method():
    return '''
        //　Return URL
        public String retUrl {get;set;}
        //　Return Current Url
        public String currentUrl {get;set;}

        //　Page Mode
        public Integer modeIndex {get;set;}
        public static final Integer MODE_EDIT = 0;
        public static final Integer MODE_VIEW = 1;
        public static final Integer MODE_MESSAGE = 2;

        public Boolean isEditMode {
            get{
                return (modeIndex == MODE_EDIT);
            }
        }
        
        public Boolean isViewMode {
            get{
                return (modeIndex == MODE_VIEW);
            }
        }

        public Boolean isMessageMode {
            get{
                return (modeIndex == MODE_MESSAGE);
            }
        }

        /**
         * Go Next
         */
        public PageReference doNext() {
            Boolean result = doCheck();
            if(result){
                System.debug('-->doCheck ok');
                setNextMode();

            }else{
                System.debug('-->doCheck error');
            }

            return null;
        }

        /**
         * Go Back
         */
        public PageReference doBack() {
            setBackMode();
            return null;
        }

        /**
         * Go Cancel
         */
        public PageReference doCancel() {
            if (String.isBlank(retUrl)) {
                retUrl = '/';
            }

            PageReference nextPage = new PageReference(retUrl);
            nextPage.setRedirect(true);
            return nextPage;
        }

        /**
         * do Check
         */
        private Boolean doCheck() {
            Boolean result = true;

            return result;
        }

        /**
         * set next mode
         */
        private void setNextMode() {
            if(modeIndex == MODE_EDIT) modeIndex = MODE_VIEW;
            else if(modeIndex == MODE_VIEW) modeIndex = MODE_MESSAGE;
            else if(modeIndex == MODE_MESSAGE) modeIndex = MODE_MESSAGE;
        }

        /**
         * set back mode
         */
        private void setBackMode() {
            if(modeIndex == MODE_EDIT) modeIndex = MODE_EDIT;
            else if(modeIndex == MODE_VIEW) modeIndex = MODE_EDIT;
            else if(modeIndex == MODE_MESSAGE) modeIndex = MODE_VIEW;
        }
        
'''


def get_vf_edit_snippet(data_type):
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
        or data_type == 'textarea' \
        or data_type == 'picklist' \
        or data_type == 'int' or data_type == 'percent' \
        or data_type == 'long' or data_type == 'currency' or data_type == 'double' \
        or data_type == 'boolean' or data_type == 'combobox':
            vf_code = '''<apex:outputText value="{{!{field_name}}}" />'''
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

    return vf_code
