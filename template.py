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
        <th class="has-w-20-pc">
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
                <div class="frame-wrapper">
                    <table class="mod-base-table">
                        {table_body}
                    </table>
                </div>
                <!-- // frame-wrapper -->
            </apex:form>
        </body>
    </html>
</apex:page>
'''
