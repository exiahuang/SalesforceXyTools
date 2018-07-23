"""Simple-Salesforce Package"""
# flake8: noqa

from .myconsole import MyConsole

from .api import (
    Salesforce,
    SalesforceAPI,
    SFType,
    SalesforceError,
    SalesforceMoreThanOneRecord,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceMalformedRequest
)

from .login import (
    SalesforceLogin, SalesforceAuthenticationFailed
)


from .core import (
    Soap,
    MetadataApi,
    ToolingApi,
    SoapException
)




from .bulk import Bulk
