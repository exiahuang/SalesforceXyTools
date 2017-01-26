#SalesforceXyTools

SalesforceXyTools for Sublime Text is Rapid development tools for Salesforce Development.

* Auto Create Apex Test Class Code, Auto Create Test Data For Apex Test Class.
* SFDC Dataviewer, SFDC Online Dataviewer.
* SObject Viewer, SObject Description, Export SOjbect Fields to Excel
* Atuo Login SFDC.
* SOQL Query, Tooling Query, Run Apex Script.

# SalesforceXyTools Help

  * [SalesforceXyTools Introduce](http://www.ibmer.info/salesforcexytools.html)
  * [SalesforceXyTools Install](http://www.ibmer.info/salesforcexytools-install.html)
  * [SalesforceXyTools Auto Create VF-Controller-DTO-DAO-Code](http://www.ibmer.info/auto-create-sfdc-code.html)
  * [SalesforceXyTools: Export Sobject To Excel](http://www.ibmer.info/export-sobject-excel.html)
  * [SalesforceXyTools Sublime Package](https://packagecontrol.io/packages/SalesforceXyTools)


## Basic on OpenSource
1. [xlsxwriter (License: BSD)](https://github.com/jmcnamara/XlsxWriter)
2. [Simple-Salesforce (License: Apache 2.0)](https://pypi.python.org/pypi/simple-salesforce/0.72.2)
3. [requests (License: Apache 2.0)](https://pypi.python.org/pypi/requests/2.12.3)

~~[XLWT (License: BSD)](https://pypi.python.org/pypi/xlwt)~~

## Issues

All issues are managed by the [SalesforceXyTools](https://github.com/exiahuang/SalesforceXyTools)

## Install [more install help](http://www.ibmer.info/salesforcexytools-install.html)

### Prerequisites

- Sublime Text 3 [http://www.sublimetext.com/3](http://www.sublimetext.com/3)
- Sublime Text Package Control [https://packagecontrol.io/installation](https://packagecontrol.io/installation)

### Plugin Installation(Use Package Control to Install)

1. Open Sublime Text 3
2. Run `Package Control: Install Package` command
	- [Running commands from Sublime Text](http://docs.sublimetext.info/en/latest/extensibility/command_palette.html)
3. Search for `SalesforceXyTools`
4. Hit `Enter`

## Setup

###Important Settings  
####Use OAuth2 Login  
* There are three type to access salesforce: oauth2 or password or use mavensmate
* The default value is oauth2.
* You can set `authentication` as below : "oauth2","password","mavensmate".
* You can use [SFDC-XY] -> [Change Authentication Type] to set your authentication type.  
   
```
"authentication":"oauth2",
```

####Use Password Login  
* If you like to use password to access salesforce,you need to `authentication` as password.  
* You never need to re-auth if you use this method.  
* Please set the `default_project` and `projects` if you use this type to access salesforce.  
  
```
"authentication":"password",
```  

####Use [Mavensmate](https://github.com/joeferraro/MavensMate-SublimeText) Session  
* If you like to use mavensmate's setting, you can set `authentication` mavensmate.
* mavensmate-destop v0.0.10 or below, please set mm_use_keyring true.
* mavensmate-destop v0.0.11-beta.2 to v0.0.11-beta.7, please set mm_use_keyring false.
  
```
"authentication":"oauth2",
```

*`use_mavensmate_setting` is No Longer Forever.*
  
~~You may set `use_mavensmate_setting` to a single path on your local filesystem or an array of paths.~~
~~If you set `use_mavensmate_setting` true, you can use all the setting of mavensmate, you need not to set `projects` and `default_project` .~~
  
~~"use_mavensmate_setting" : true~~

mavensmate-destop v0.0.10 or below, please set mm_use_keyring true.
please re-auth again, Or Create project again!
![SOS](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/Setup/Image%20001.jpg?raw=true)


mavensmate-destop v0.0.11-beta.2 to v0.0.11-beta.7, please set mm_use_keyring false.
please re-auth again, Or Create project again!
![SOS](https://github.com/exiahuang/XyHelp/blob/master/SalesforceXyTools/Setup/Image%20002.jpg?raw=true)


####Use `projects` Setting

* If you set `use_mavensmate_setting` false, please set the `default_project` and `projects` as the example.    
  
#####Examples of projects

  ```
"default_project":"huangxy1",
 "projects":
    {
        // the Example of the projects 
        // If you set the use_mavensmate_setting false, 
        // you need to set "projects" value below.

        // if you use oauth2 to authenticate salesforce,
        // you can use the setting as below
        "huangxy1":
        {
          "loginUrl": "https://login.salesforce.com",
          "password": "XXXXXXX",
          // if you have not security_token,please set ""
          "security_token": "",
          "username": "XXXXXXX@ibmer.info",
          "is_sandbox": false,
          // "api_version" is not Required, if not set, it will use default_api_version
          "api_version": 36.0,
          "workspace": "C:/workspace/huangxy1/"
        },
        // if you use password to authenticate salesforce,
        // you can use the setting as below
        "huangxy2":
        {
          "loginUrl": "https://test.salesforce.com",
          "password": "XXXXXXX",
          "security_token": "",
          "username": "XXXXXXX@ibmer.info",
          "is_sandbox": true,
          "workspace": "C:\\workspace\\huangxy2\\"
        }
    }
  ```

#### Define your login browser
Add your `browsers` setting as below.
You can use [SFDC-XY] -> [Switch Broswer] to set your default browser.
  ```
    // Add your browser which you like!
    // examle:
    // "firefox":"Path of firefox!",
    // "Edge":"Path of Edge", or another
    "browsers":
    {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "IE": "C:\\Program Files\\Internet Explorer\\iexplore.exe"
    },
  ```


## Usage [more usage help](https://github.com/exiahuang/SalesforceXyTools/blob/master/help/SalesforceXyTools-Help.md)

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


