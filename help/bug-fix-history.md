# SalesforceXyTools Update History

## 2.0.4
* Remove Python Jar `Auto Download`.
* Add Ant Auto Download task.
* Fix Code Creator.

## 2.0.3
* Add `Proxy` config
* Add `auto_save_to_server` config
* Fix Retrieve Source `src` lock

## 2.0.2
* Add Permisson Profile Builder(Profile/Permisson Set)
* Save Module / Open Module
* Fix New Metadata duplicate Error.
* Fix Package.xml CustomSobject Builder
* Pretty show run apex script, unescape `run apex script` log 

## 2.0.1
* Fix Ant Deploy Bug.
* Fix `open in browser`
* Add `Apex Code Coverage`

## 2.0.0 (2018.07.22)
* Create Salesforce Project, Retrieve Metadata, Search Metadata
* Create ApexClass, ApexTrigger, ApexComponent, Refresh, Diff with Server(Support winmerge diff), Save to Server, Deploy to Server
* Package.xml Builder.
* Integrate Sfdc Dataloader, Config DataLoader and Run(Need Ant and Java Environment)
* Integrate Sfdc Migration Tool (Need Ant and Java Environment)
* Atuo Login SFDC (two login type: oauth2 , password config).
*  change password config file 
   use [./`current workspace`/.xyconfig/xyconfig.json] to config password
   

## 1.0.8 (2017.03.03)
1. Add SFDC Quick Viewer
You can search SObject Data/SObject Setting/ApexClass/Trigger/VisualForce Page/VisualForce Components/Email Template/Static Resource and open on browser Quickly.
usage:
[SFDC-XY] -> [SFDC Quick Viewer]


## 1.0.7 (2017.01.31)
1. Auto Create Child-Parent Query.
2. Create DTO/DAO cls Include Child-Parent Relation.


## 1.0.6 (2017.01.26)
1. Add oauth2
2. Add Switch broswer
3. Add Switch Project
4. delete `use_mavensmate_setting` flag


##  1.0.5 (2017.01.19)
1. support for MavensMate-destop v0.0.11-beta.2 to v0.0.11-beta.7
	[Need more help?](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/Setup/Readme.md)

2. [Create VisualForce/Controller/DTO/DAO Code] bug fix.

##  1.0.4 (2017.01.19)
1. [Create VisualForce/Controller/DTO/DAO Code]
 Add Sobject List Page and List Controller
 Add Dao Search
 Add virtual SfdcXyController

##  1.0.3 (2017.01.17)
1. Create VisualForce/Controller/DTO/DAO Code bug fix
  Add Auto Create Edit/View/Message Mode.
2. Save SFDC Object List AS Excel
  Save all fields to Excel.


