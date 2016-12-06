#SalesforceXyTools

SalesforceXyTools for Sublime Text is Rapid development tools for Salesforce Development.

* Auto Create Apex Test Class Code, Auto Create Test Data For Apex Test Class.
* SFDC Dataviewer, SFDC Online Dataviewer
* SObject Viewer, SObject Description, Export SOjbect Fields to Excel
* Atuo Login SFDC.
* SOQL Query/ Tooling Query/ Run Apex Script

## Issues

All issues are managed by the [SalesforceXyTools](https://github.com/exiahuang/SalesforceXyTools)

## Install

### Prerequisites

- Sublime Text 3 [http://www.sublimetext.com/3](http://www.sublimetext.com/3)
- Sublime Text Package Control [https://packagecontrol.io/installation](https://packagecontrol.io/installation)

### Plugin Installation

1. Open Sublime Text 3
2. Run `Package Control: Install Package` command
	- [Running commands from Sublime Text](http://docs.sublimetext.info/en/latest/extensibility/command_palette.html)
3. Search for `SalesforceXyTools`
4. Hit `Enter`


## Setup

###Important Settings

####Use [Mavensmate](https://github.com/joeferraro/MavensMate-SublimeText) Session 

You may set `use_mavensmate_setting` to a single path on your local filesystem or an array of paths.
If you set `use_mavensmate_setting` true, you can use all the setting of mavensmate, you need not to add any ID/Password of SFDC.
```
"use_mavensmate_setting" : true
```

If you set `use_mavensmate_setting` false, please set the `default_project` and `projects` as the example.
#####Examples

######Array of projects

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

