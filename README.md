#SalesforceXyTools

SalesforceXyTools for Sublime Text is Rapid development tools for Salesforce Development.

* Auto Create Apex Test Class Code, Auto Create Test Data For Apex Test Class.
* SFDC Dataviewer, SFDC Online Dataviewer.
* SObject Viewer, SObject Description, Export SOjbect Fields to Excel
* Atuo Login SFDC.
* SOQL Query, Tooling Query, Run Apex Script.


## Basic on OpenSource
1. [XLWT (License: BSD)](https://pypi.python.org/pypi/xlwt)
2. [Simple-Salesforce (License: Apache 2.0)](https://pypi.python.org/pypi/simple-salesforce/0.72.2)
3. [requests (License: Apache 2.0)](https://pypi.python.org/pypi/requests/2.12.3)

## Issues

All issues are managed by the [SalesforceXyTools](https://github.com/exiahuang/SalesforceXyTools)

## Install

### Prerequisites

- Sublime Text 3 [http://www.sublimetext.com/3](http://www.sublimetext.com/3)
- Sublime Text Package Control [https://packagecontrol.io/installation](https://packagecontrol.io/installation)

### Plugin Installation(Use Package Control to Install)

1. Open Sublime Text 3
2. Run `Package Control: Install Package` command
	- [Running commands from Sublime Text](http://docs.sublimetext.info/en/latest/extensibility/command_palette.html)
3. Search for `SalesforceXyTools`
4. Hit `Enter`

### Plugin Installation(Use Source package)

1. Download [SalesforceXyTools](https://github.com/exiahuang/SalesforceXyTools/archive/master.zip)
2. Open Sublime Text 3
3. Prefences -> Browse Packages 
4. Extra zip file which you download
```
    Extra path Example:
    {Path Of Sublime Text}\Data\Packages\SalesforceXyTools-master
```

## Setup

###Important Settings

####Use [Mavensmate](https://github.com/joeferraro/MavensMate-SublimeText) Session 

You may set `use_mavensmate_setting` to a single path on your local filesystem or an array of paths.
If you set `use_mavensmate_setting` true, you can use all the setting of mavensmate, you need not to set `projects` or `default_project` .
```
"use_mavensmate_setting" : true
```

####Use `projects` Setting

If you set `use_mavensmate_setting` false, please set the `default_project` and `projects` as the example.

#####Examples of projects

```
"default_project":"huangxy1",
 "projects":
    {
        "huangxy1":
        {
            "loginUrl": "https://login.salesforce.com",
            "password": "XXXXXXX",
            "security_token": "XXXXXXXXXXXXXXX",
            "username": "XXXXXXX@ibmer.info",
            "api_version": 36.0,
            "is_sandbox": false,
            "workspace": "C:/workspace/huangxy1/"
        },
        "huangxy2":
        {
            "loginUrl": "https://test.salesforce.com",
            "password": "XXXXXXX",
            "security_token": "XXXXXXX",
            "username": "XXXXXXX@ibmer.info",
            "api_version": 36.0,
            "is_sandbox": true,
            "workspace": "C:/workspace/huangxy2/"
        }
    }
```



## Usage
#### Run SOQL/Run Tooling api
Select your SOQL, [SFDC-XY] -> [SFDC SOQL] -> [SOQL Query]/[Tooling Query] and run!

![Run SOQL](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/sfdc_soql.gif?raw=true)


#### SFDC Object Descript, Save as Excel
Path: [SFDC-XY] -> [SFDC Object]

![SFDC Object](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/sfdc_object.gif?raw=true)


#### SFDC DataViewer
Path: [SFDC-XY] -> [SFDC Dataviewer]

![SFDC Object](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/dataviwer.gif?raw=true)



#### Create Test Code
Open your apex code, [SFDC-XY] -> [SFDC Code Creator] -> [Create Test Code] and you can auto creat your apex test class!! 

![Create Test Code](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/test_class_create.gif?raw=true)


#### ApexController , Viewer , TestClass Quick Jump 
Right Click, and find the click!

![Controller_VF_Jump](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/Controller_VF_Jump.gif?raw=true)
