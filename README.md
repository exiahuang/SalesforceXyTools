# About Cli and vscode

- [exiahuang/sfdc-cli](https://github.com/exiahuang/sfdc-cli) is a sfdc development kit. sfdc-cli is base on SalesforceXytoolsForSublime.
- [exiahuang/xysfdx](https://github.com/exiahuang/xysfdx) is a vscode plugin, support sfdx and sfdc-cli.


# SalesforceXytoolsForSublime

[SalesforceXytoolsForSublime](http://salesforcexytools.com/SalesforceXyTools/) is Rapid development tools for Salesforce Development.

- Create Salesforce Project, Retrieve Metadata, Search Metadata

- Create ApexClass, ApexTrigger, ApexComponent, Refresh, Diff with Server(Support winmerge diff), Save to Server, Deploy to Server

- SObject Viewer, SObject Description, Export SOjbect Fields to Excel

- Run SOQL Query, Tooling Query, Apex Script.

- Code Creator : Auto Create Apex Test Class Code, Auto Create Test Data For Apex Test Class.

- SFDC Dataviewer, SFDC Online Dataviewer.

- Atuo Login SFDC (two login type: oauth2 , password config).

- Quick local sfdc file from sublime.

- Quick Search SObject Data/SObject Setting/ApexClass/Trigger/VisualForce Page/VisualForce Components/Email Template/Static Resource and open on browser Quickly

- Package.xml Builder.

- Build Release Package.

- Integrate Sfdc Dataloader, Config DataLoader and Run (**Need Ant and Java Environment**)

  **Set your schedule, backup your sfdc data.**

- Integrate Sfdc Migration Tool (**Need Ant and Java Environment**)

- Auto Backup all metadata script(**Set your schedule, backup your sfdc metadata.**).

- Support sfdx command (From v2.1.6), [Document](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-Support-Git/)

- Support git command (From v2.1.7), [Document](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-Support-Sfdx-Develop/)

# Basic on OpenSource

SalesforceXyToolsForSublime is based on python and open source below.

1. [xlsxwriter (License: BSD)](https://github.com/jmcnamara/XlsxWriter)
2. [Simple-Salesforce (License: Apache 2.0)](https://pypi.python.org/pypi/simple-salesforce/0.72.2)
3. [requests (License: Apache 2.0)](https://pypi.python.org/pypi/requests/2.12.3)
4. [Apex Template From MavensMate](https://github.com/joeferraro/MavensMate/tree/master/app/lib/templates/github)

# Include Salesforce Migration Tool And Dataloader
> Include salesforce ant-salesforce.jar and dataloader.jar
> ant-salesforce.jar and dataloader.jar will be downloaded by salesforcexytools.
> You will not need to download them.
1. [Ant Migration Tool](https://developer.salesforce.com/docs/atlas.en-us.216.0.daas.meta/daas/meta_development.htm)
2. [Data Loader](https://developer.salesforce.com/docs/atlas.en-us.216.0.dataLoader.meta/dataLoader/data_loader.htm)

# SalesforceXyToolsForSublime Reference

* [SalesforceXyToolsForSublime Guide](http://salesforcexytools.com/SalesforceXyTools/)
* [SalesforceXyToolsForSublime-Rapid-development-tools-for-Salesforce](http://salesforcexytools.com/SalesforceXyTools/SalesforceXyTools-For-Sublime/)
* [SalesforceXyToolsForSublime-Rapid-development-tools-for-Salesforce.pdf](http://salesforcexytools.com/pdf/SalesforceXyToolsForSublime-Rapid-development-tools-for-Salesforce.pdf)
* [Source of SalesforceForSublime](https://github.com/exiahuang/SalesforceXyTools)
* [Issues of SalesforceXyToolsForSublime](https://github.com/exiahuang/SalesforceXyTools/issues)
* [Sublime Package Control](https://packagecontrol.io/packages/SalesforceXyTools)



# Document Reference
- [How to Install SalesforceXytoolsForSublime](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-001-Install/)
- [How to Config SalesforceXytoolsForSublime](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-002-Config/)
- [Use SalesforceXytoolsForSublime to develop SFDC](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-003-SFDC-Develop/)
- [Export Sobject to Excel and Search Sobject](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-004-Sobject/)
- [Run sfdc soql, apex script, tooling api](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-005-RunScript/)
- [Auto config salesforce ant-dataloader and Backup Sobject Data](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-006-Dataloader/)
- [Auto config salesforce ant-migration-tools and Backup Metadata](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-007-Migration-Tool/)
- [Export Sfdc Sobject Schema To Excel](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-008-Export-Sobject-Schema-To-Excel/)
- [Use SalesforceXytoolsForSublime Salesforce Deploy Package](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-009-DeployPackage-Builder/)
- [Salesforce package.xml Auto Builder](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-010-Packagexml-Builder/)
- [How to export Apex Code Coverage](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-011-Apex-Coverage/)
- [PermissionSet Builder](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-012-PermissionSet-Builder/)
- [Soql Creator](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-013-Create-Soql/)
- [Save Your Sfdc Module and build a deploy module package](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-014-Build-Deploy-Module/)
- [Search sfdc metadata](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-015-Search-SFDC-Metadata/)
- [Copy a Lightning Component](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-016-Copy-Lightning-component/)
- [Auto Create Salesforce VisualForce Apex](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-101-ApexCode-Creater/)
- [Salesforce test code creator](http://salesforcexytools.com/SalesforceXyTools/SalesforceXytoolsForSublime-102-TestClass-Creater/)
- [SalesforceXytoolsForSublime Reference](http://salesforcexytools.com/SalesforceXyTools/)



# About Author : Exia.Huang

* [SalesforceXyTools HP](http://salesforcexytools.com)
* [Github](https://github.com/exiahuang)
* [Twitter](https://twitter.com/ExiaSfdc)
* [Facebook](https://www.facebook.com/profile.php?id=100015890262852)
* [Qiita](https://qiita.com/exiasfdc)
* [Hatenaはてなブログ](https://exiasfdc.hatenablog.com/)


# Other tools for salesforce
* [SalesforceXyToolsCore](https://github.com/exiahuang/SalesforceXyToolsCore) is base on Python. 
The core of SalesforceXyTools For Sublime. Soap, Metadata, Rest API For Salesforce.

* [SalesforceXyTools For Chrome](http://salesforcexytools.com/Salesforce/SalesforceXyTools-For-Chrome.html)

* [Install SalesforceXyTools For Chrome From Web Store](https://chrome.google.com/webstore/detail/salesforcexytools/ehklfkbacogbanjgekccnbfdgjechlmf)

> SalesforceXyTools for Chrome is a developer tools for Salesforce,SFDC,Force.com. Login SFDC By 1 click. Quickly Search Metadata Sobject,Apex,Trigger,Page,Component,EmailTemplate,SataticResource, etc. Auto Create Soql, Run Soql, Soql History. Run Apex Script. Quick Search SFDC Document.

