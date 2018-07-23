DEPLOY = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <deploy xmlns="http://soap.sforce.com/2006/04/metadata">
      <ZipFile>%(package_zip)s</ZipFile>
      <DeployOptions>
        <allowMissingFiles>false</allowMissingFiles>
        <autoUpdatePackage>false</autoUpdatePackage>
        <checkOnly>false</checkOnly>
        <ignoreWarnings>true</ignoreWarnings>
        <performRetrieve>false</performRetrieve>
        <purgeOnDelete>%(purge_on_delete)s</purgeOnDelete>
        <rollbackOnError>true</rollbackOnError>
        <runAllTests>false</runAllTests>
        <singlePackage>true</singlePackage>
      </DeployOptions>
    </deploy>
  </soap:Body>
</soap:Envelope>'''

CHECK_DEPLOY_STATUS = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <checkDeployStatus xmlns="http://soap.sforce.com/2006/04/metadata">
      <asyncProcessId>%(process_id)s</asyncProcessId>
      <includeDetails>true</includeDetails>
    </checkDeployStatus>
  </soap:Body>
</soap:Envelope>'''

RETRIEVE_INSTALLEDPACKAGE = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <retrieve xmlns="http://soap.sforce.com/2006/04/metadata">
      <retrieveRequest>
        <apiVersion>{api_version}</apiVersion>
        <unpackaged>
          <types>
            <members>*</members>
            <name>InstalledPackage</name>
          </types>
          <version>{api_version}</version>
        </unpackaged>
      </retrieveRequest>
    </retrieve>
  </soap:Body>
</soap:Envelope>'''

RETRIEVE_PACKAGED = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <retrieve xmlns="http://soap.sforce.com/2006/04/metadata">
      <retrieveRequest>
        <apiVersion>{}</apiVersion>
        <packageNames>{}</packageNames>
      </retrieveRequest>
    </retrieve>
  </soap:Body>
</soap:Envelope>'''



LIST_METADATA = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:meta="http://soap.sforce.com/2006/04/metadata">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <listMetadata xmlns="http://soap.sforce.com/2006/04/metadata">
      {queries_type}
      <asOfVersion>{as_of_version}</asOfVersion>
    </listMetadata>
  </soap:Body>
</soap:Envelope>'''


LIST_METADATA = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:meta="http://soap.sforce.com/2006/04/metadata">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <listMetadata xmlns="http://soap.sforce.com/2006/04/metadata">
      {queries_type}
      <asOfVersion>{as_of_version}</asOfVersion>
    </listMetadata>
  </soap:Body>
</soap:Envelope>'''

DESCRIBEMETATDATA = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:meta="http://soap.sforce.com/2006/04/metadata">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <describeMetadata xmlns="http://soap.sforce.com/2006/04/metadata">
      <asOfVersion>{as_of_version}</asOfVersion>
    </describeMetadata>
  </soap:Body>
</soap:Envelope>
'''

PACKAGEXML_TYPE = """
    <types>
{members}
        <name>{name}</name>
    </types>"""

PACKAGE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
{types}
    <version>{version}</version>
</Package>
"""

PACKAGEXML_TYPE_StandardValueSet_V38_LIST = ["AccountContactMultiRoles", "AccountContactRole", "AccountOwnership", "AccountRating", "AccountType", "AssetStatus", "CampaignMemberStatus", "CampaignStatus", "CampaignType", "CaseContactRole", "CaseOrigin", "CasePriority", "CaseReason", "CaseStatus", "CaseType", "ContactRole", "ContractContactRole", "ContractStatus", "EntitlementType", "EventSubject", "EventType", "FiscalYearPeriodName", "FiscalYearPeriodPrefix", "FiscalYearQuarterName", "FiscalYearQuarterPrefix", "IdeaCategory", "IdeaMultiCategory", "IdeaStatus", "IdeaThemeStatus", "Industry", "LeadSource", "LeadStatus", "OpportunityCompetitor", "OpportunityStage", "OpportunityType", "OrderType", "PartnerRole", "Product2Family", "QuestionOrigin", "QuickTextCategory", "QuickTextChannel", "QuoteStatus", "RoleInTerritory2", "SalesTeamRole", "Salutation", "ServiceContractApprovalStatus", "SocialPostClassification", "SocialPostEngagementLevel", "SocialPostReviewedStatus", "SolutionStatus", "TaskPriority", "TaskStatus", "TaskSubject", "TaskType", "WorkOrderLineItemStatus", "WorkOrderPriority", "WorkOrderStatus"]

PACKAGEXML_TYPE_StandardValueSet_V37_LIST = ["AccountContactRelation.Roles", "AccountContactRole.Role", "Account.Ownership", "Account.RatingLead.Rating", "Account.Type", "Asset.Status", "CampaignMember.Status", "Campaign.Status", "Campaign.Type", "CaseContactRole.Role", "Case.Origin", "Case.Priority", "Case.Reason", "Case.Status", "Case.Type", "OpportunityContactRole.Role", "ContractContactRole.Role", "Contract.Status", "Entitlement.Type", "Event.Subject", "Event.Type", "Period.PeriodLabel", "FiscalYearSettings.PeriodPrefix", "Period.QuarterLabel", "FiscalYearSettings.QuarterPrefix", "IdeaTheme.Categories1", "Idea.Categories", "Idea.Status", "IdeaTheme.Status", "Account.IndustryLead.Industry", "Account.AccountSource", "Lead.LeadSource", "Opportunity.Source", "Lead.Status", "Opportunity.Competitors", "Opportunity.StageName", "Opportunity.Type", "Order.Type", "Account.PartnerRole", "Product2.Family", "Question.Origin1", "QuickText.Category", "QuickText.Channel", "Quote.Status", "UserTerritory2Association.RoleInTerritory2", "OpportunityTeamMember.TeamMemberRole", "UserAccountTeamMember.TeamMemberRole", "UserTeamMember.TeamMemberRole", "AccountTeamMember.TeamMemberRole", "Contact.Salutation", "Lead.Salutation", "ServiceContract.ApprovalStatus", "SocialPost.Classification", "SocialPost.EngagementLevel", "SocialPost.ReviewedStatus", "Solution.Status", "Task.Priority", "Task.Status", "Task.Subject", "Task.Type", "WorkOrderLineItem.Status", "WorkOrder.Priority", "WorkOrder.Status"]

RETRIEVE_UNPACKAGED = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <retrieve xmlns="http://soap.sforce.com/2006/04/metadata">
      <retrieveRequest>
        <apiVersion>{version}</apiVersion>
        <unpackaged>
          {unpackaged} 
        </unpackaged>
      </retrieveRequest>
    </retrieve>
  </soap:Body>
</soap:Envelope>'''

CHECK_RETRIEVE_STATUS = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <checkRetrieveStatus xmlns="http://soap.sforce.com/2006/04/metadata">
      <asyncProcessId>{process_id}</asyncProcessId>
    </checkRetrieveStatus>
  </soap:Body>
</soap:Envelope>'''


CHECK_STATUS = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Header>
    <SessionHeader xmlns="http://soap.sforce.com/2006/04/metadata">
      <sessionId>{session_id}</sessionId>
    </SessionHeader>
  </soap:Header>
  <soap:Body>
    <checkStatus xmlns="http://soap.sforce.com/2006/04/metadata">
      <asyncProcessId>%(process_id)s</asyncProcessId>
    </checkStatus>
  </soap:Body>
</soap:Envelope>'''


# query_option_list : max length is 3.
def get_list_metadata_envelope(session_id, query_option_list, api_version):
    queries_type = ""
    for query_option in query_option_list:
          if query_option['folder'] is None or query_option['folder'] == '':
              queries_type = queries_type + """
                    <queries>
                      <type>{metadata_type}</type>
                    </queries>""".format(metadata_type=query_option['metadata_type'])
          else:
              queries_type = queries_type + """
                    <queries>
                      <type>{metadata_type}</type>
                      <folder>{folder}</folder>
                    </queries>""".format(metadata_type=query_option['metadata_type'], folder=query_option['folder'])
    return LIST_METADATA.format(
        queries_type=queries_type,
        as_of_version=api_version,
        session_id=session_id
    )

def get_describe_metadata_envelope(session_id, api_version):
    return DESCRIBEMETATDATA.format(
        as_of_version=api_version,
        session_id=session_id
    )

def get_StandardValueSet(version):
    f_version = float(version)
    if f_version >= 38.0:
        return PACKAGEXML_TYPE_StandardValueSet_V38_LIST
    else:
        return PACKAGEXML_TYPE_StandardValueSet_V37_LIST


def get_retrieve_unpackaged_envelope(session_id, package_type_list, api_version):
    packagexml_types = ""
    for package_type in package_type_list:
        members = ["""        <members>{member}</members>""".format(member=member) for member in package_type["members"]]
        packagexml_types = packagexml_types + PACKAGEXML_TYPE.format(members='\n'.join(members),name=package_type["name"])
    return RETRIEVE_UNPACKAGED.format(
        version=api_version,
        unpackaged=packagexml_types,
        session_id=session_id
    )


def get_check_retrieve_status(session_id, process_id):
    return CHECK_RETRIEVE_STATUS.format(
        process_id=process_id,
        session_id=session_id
    )