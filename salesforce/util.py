"""Utility functions for simple-salesforce"""

import xml.dom.minidom
from xml.sax.saxutils import quoteattr

# pylint: disable=invalid-name
def getUniqueElementValueFromXmlString(xmlString, elementName):
    """
    Extracts an element value from an XML string.

    For example, invoking
    getUniqueElementValueFromXmlString(
        '<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>', 'foo')
    should return the value 'bar'.
    """
    xmlStringAsDom = xml.dom.minidom.parseString(xmlString)
    elementsByName = xmlStringAsDom.getElementsByTagName(elementName)
    elementValue = None
    if len(elementsByName) > 0:
        elementValue = elementsByName[0].toxml().replace(
            '<' + elementName + '>', '').replace('</' + elementName + '>', '')
    return elementValue


def date_to_iso8601(date):
    """Returns an ISO8601 string from a date"""
    datetimestr = date.strftime('%Y-%m-%dT%H:%M:%S')
    timezone_sign = date.strftime('%z')[0:1]
    timezone_str = '%s:%s' % (
        date.strftime('%z')[1:3], date.strftime('%z')[3:5])
    return '{datetimestr}{tzsign}{timezone}'.format(
        datetimestr=datetimestr,
        tzsign=timezone_sign,
        timezone=timezone_str
        ).replace(':', '%3A').replace('+', '%2B')


class SalesforceError(Exception):
    """Base Salesforce API exception"""

    message = u'Unknown error occurred for {url}. Response content: {content}'

    def __init__(self, url, status, resource_name, content):
        # TODO exceptions don't seem to be using parent constructors at all.
        # this should be fixed.
        # pylint: disable=super-init-not-called
        self.url = url
        self.status = status
        self.resource_name = resource_name
        self.content = content

    def __str__(self):
        return self.message.format(url=self.url, content=self.content)

    def __unicode__(self):
        return self.__str__()


###########################################################
###SOAP String
########################################################### 
def get_soap_anonymous_body(apex_string):
    apex_string = quoteattr(apex_string).replace('"', '')
    return '<apex:executeAnonymous><apex:String>{0}</apex:String></apex:executeAnonymous>'.format(apex_string)

def create_apex_envelope(session_id, debug_levels, request_body):
    # print('------->')
    # print(settings)
    # debug_levels -> settings["debug_levels"] 

    log_levels = ""
    for log_cat in debug_levels:
        log_level = debug_levels[log_cat]
        log_levels += """
            <apex:categories>
                <apex:category>%s</apex:category>
                <apex:level>%s</apex:level>
            </apex:categories>
        """ % (log_cat, log_level)

    apex_request_envelope = """<soapenv:Envelope 
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
        xmlns:apex="http://soap.sforce.com/2006/08/apex">
        <soapenv:Header>
            <apex:DebuggingHeader>
                {log_levels}
            </apex:DebuggingHeader>
            <apex:SessionHeader>
                <apex:sessionId>{session_id}</apex:sessionId>
            </apex:SessionHeader>
        </soapenv:Header>
        <soapenv:Body>
            {body}
        </soapenv:Body>
    </soapenv:Envelope>
    """.format(log_levels=log_levels, session_id=session_id, body=request_body)

    return_body = apex_request_envelope.encode("utf-8")

    return return_body

# How do you split a list into evenly sized chunks?
def chunks(li, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(li), n):
        yield li[i:i + n]

def debug(msg):
    print(msg)

