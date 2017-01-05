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
public with sharing class {class_name}{class_type} {{
         public {class_name}{class_type}() {{

         }}
{class_body}
}}
'''


# Apex Class Without Constructor Template
def template_no_con_class():
    return '''/**
* @author {author}
*/
public with sharing class {class_name}{class_type} {{
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