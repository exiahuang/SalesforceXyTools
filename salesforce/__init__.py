"""Simple-Salesforce Package"""
# flake8: noqa

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


from .soap import (
    Soap
)
