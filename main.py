import sublime
import sublime_plugin
import os
import threading
# import datetime
# import sys, xdrlib
# import json
# import random

# from . import xlwt
# from . import requests
from . import util
from . import codecreator
from . import setting
from . import xlsxwriter
from .requests.exceptions import RequestException
from .salesforce import (
    SalesforceMoreThanOneRecord,
    SalesforceMalformedRequest,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceError
    )

AUTO_CODE_DIR = "code-creator"

##########################################################################################
#Sublime main menu
##########################################################################################
# Oauth2
# class OauthCheckCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         util.stop_server()
        # util.open_in_default_browser(authorize_url)

# print the SFDC Object
class ShowSfdcObjectListCommand(sublime_plugin.TextCommand):
    def main_handle(self):
        try:
            sf = util.sf_login()
            message = 'label, name, keyPrefix' + "\n"
            for x in sf.describe()["sobjects"]:
              message += util.xstr(x["label"]) + "," + util.xstr(x["name"]) + "," + util.xstr(x["keyPrefix"]) + "\n"

            # util.show_in_new_tab(message)
            file_name = sf.settings["default_project"] + '_sobject_lst.csv'
            util.save_and_open_in_panel(message, file_name, True )

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return    

    def run(self, edit):
        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

# Save the SFDC Object As Excel
# # use xlsxwriter to write excel
class SaveSfdcObjectAsExcelCommand(sublime_plugin.WindowCommand):
    def main_handle(self, savePath = ''):
        try:
            dirPath = os.path.dirname(savePath)
            util.makedir(dirPath)

            sf = util.sf_login()
            # contact = sf.query("SELECT Id, Email FROM Contact limit 1")

            sfdesc = sf.describe()
            book = xlsxwriter.Workbook(savePath)
            newSheet_1Name = 'オブジェクトリスト'
            newSheet_1 = book.add_worksheet(newSheet_1Name)
            newSheet_1.write(0, 0, 'label')
            newSheet_1.write(0, 1, 'name')
            newSheet_1.write(0, 2, 'keyPrefix')
            index = 1;

            sheetIndexMap = {}
            sheetIndex = 0;
            sheetIndexMap[0] = newSheet_1Name

            sheetNameList = []

            headers = ['name','label','type','length','scale','updateable','unique','custom','picklistValues','aggregatable','autoNumber','byteLength','calculated','calculatedFormula','cascadeDelete','caseSensitive','controllerName','createable','defaultValue','defaultValueFormula','defaultedOnCreate','dependentPicklist','deprecatedAndHidden','digits','displayLocationInDecimal','encrypted','externalId','extraTypeInfo','filterable','filteredLookupInfo','groupable','highScaleNumber','htmlFormatted','idLookup','inlineHelpText','mask','maskType','nameField','namePointing','nillable','permissionable','precision','queryByDistance','referenceTargetField','referenceTo','relationshipName','relationshipOrder','restrictedDelete','restrictedPicklist','soapType','sortable','writeRequiresMasterRead']

            for x in sf.describe()["sobjects"]:
              #write to xls
              # book.get_sheet(0)
              newSheet_1.write(index, 0, util.xstr(x["label"]))
              newSheet_1.write(index, 1, util.xstr(x["name"]))
              newSheet_1.write(index, 2, util.xstr(x["keyPrefix"]))
              index = index + 1
              #print(sf.Kind__c.describe())
              #print(x["name"])
              #print(x["custom"])
              if x["custom"]:
                  sheetIndex += 1
                  
                  # sftype = SFType(util.xstr(x["name"]), sf.session_id, sf.sf_instance, sf_version=sf.sf_version,
                  #               proxies=sf.proxies, session=sf.session)
                  sftype = sf.get_sobject(util.xstr(x["name"]))

                  #print(x["name"])     
                  #write to xls
                  # worksheet_name = x["name"]
                  # if len(worksheet_name) > 31:
                  #   worksheet_name = (x["name"].replace("_",""))[0:31]
                  
                  worksheet_name = x["label"]
                  if len(worksheet_name) > 31:
                    worksheet_name = (x["label"])[0:31]
                  if worksheet_name in sheetNameList:
                    worksheet_name = (x["label"])[0:25] + "_" + util.random_str(4)
                  
                  sheetNameList.append(worksheet_name)


                  fieldSheet_1 = book.add_worksheet(worksheet_name)

                  fieldSheet_1.write(0, 0, 'sobject')
                  fieldSheet_1.write(0, 1, x["name"])
                  fieldSheet_1.write(1, 0, 'label')
                  fieldSheet_1.write(1, 1, x["label"])
                  fieldSheet_1.write(2, 0, 'keyPrefix')
                  fieldSheet_1.write(2, 1, x["keyPrefix"])

                  # book.get_sheet(sheetIndex)
                  rowIndex = 4;
                  headerIndex = 0
                  for header in headers:
                    fieldSheet_1.write(rowIndex, headerIndex, header)
                    headerIndex = headerIndex + 1

                  sftypedesc = sftype.describe()
                  for field in sftypedesc["fields"]:
                     print(field)  
                     #print(field["name"])  
                     #print(field["label"])  
                     #print(field["type"])  
                     #print(field["length"])  
                     #print(field["scale"])  
                     rowIndex += 1
                     headerIndex = 0
                     for header in headers:
                        if header == "picklistValues":
                            picklistValuesStr = ''
                            for pv in field[header]:
                                picklistValuesStr += pv['label'] + ':' + pv['value'] + '\n'
                            fieldSheet_1.write(rowIndex, headerIndex, picklistValuesStr)
                        else:
                            fieldSheet_1.write(rowIndex, headerIndex, util.xstr(field[header]))
                        headerIndex = headerIndex + 1

              #message += x["label"] + "\n"

            # book.save( settings["default_project"] + '_sobject.xls')
            util.show_in_dialog("Done! Please see the dir below: \n" + dirPath)
            # isOpen = sublime.ok_cancel_dialog('Do you want to open the directory?')
            # if isOpen:


        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def on_input(self, args):
        thread = threading.Thread(target=self.main_handle, args=(args, ))
        thread.start()
        util.handle_thread(thread)


    def run(self):
        settings = setting.load()
        self.fullPath =  os.path.join(util.get_default_floder(), settings["default_project"] + '_sobject.xlsx')
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel("Please Input FullPath of fileName: " , 
            self.fullPath, self.on_input, None, None)
        

# Soql Query
class SoqlQueryCommand(sublime_plugin.TextCommand):
    def main_handle(self, sel_string = ''):
        try:
            sf = util.sf_login()

            soql_str = soql_format(sf,sel_string)

            print('------>soql')
            print(soql_str)
            
            soql_result = sf.query(soql_str)
            print('----->soql_result')  
            print(soql_result)  


            # header = [key for key in soql_result['records'].iterkeys()]
            # print(header)
            message = util.get_soql_result(soql_str, soql_result)

            util.show_in_new_tab(message)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def run(self, edit):
        sel_area = self.view.sel()
        if sel_area[0].empty():
          util.show_in_dialog("Please select the SOQL !!")
          return
        else:
            soql_string = self.view.substr(sel_area[0])
            soql_string = util.del_comment(soql_string)

        # TODO
        # sobject_name = util.get_soql_sobject(soql_string)
        # if not sobject_name:
        #     util.show_in_dialog("Please select SOQL !")
        #     return

        thread = threading.Thread(target=self.main_handle, args=(soql_string, ))
        thread.start()
        util.handle_thread(thread)


# ToolingQueryCommand
class ToolingQueryCommand(sublime_plugin.TextCommand):
    def main_handle(self, sel_string = ''):
        try:
            # print("ToolingQueryCommand Start")

            sf = util.sf_login()
            
            params = {'q': sel_string}
            soql_result = sf.restful('tooling/query', params)
            # header = [key for key in soql_result['records'].iterkeys()]
            # print(header)
            message = util.get_soql_result(sel_string, soql_result)

            util.show_in_new_tab(message)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def run(self, edit):
        sel_area = self.view.sel()
        if sel_area[0].empty():
          util.show_in_dialog("Please select the Tooling SOQL !!")
          return
        else:            
            sel_string = self.view.substr(sel_area[0])
            sel_string = util.del_comment(sel_string)

        thread = threading.Thread(target=self.main_handle, args=(sel_string, ))
        thread.start()
        util.handle_thread(thread)

# SFDC Coverage
class SfdcCoverageCommand(sublime_plugin.TextCommand):
    def main_handle(self):
        try:
            sf = util.sf_login()
            apexClassSoql = "select Id, Name, ApiVersion, LengthWithoutComments from ApexClass where Status = 'Active'"
            apexClass = sf.query(apexClassSoql)
            

            apexCodeCoverageSoql = "select Id , ApexClassOrTriggerId , NumLinesCovered , NumLinesUncovered FROM ApexCodeCoverageAggregate"
            params = {'q': apexCodeCoverageSoql}
            apexCodeCoverage = sf.restful('tooling/query', params)

            util.show_in_new_tab(util.xstr(apexClass))
            util.show_in_new_tab(util.xstr(apexCodeCoverage))

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def run(self, edit):
        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

# RunApexScript
class RunApexScriptCommand(sublime_plugin.TextCommand):
    def main_handle(self, sel_string = ''):
        try:
            sel_area = self.view.sel()
            sf = util.sf_login()
            result = sf.execute_anonymous(sel_string)
            # print(result)
            util.show_in_new_tab(result["debugLog"])
             
        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return


    def run(self, edit):
        sel_area = self.view.sel()
        if sel_area[0].empty():
          util.show_in_dialog("Please select the Tooling SOQL !!")
          return
        else:
            sel_string = self.view.substr(sel_area[0])
            sel_string = util.del_comment(sel_string)
                        
        thread = threading.Thread(target=self.main_handle, args=(sel_string, ))
        thread.start()
        util.handle_thread(thread)


# Login Salesforce
class LoginSfdcCommand(sublime_plugin.WindowCommand):
    def run(self):
    #     try:
    #         self.dirs = setting.get_browser_setting()
    #         dirs = []
    #         for dir in self.dirs:
    #             dirs.append(dir[0])

    #         self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

    #     except Exception as e:
    #         util.show_in_panel(e)
    #         return

    # def panel_done(self, picked):
    #     if 0 > picked < len(self.dirs):
    #         return
    #     self.browser = self.dirs[picked][0]
    #     self.broswer_path = self.dirs[picked][1]

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):
        try:
            sf = util.sf_login()
            login_sf_home(self, sf)
        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            return

# Login Project
class LoginProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = setting.load()
        self.settings = settings
        projects = settings["projects"]
        dirs = []
        for project_key in projects.keys():
            project_value = projects[project_key]
            dirs.append(project_key)

        self.results = dirs
        self.window.show_quick_panel(dirs, self.panel_done,
            sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_project = self.results[picked]

        self.dirs = setting.get_browser_setting()
        dirs = []
        for dir in self.dirs:
            dirs.append(dir[0])

        sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.browser_choose), 10)

    def browser_choose(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.browser = self.dirs[picked][0]
        self.broswer_path = self.dirs[picked][1]
        
        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

    def main_handle(self):
        try:
            sf = util.sf_login(self.picked_project)
            # login_sf_home(self, sf)
            login_sf_home(self, sf, self.browser, self.broswer_path)
        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            return




# sfdc_dataviewer
class SfdcDataviewerCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            self.settings = self.sf.settings

            dirs = []
            self.results = []
            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]) +' : Export to Tab ')
                self.results.append(util.xstr(x["name"]))
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):
        self.sftype = self.sf.get_sobject(self.picked_name)

        soql = 'SELECT '
        fields = []

        sftypedesc = self.sftype.describe()
        for field in sftypedesc["fields"]:
            fields.append(util.xstr(field["name"]))
        soql += ' , '.join(fields)
        soql += ' FROM ' + self.picked_name
        if 'soql_select_limit' in self.settings:
            soql += ' LIMIT ' + util.xstr(self.settings["soql_select_limit"])

        message = 'soql : ' + soql + '\n\n\n\n'

        soql_result = self.sf.query(soql)
        message += util.get_soql_result(soql, soql_result)

        util.show_in_new_tab(message)



# sfdc_online_dataviewer
class SfdcQuickViewerCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.menu = [
                "0. Reload Cache",
                "1. Search All", 
                "2. SObject Data", 
                "3. SObject Setting", 
                "4. ApexClass", 
                "5. Trigger", 
                "6. VisualForce Page",
                "7. VisualForce Components", 
                "8. Email Template", 
                "9. Static Resource" 
                # "10. Workflow Rule", 
                # "11. Validate Rule"
                ]
         
        sublime.set_timeout(lambda:self.window.show_quick_panel(self.menu, self.select_menu), 10)

    def select_menu(self, picked):
        if 0 > picked < len(self.menu):
            return
        self.sel_menu = picked
        self.sel_key = self.menu[picked]

        self.tooling_soql = {}
        self.tooling_soql[self.menu[3]] = 'SELECT id,developername FROM CustomObject'
        self.tooling_soql[self.menu[4]] = 'SELECT id,name FROM ApexClass'
        self.tooling_soql[self.menu[5]] = 'SELECT id,name FROM ApexTrigger'
        self.tooling_soql[self.menu[6]] = 'SELECT id,name FROM ApexPage'
        self.tooling_soql[self.menu[7]] = 'SELECT id,name FROM ApexComponent'
        self.tooling_soql[self.menu[8]] = 'SELECT id,name FROM EmailTemplate'
        self.tooling_soql[self.menu[9]] = 'SELECT id,name FROM StaticResource'
        # self.tooling_soql[self.menu[10]] = 'SELECT id,fullname FROM WorkflowRule'
        # self.tooling_soql[self.menu[11]] = 'SELECT Id,FullName FROM ValidationRule'


        self.sf = util.sf_login()
        self.settings = self.sf.settings
        default_project = self.settings['default_project_value']['project_name']
        
        s = sublime.load_settings(setting.SFDC_CACHE_SETTINGS)
        project_meta_map = s.get(default_project)
        # print('project_meta_map-->')
        # print(project_meta_map)

        # Reload Cache
        if picked == 0:
            thread = threading.Thread(target=self.reload_cache)
            thread.start()
            util.handle_thread(thread)
        else:
            # reload cache
            if (project_meta_map is None):
                # thread = threading.Thread(target=self.reload_cache)
                # thread.start()
                # util.handle_thread(thread)
                # print('reload_cache()-->')
                self.reload_cache()
                s = sublime.load_settings(setting.SFDC_CACHE_SETTINGS)
                project_meta_map = s.get(default_project)


            self.metadata = []
            self.metadata_view = []
            sel_key_str = self.menu[picked]

            # Search All
            if picked == 1:
                self.metadata = []
                self.metadata_view = []
                for key in range(2,9):
                    tmp = project_meta_map[self.menu[key]]
                    if tmp is not None:
                        self.metadata.extend(tmp)
                        for obj in tmp:
                            self.metadata_view.append(obj['name'])
                sublime.set_timeout(lambda:self.window.show_quick_panel(self.metadata_view, self.select_metadata), 10)

            # Custom Object Data 
            elif picked >= 2:
                self.metadata = project_meta_map[sel_key_str]
                for obj in project_meta_map[sel_key_str]:
                    self.metadata_view.append(obj['name'])
                sublime.set_timeout(lambda:self.window.show_quick_panel(self.metadata_view, self.select_metadata), 10)

    def select_metadata(self, picked):
        if 0 > picked < len(self.metadata):
            return

        if self.sf is None:
            self.sf = util.sf_login()

        sel_item = self.metadata[picked]
        # login_url = ('https://{instance}/{id}'
        #              .format(instance=self.sf.sf_instance,
        #                      id=sel_item['id']))
      
        returl = '/' + sel_item['id']
        login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                     .format(instance=self.sf.sf_instance,
                             sid=self.sf.session_id,
                             returl=returl))

        # print(login_url)
        util.open_in_default_browser(login_url)


    def reload_cache(self):
        # try:

            sel_type = {}
            sel_type[self.menu[2]] = ''
            sel_type[self.menu[3]] = '__c Custom SObject Setting'
            sel_type[self.menu[4]] = '.cls'
            sel_type[self.menu[5]] = '.trigger'
            sel_type[self.menu[6]] = '.page'
            sel_type[self.menu[7]] = '.component'
            sel_type[self.menu[8]] = '-EmailTemplate'
            sel_type[self.menu[9]] = '-StaticResource'
            # sel_type[self.menu[10]] = '-WorkflowRule'
            # sel_type[self.menu[11]] = '-ValidationRule'

            default_project = self.settings['default_project_value']['project_name']
            # print('default_project -->')
            # print(default_project)


            s = sublime.load_settings(setting.SFDC_CACHE_SETTINGS)
            project_meta_map = s.get(default_project)

            if project_meta_map is None:
                project_meta_map = {}
            
            for key in self.tooling_soql:
                soql = self.tooling_soql[key]
                params = {'q': soql}
                soql_result = {}

                # TODO
                try:
                   soql_result = self.sf.restful('tooling/query', params)
                   # print(soql_result)
                except Exception as e:
                    print('------>reload_cache Exception')
                    print(e)
                    pass
                
                # util.show_in_new_tab(soql_result)
                # table = util.search_soql_to_list(soql, soql_result)
                if soql_result['records'] is not None:
                    result = []
                    name_key = 'Name'
                    if self.menu[3] == key:
                        name_key = 'DeveloperName'
                    # TODO
                    # elif self.menu[10] == key:
                    #     name_key = 'FullName'
                    
                    for obj in soql_result['records']:
                        tmp = {}
                        tmp['id'] = obj['Id']
                        tmp['name'] = obj[name_key] + sel_type[key]
                        result.append(tmp)

                    project_meta_map[key] = result

            # "2. Custom Object Data"
            custom_obj_meta = []
            for x in self.sf.describe()["sobjects"]:
                if x["keyPrefix"] is not None:
                    tmp_map = {}
                    tmp_map['id'] = util.xstr(x["keyPrefix"])
                    tmp_map['name'] = (util.xstr(x["name"])+' : '+util.xstr(x["label"]) +' : '+ x["keyPrefix"])
                    custom_obj_meta.append(tmp_map)

                # stand sobject setting page
                if not x['custom']:
                    tmp_map = {}
                    tmp_map['id'] = 'p/setup/layout/LayoutFieldList?type=' + util.xstr(x["name"])
                    tmp_map['name'] = util.xstr(x["name"]) + ' ' + util.xstr(x["label"]) + ' Standard SObject Setting'
                    if project_meta_map[self.menu[3]] is None:
                        project_meta_map[self.menu[3]] = {}
                    project_meta_map[self.menu[3]].append(tmp_map)

            project_meta_map[self.menu[2]] = custom_obj_meta

            s.set(default_project, project_meta_map)

            sublime.save_settings(setting.SFDC_CACHE_SETTINGS)

        # except RequestException as e:
        #     util.show_in_panel("Network connection timeout when issuing REST GET request")
        #     return
        # except SalesforceExpiredSession as e:
        #     util.show_in_dialog('session expired')
        #     util.re_auth()
        #     return
        # except SalesforceRefusedRequest as e:
        #     util.show_in_panel('The request has been refused.')
        #     return
        # except SalesforceError as e:
        #     err = 'Error code: %s \nError message:%s' % (e.status,e.content)
        #     util.show_in_panel(err)
        #     return
        # except Exception as e:
        #     util.show_in_panel(e)
        #     # util.show_in_dialog('Exception Error!')
        #     return


# sfdc_object_desc
class SfdcObjectDescCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
                self.results.append(util.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):

        self.sftype = self.sf.get_sobject(self.picked_name)
        message = 'name, label, type, length, scale' + "\n"

        sftypedesc = self.sftype.describe()
        for field in sftypedesc["fields"]:
           # print(field["name"])  
           # print(field["label"])  
           # print(field["type"])  
           # print(field["length"])  
           # print(field["scale"])  
           message += util.xstr(field["name"]) + "," + util.xstr(field["label"]) \
                    + "," + util.xstr(field["type"]) + "," + util.xstr(field["length"]) + "," + util.xstr(field["scale"]) + "\n"
          
        # util.show_in_new_tab(message)
        file_name = self.picked_name + '_sobject_desc.csv'
        sub_folder = 'sobject-desc'
        util.save_and_open_in_panel(message, file_name, True, sub_folder )

# soql create
class SoqlCreateCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
                self.results.append(util.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)
        # print(self.picked_name)
        dirs = ["1. Custom Fields Only(Exclude Relation)", 
                "2. Updateable(Exclude Relation)", 
                "3. All Fields(Exclude Relation)",
                "4. Custom Fields Only(Include Relation)", 
                "5. Updateable(Include Relation)", 
                "6. All Fields(Include Relation)"]
        self.custom_result = dirs
         
        sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.select_panel), 10)

    def select_panel(self, picked):
        if 0 > picked < len(self.custom_result):
            return
        self.is_custom_only = ( picked == 0 or picked == 3 )
        self.is_updateable = ( picked == 1 or picked == 4)
        self.include_relationship = ( picked >= 3 )

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):
        try:
            # sobject = self.picked_name
            # fields = get_sobject_fields(self.sf, sobject)
            # fields_str = ",".join(fields)
            # soql = ("select %s from %s " % (fields_str, sobject))
            # util.show_in_new_tab(soql)
            
            sobject = self.picked_name
            sftype = self.sf.get_sobject(sobject)
            sftypedesc = sftype.describe()
            soql = codecreator.get_soql_src(sobject, sftypedesc["fields"],self.sf, condition='', has_comment=True, 
                                    is_custom_only=self.is_custom_only,
                                    updateable_only=self.is_updateable,
                                    include_relationship=self.include_relationship)
            util.show_in_new_tab(soql)
        except Exception as e:
            util.show_in_panel(e)
            return


# sfdc_object_desc
class CreateAllTestDataCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

    def main_handle(self):
        try:
            self.sf = util.sf_login()

            message = ''
            for x in self.sf.describe()["sobjects"]:
                if x["custom"]:
                    objectApiName = util.xstr(x["name"])
                    message += createTestDataStr(objectApiName=objectApiName, 
                                        sftype=self.sf.get_sobject(objectApiName), 
                                        isAllField=False)

            util.show_in_new_tab(message)
            
        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return


# sfdc_object_desc
class CreateTestDataNeedCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
                self.results.append(util.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):

        self.sftype = self.sf.get_sobject(self.picked_name)
        obj_name = util.get_obj_name(self.picked_name)
        message = createTestDataStr(objectApiName=self.picked_name, 
                                    sftype=self.sftype, 
                                    isAllField=False)
        util.insert_str(message)
         

class CreateTestDataFromSoqlCommand(sublime_plugin.TextCommand):
    def main_handle(self, sel_string = ''):
        try:
            sf = util.sf_login()

            soql_result = sf.query(sel_string)

            object_name = util.get_query_object_name(soql_result)

            if object_name:
                sftype = sf.get_sobject(object_name)
                sftypedesc = sftype.describe()
                fields = {}
                for field in sftypedesc["fields"]:
                    name = field['name'].lower()
                    fields[name] = field

                message = util.get_soql_to_apex(fields, sel_string, soql_result)
            else :
                # print(header)
                message = 'Query Error!\n'

            util.insert_str(message)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def run(self, edit):
        sel_area = self.view.sel()
        if sel_area[0].empty():
          util.show_in_dialog("Please select the SOQL !!")
          return
        else:
            sel_string = self.view.substr(sel_area[0])
            sel_string = util.del_comment(sel_string)

        thread = threading.Thread(target=self.main_handle, args=(sel_string, ))
        thread.start()
        util.handle_thread(thread)

# sfdc_object_desc
class CreateTestDataAllCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
                self.results.append(util.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):
        # print(self.picked_name)
        self.sftype = self.sf.get_sobject(self.picked_name)

        obj_name = util.get_obj_name(self.picked_name)
        message = createTestDataStr(objectApiName=self.picked_name, 
                                    sftype=self.sftype, 
                                    isAllField=True)
        # util.show_in_new_tab(message)
        util.insert_str(message)


def createTestDataStr(objectApiName, sftype, isAllField):
    obj_name = util.get_obj_name(objectApiName)
    message = ("List<{T}> {objName}List = new List<{T}>();\n"
                .format(T=objectApiName,
                        objName=obj_name))
    message += "for(Integer i=0; i<5; i++){\n"
    message += ("\t{T} {objName} = new {T}();\n"
                .format(T=objectApiName,
                        objName=obj_name))

    sftypedesc = sftype.describe()
    for field in sftypedesc["fields"]:
        # util.show_in_panel("defaultValue------->" + util.xstr(field["defaultValue"]))  
        # util.show_in_panel('\n')  
        # util.show_in_panel(field)
        # util.show_in_panel('\n')  
        # util.show_in_panel(field["name"])
        # util.show_in_panel('\n')  
        # util.show_in_panel(field["defaultValue"])
        # util.show_in_panel('\n')  
        # util.show_in_panel(field["defaultValue"] is None)  
        # util.show_in_panel('\n\n\n')  
        # print(field["name"])  
        # print(field["label"])  
        # print(field["type"])  
        # print(field["length"])  
        # print(field["scale"])  
        # print(field)  
        ## https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_calls_describesobjects_describesobjectresult.htm#topic-title
        ## obj type
        if isAllField:
            check = field["updateable"] and field["name"] != 'OwnerId'
        else:
            check = field["updateable"] \
                    and not field["nillable"] \
                    and field["name"] != 'OwnerId'\
                    and ( field["defaultValue"] is None ) \
                    and ( field["type"] != 'boolean' )

        if check:
        # if field["updateable"]:
           ## do with picklist
            picklistValues = []
            if field["type"] == 'picklist' or field["type"]== 'multipicklist':
               for pv in field['picklistValues']:
                  picklistValues.append(pv['value'])
               # print('------>')
               # print(field["name"])
               # print(picklistValues)
               # print(field['picklistValues'])
            
            if field["type"] == 'int' or field["type"] == 'double' or field["type"] == 'currency':
                length = field["length"] if field["length"] < 3 else 3
            else:
                length = field["length"] if field["length"] < 8 else 8
            val = util.random_data(data_type=field["type"],
                                  length=length,
                                  scale=field["scale"], 
                                  filed_name=field["name"], 
                                  picklistValues=picklistValues)
            message += ("\t{objName}.{field} = {value};    //{label}\n"
                 .format(objName=obj_name,
                         field=util.xstr(field["name"]),
                         value=val,
                         label=field["label"],))
    message += ("\t{objName}List.add({objName});\n"
                .format(T=objectApiName,
                        objName=obj_name))
    message += "}\n"
    message += ("insert {objName}List;\n\n"
                .format(objName=obj_name))
    return message


class CreateTestCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            file_name = self.view.file_name()
            if file_name is None:
                return
            check = os.path.isfile(file_name) and ( file_name.find(".cls") > -1 ) 
            if not check:
                util.show_in_dialog('Error file type! Please select a cls file.')
                return

            sel_string = self.view.substr(sublime.Region(0, self.view.size()))
            test_code,sfdc_name_map = codecreator.get_testclass(sel_string)
            # util.show_in_new_tab(test_code)
            
            is_open = True
            file_name = sfdc_name_map['test_class_file']
            sub_folder = AUTO_CODE_DIR
            save_path = util.save_and_open_in_panel(test_code, file_name, is_open, sub_folder )
            
        except Exception as e:
            util.show_in_panel(e)
            return

#Create VisualForce/Controller/DTO/DAO Code
class CreateSfdcCodeCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login()
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
                dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
                self.results.append(util.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            # util.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)
        dirs = ["1. Custom Fields Only(Exclude Validate)", 
                "2. All Fields(Exclude Validate)",
                "3. Custom Fields Only(Include Validate)", 
                "4. All Fields(Include Validate)"]
        self.custom_result = dirs
        
        sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.select_panel), 10)

    def select_panel(self, picked):
        if 0 > picked < len(self.custom_result):
            return
        self.is_custom_only = (picked==0 or picked==2)
        self.include_validate = (picked>1)

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):

        self.sftype = self.sf.get_sobject(self.picked_name)

        sftypedesc = self.sftype.describe()
          
        # util.show_in_new_tab(util.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only))


        sub_folder = AUTO_CODE_DIR
        sfdc_name_map = codecreator.get_sfdc_namespace(self.picked_name)

        is_open = False
        save_path_list = []

        # dto Code
        dto_code, class_name = codecreator.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['dto_file']
        save_path = util.save_and_open_in_panel(dto_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # dao Code
        dao_code = codecreator.get_dao_class(self.picked_name, sftypedesc["fields"], self.sf, self.is_custom_only)
        file_name = sfdc_name_map['dao_file']
        save_path = util.save_and_open_in_panel(dao_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # controller code
        controller_code, class_name = codecreator.get_controller_class(self.picked_name)
        file_name = sfdc_name_map['controller_file']
        save_path = util.save_and_open_in_panel(controller_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # visualforce code
        vf_code, class_name = codecreator.get_vf_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['vf_file']
        save_path = util.save_and_open_in_panel(vf_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # list controller code
        list_controller_code, class_name = codecreator.get_list_controller_class(self.picked_name)
        file_name = sfdc_name_map['list_controller_file']
        save_path = util.save_and_open_in_panel(list_controller_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # visualforce code
        list_vf_code, class_name = codecreator.get_list_vf_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['list_vf_file']
        save_path = util.save_and_open_in_panel(list_vf_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        # SfdcXyController
        src_code = codecreator.get_sfdcxycontroller()
        file_name = 'SfdcXyController.cls'
        save_path = util.save_and_open_in_panel(src_code, file_name, is_open, sub_folder )
        save_path_list.append(save_path)

        if sublime.ok_cancel_dialog('Create Source Over,Do you want to open the sources? '):
            for save_path in save_path_list:
                util.open_file(save_path)


class OpenControllerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        isExist = False
        if file_name and ( file_name.find(".page") > -1 ):
            # XyzPage.page -> XyzController.cls
            # Xyz.page -> XyzController.cls
            page_floder = util.get_slash() + "pages" + util.get_slash()
            class_floder = util.get_slash() + "classes" + util.get_slash()
            file_name1 = file_name.replace(page_floder, class_floder).replace('.page', 'Controller.cls')
            file_name2 = file_name.replace(page_floder, class_floder).replace('Page.page', 'Controller.cls')
            if os.path.isfile(file_name1): 
                self.view.window().open_file(file_name1)
                isExist = True
            elif os.path.isfile(file_name2): 
                self.view.window().open_file(file_name2)
                isExist = True
        elif file_name and ( file_name.find("Test.cls") > -1 ):
            # XyzControllerTest.cls -> XyzController.cls
            file_name1 = file_name.replace('Test.cls', '.cls')
            if os.path.isfile(file_name1): 
                self.view.window().open_file(file_name1)
                isExist = True

        if not isExist:
            util.show_in_panel('file not found!\n')


    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        check = os.path.isfile(file_name) and (( file_name.find(".page") > -1 ) or ( file_name.find("Test.cls") > -1 ))
        return check
        
    def is_visible(self):
        return self.is_enabled()

# Open Test Class
class OpenTestclassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        isExist = False

        if file_name:
            # XyzController.cls -> XyzControllerTest.cls
            file_name1 = file_name.replace('.cls', 'Test.cls')
            if os.path.isfile(file_name1): 
                self.view.window().open_file(file_name1)
                isExist = True

        if not isExist:
            util.show_in_panel('file not found!\n')

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        check = os.path.isfile(file_name) and ( file_name.find(".cls") > -1 ) and ( file_name.find("Test.cls") == -1 )
        return check

    def is_visible(self):
        return self.is_enabled()



class OpenVisualpageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        isExist = False

        if file_name:
            # XyzPage.page -> XyzController.cls
            # Xyz.page -> XyzController.cls
            page_floder = util.get_slash() + "pages" + util.get_slash()
            class_floder = util.get_slash() + "classes" + util.get_slash()
            file_name1 = file_name.replace(class_floder, page_floder).replace('Controller.cls', '.page')
            file_name2 = file_name.replace(class_floder, page_floder).replace('Controller.cls', 'Page.page')
            if os.path.isfile(file_name1): 
                self.view.window().open_file(file_name1)
                isExist = True
            elif os.path.isfile(file_name2): 
                self.view.window().open_file(file_name2)
                isExist = True

        if not isExist:
            util.show_in_panel('file not found!\n')

    def is_enabled(self):
        file_name = self.view.file_name()
        if file_name is None:
            return False
        check = os.path.isfile(file_name) and ( file_name.find(".cls") > -1 ) and ( file_name.find("Test.cls") == -1 )
        return check

    def is_visible(self):
        return self.is_enabled()


class CopyFilenameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        full_path = self.view.file_name()
        if full_path != None:
            str_list = full_path.split(util.get_slash())
            file_name = str(str_list[-1])
            sublime.set_clipboard(file_name)
            sublime.status_message("Copy File Name : %s " % file_name)


class ChangeAuthTypeCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            settings = setting.load()
            auth_type = settings["authentication"]
            self.dirs = [setting.AUTHENTICATION_OAUTH2, setting.AUTHENTICATION_PASSWORD, setting.AUTHENTICATION_MAVENSMATE]
            show_dirs = []
            for dirstr in self.dirs:
                if auth_type == dirstr:
                    show_dirs.append('[○]' + dirstr)
                else:
                    show_dirs.append('[X]' + dirstr)

            self.window.show_quick_panel(show_dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except Exception as e:
            util.show_in_panel(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.auth_type = self.dirs[picked]

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

    def main_handle(self):
        # print('self.auth_type-->')
        # print(self.auth_type)
        setting.update_authentication_setting(self.auth_type)


class SwitchBrowserCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.dirs = setting.get_browser_setting2()
            dirs = []
            for dir in self.dirs:
                dirs.append(dir[0])

            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except Exception as e:
            util.show_in_panel(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.browser = self.dirs[picked][0]
        self.broswer_name = self.dirs[picked][1]

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

    def main_handle(self):
        setting.update_default_browser(self.broswer_name)

class SwitchXyProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = setting.load()
        self.settings = settings
        projects = settings["projects"]
        default_project = settings["default_project"]
        dirs = []
        dirs_result = []
        for project_key in projects.keys():
            project_value = projects[project_key]

            if default_project == project_key:
                tmp = '[○]' + project_key
            else:
                tmp = '[X]' + project_key
            dirs.append(tmp)
            dirs_result.append(project_key)

        self.results = dirs_result
        window = sublime.active_window()
        window.show_quick_panel(dirs, self.panel_done,
            sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_project = self.results[picked]

        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)

    def main_handle(self):
        setting.update_default_project(self.picked_project)

        # if self.settings["use_oauth2"]:
        #     util.sf_oauth2()

        # TODO
        #　open project
        # current_project_dir = setting.mm_project_directory()
        # project = self.settings["projects"][self.picked_project]
        # workspace = project["workspace"]
        # project_file = self.picked_project + ".sublime-project"
        # project_file_path = os.path.join(workspace, project_file)
        # if os.path.normpath(current_project_dir) != os.path.normpath(workspace):
        #     print('--->open project')
        #     print(project_file_path)
        #     if os.path.isfile(project_file_path):
        #         util.subl(project_file_path)

    # def is_enabled(self):
    #     use_mavensmate_setting = self.settings["use_mavensmate_setting"]
    #     return (not use_mavensmate_setting)

    # def is_visible(self):
    #     return self.is_enabled()


class AboutHxyCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        version_info = sublime.load_settings("sfdc.version.sublime-settings")

        version_msg = "%s v%s\n\n%s\n\nCopyright © 2016-2017 By %s\n\nEmail: %s\nHomePage: %s\n" % (
            version_info.get("name"),
            version_info.get("version"),
            version_info.get("description"),
            version_info.get("author"),
            version_info.get("email"),
            version_info.get("homepage")
        )
        util.show_in_dialog(version_msg)


class ReportIssueXyCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        version_info = sublime.load_settings("sfdc.version.sublime-settings")
        util.open_in_default_browser(version_info.get("issue"))


class HomePageCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        version_info = sublime.load_settings("sfdc.version.sublime-settings")
        util.open_in_default_browser(version_info.get("homepage"))




##########################################################################################
#Main Util
##########################################################################################
# salesforce_instance is Salesforce instance from simple-salesforce
def login_sf_home(self, salesforce_instance, browser='default', broswer_path=''):
        try:
            sf = salesforce_instance
            sfdesc = sf.describe()
             
            returl = '/home/home.jsp'
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                         .format(instance=sf.sf_instance,
                                 sid=sf.session_id,
                                 returl=returl))
            if browser == 'default':
                util.open_in_default_browser(login_url)
            else:
                util.open_in_browser(login_url,browser,broswer_path)


        except RequestException as e:
            util.show_in_panel("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            util.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            util.show_in_panel('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            util.show_in_panel(err)
            return
        except Exception as e:
            util.show_in_panel(e)
            return

# format soql ,
# format 'select * from Sojbect' -> add all field 
def soql_format(sf_instance,soql_str):
    import re

    soql = util.del_comment(soql_str)
    match = re.match("select\s+\*\s+from[\s\t]+(\w+)([\t\s\S]*)", soql, re.I|re.M)
    if match:
        sobject = match.group(1)
        condition = match.group(2)
        fields = get_sobject_fields(sf_instance, sobject)
        fields_str = ','.join(fields)
        soql = ("select %s from %s %s" % (fields_str, sobject, condition))
    
    return soql


# get all fields from sobject
def get_sobject_fields(sf_instance, sobject):
    fields = []
    sftype = sf_instance.get_sobject(sobject)
    sftypedesc = sftype.describe()
    for field in sftypedesc["fields"]:
        fields.append(util.xstr(field["name"]))
    return fields




##########################################################################################
#Deprecated Or Delete
##########################################################################################
# # Save the SFDC Object As Excel
# # use xlwt to write excel,deprecated 
# class SaveSfdcObjectAsExcelCommand(sublime_plugin.WindowCommand):
#     def main_handle(self, savePath = ''):
#         try:
#             dirPath = os.path.dirname(savePath)
#             util.makedir(dirPath)

#             sf = util.sf_login()
#             # contact = sf.query("SELECT Id, Email FROM Contact limit 1")

#             sfdesc = sf.describe()
#             book = xlwt.Workbook()
#             newSheet_1 = book.add_sheet('オブジェクトリスト')
#             newSheet_1.write(0, 0, 'label')
#             newSheet_1.write(0, 1, 'name')
#             newSheet_1.write(0, 2, 'keyPrefix')
#             index = 1;
#             sheetIndex = 0;

#             for x in sf.describe()["sobjects"]:
#               #write to xls
#               book.get_sheet(0)
#               newSheet_1.write(index, 0, util.xstr(x["label"]))
#               newSheet_1.write(index, 1, util.xstr(x["name"]))
#               newSheet_1.write(index, 2, util.xstr(x["keyPrefix"]))
#               index = index + 1
#               #print(sf.Kind__c.describe())
#               #print(x["name"])
#               #print(x["custom"])
#               if x["custom"]:
#                   sheetIndex += 1
                  
#                   # sftype = SFType(util.xstr(x["name"]), sf.session_id, sf.sf_instance, sf_version=sf.sf_version,
#                   #               proxies=sf.proxies, session=sf.session)
#                   sftype = sf.get_sobject(util.xstr(x["name"]))

#                   #print(x["name"])     
#                   #write to xls
#                   fieldSheet_1 = book.add_sheet(x["name"])
#                   book.get_sheet(sheetIndex)
#                   rowIndex = 0;
#                   fieldSheet_1.write(rowIndex, 0, "name")
#                   fieldSheet_1.write(rowIndex, 1, "label")
#                   fieldSheet_1.write(rowIndex, 2, "type")
#                   fieldSheet_1.write(rowIndex, 3, "length")
#                   fieldSheet_1.write(rowIndex, 4, "scale")

#                   sftypedesc = sftype.describe()
#                   for field in sftypedesc["fields"]:
#                      #print(field["name"])  
#                      #print(field["label"])  
#                      #print(field["type"])  
#                      #print(field["length"])  
#                      #print(field["scale"])  
#                      rowIndex += 1
#                      fieldSheet_1.write(rowIndex, 0, field["name"])
#                      fieldSheet_1.write(rowIndex, 1, field["label"])
#                      fieldSheet_1.write(rowIndex, 2, field["type"])
#                      fieldSheet_1.write(rowIndex, 3, field["length"])
#                      fieldSheet_1.write(rowIndex, 4, field["scale"])

#               #message += x["label"] + "\n"

#             # book.save( settings["default_project"] + '_sobject.xls')
#             book.save(savePath)
#             util.show_in_dialog("Done! Please see the dir below: \n" + dirPath)
#             # isOpen = sublime.ok_cancel_dialog('Do you want to open the directory?')
#             # if isOpen:



#         except RequestException as e:
#             util.show_in_panel("Network connection timeout when issuing REST GET request")
#             return
#         except SalesforceExpiredSession as e:
#             util.show_in_dialog('session expired')
#             return
#         except SalesforceRefusedRequest as e:
#             util.show_in_panel('The request has been refused.')
#             return
#         except SalesforceError as e:
#             err = 'Error code: %s \nError message:%s' % (e.status,e.content)
#             util.show_in_panel(err)
#             return
#         except Exception as e:
#             util.show_in_panel(e)
#             # util.show_in_dialog('Exception Error!')
#             return

#     def on_input(self, args):
#         thread = threading.Thread(target=self.main_handle, args=(args, ))
#         thread.start()
#         util.handle_thread(thread)


#     def run(self):
#         settings = setting.load()
#         self.fullPath =  os.path.join(util.get_default_floder(), settings["default_project"] + '_sobject.xls')
#         # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
#         self.window.show_input_panel("Please Input FullPath of fileName: " , 
#             self.fullPath, self.on_input, None, None)

# class CreateDtoCodeCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         try:
#             self.sf = util.sf_login()
#             dirs = []
#             self.results = []

#             for x in self.sf.describe()["sobjects"]:
#                 # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
#                 dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
#                 self.results.append(util.xstr(x["name"]))
#                 # print(x)
#             self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

#         except RequestException as e:
#             util.show_in_panel("Network connection timeout when issuing REST GET request")
#             return
#         except SalesforceExpiredSession as e:
#             util.show_in_dialog('session expired')
#             return
#         except SalesforceRefusedRequest as e:
#             util.show_in_panel('The request has been refused.')
#             return
#         except SalesforceError as e:
#             err = 'Error code: %s \nError message:%s' % (e.status,e.content)
#             util.show_in_panel(err)
#             return
#         except Exception as e:
#             util.show_in_panel(e)
#             # util.show_in_dialog('Exception Error!')
#             return

#     def panel_done(self, picked):
#         if 0 > picked < len(self.results):
#             return
#         self.picked_name = self.results[picked]
#         # print(self.picked_name)
#         dirs = ["Custom Fields Only-Exclude Validate", "All Fields-Exclude Validate",
#                 "Custom Fields Only-Include Validate",  "All Fields-Include Validate"]
#         self.custom_result = [1, 2, 3, 4]
        
#         sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.select_panel), 10)

#     def select_panel(self, picked):
#         if 0 > picked < len(self.custom_result):
#             return
#         self.is_custom_only = (self.custom_result[picked]==1 or self.custom_result[picked]==3)
#         self.include_validate = (self.custom_result[picked]>2)

#         thread = threading.Thread(target=self.main_handle)
#         thread.start()
#         util.handle_thread(thread)


#     def main_handle(self):

#         self.sftype = self.sf.get_sobject(self.picked_name)

#         sftypedesc = self.sftype.describe()
          
#         # util.show_in_new_tab(util.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only))

#         dto_class, class_name = util.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
#         file_name = class_name + 'Dto.cls'
#         sub_folder = AUTO_CODE_DIR
#         util.save_and_open_in_panel(dto_class, file_name, sub_folder )

# class CreateVfCodeCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         try:
#             self.sf = util.sf_login()
#             dirs = []
#             self.results = []

#             for x in self.sf.describe()["sobjects"]:
#                 # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
#                 dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
#                 self.results.append(util.xstr(x["name"]))
#                 # print(x)
#             self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

#         except RequestException as e:
#             util.show_in_panel("Network connection timeout when issuing REST GET request")
#             return
#         except SalesforceExpiredSession as e:
#             util.show_in_dialog('session expired')
#             return
#         except SalesforceRefusedRequest as e:
#             util.show_in_panel('The request has been refused.')
#             return
#         except SalesforceError as e:
#             err = 'Error code: %s \nError message:%s' % (e.status,e.content)
#             util.show_in_panel(err)
#             return
#         except Exception as e:
#             util.show_in_panel(e)
#             # util.show_in_dialog('Exception Error!')
#             return

#     def panel_done(self, picked):
#         if 0 > picked < len(self.results):
#             return
#         self.picked_name = self.results[picked]
#         # print(self.picked_name)
#         dirs = ["Custom Fields Only", "All Fields"]
#         self.custom_result = [1, 2]
        
#         sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.select_panel), 10)

#     def select_panel(self, picked):
#         if 0 > picked < len(self.custom_result):
#             return
#         self.is_custom_only = (self.custom_result[picked]==1 )

#         thread = threading.Thread(target=self.main_handle)
#         thread.start()
#         util.handle_thread(thread)


#     def main_handle(self):

#         self.sftype = self.sf.get_sobject(self.picked_name)

#         sftypedesc = self.sftype.describe()
          
#         # util.show_in_new_tab(util.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only))

#         source_code, class_name = util.get_vf_class(self.picked_name, sftypedesc["fields"], self.is_custom_only)
#         file_name = class_name + '.page'
#         sub_folder = AUTO_CODE_DIR
#         util.save_and_open_in_panel(source_code, file_name, sub_folder )


# class CreateDaoCodeCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         try:
#             self.sf = util.sf_login()
#             dirs = []
#             self.results = []

#             for x in self.sf.describe()["sobjects"]:
#                 # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
#                 dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
#                 self.results.append(util.xstr(x["name"]))
#                 # print(x)
#             self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

#         except RequestException as e:
#             util.show_in_panel("Network connection timeout when issuing REST GET request")
#             return
#         except SalesforceExpiredSession as e:
#             util.show_in_dialog('session expired')
#             return
#         except SalesforceRefusedRequest as e:
#             util.show_in_panel('The request has been refused.')
#             return
#         except SalesforceError as e:
#             err = 'Error code: %s \nError message:%s' % (e.status,e.content)
#             util.show_in_panel(err)
#             return
#         except Exception as e:
#             util.show_in_panel(e)
#             # util.show_in_dialog('Exception Error!')
#             return

#     def panel_done(self, picked):
#         if 0 > picked < len(self.results):
#             return
#         self.picked_name = self.results[picked]
#         # print(self.picked_name)
#         dirs = ["Custom Fields Only", "All Fields"]
#         self.custom_result = [True, False]
        
#         sublime.set_timeout(lambda:self.window.show_quick_panel(dirs, self.select_panel), 10)

#     def select_panel(self, picked):
#         if 0 > picked < len(self.custom_result):
#             return
#         self.is_custom_only = self.custom_result[picked]    

#         thread = threading.Thread(target=self.main_handle)
#         thread.start()
#         util.handle_thread(thread)


#     def main_handle(self):

#         self.sftype = self.sf.get_sobject(self.picked_name)

#         sftypedesc = self.sftype.describe()
          
#         util.show_in_new_tab(util.get_dao_class(self.picked_name, sftypedesc["fields"], self.is_custom_only))


# class CreateControllerCodeCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         try:
#             self.sf = util.sf_login()
#             dirs = []
#             self.results = []

#             for x in self.sf.describe()["sobjects"]:
#                 # dirs.append([util.xstr(x["name"]), util.xstr(x["label"])])
#                 dirs.append(util.xstr(x["name"])+' : '+util.xstr(x["label"]))
#                 self.results.append(util.xstr(x["name"]))
#                 # print(x)
#             self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

#         except RequestException as e:
#             util.show_in_panel("Network connection timeout when issuing REST GET request")
#             return
#         except SalesforceExpiredSession as e:
#             util.show_in_dialog('session expired')
#             return
#         except SalesforceRefusedRequest as e:
#             util.show_in_panel('The request has been refused.')
#             return
#         except SalesforceError as e:
#             err = 'Error code: %s \nError message:%s' % (e.status,e.content)
#             util.show_in_panel(err)
#             return
#         except Exception as e:
#             util.show_in_panel(e)
#             # util.show_in_dialog('Exception Error!')
#             return

#     def panel_done(self, picked):
#         if 0 > picked < len(self.results):
#             return
#         self.picked_name = self.results[picked]

#         source_code, class_name = util.get_controller_class(self.picked_name)
#         file_name = class_name + 'Controller.cls'
#         sub_folder = AUTO_CODE_DIR
#         util.save_and_open_in_panel(source_code, file_name, sub_folder )
