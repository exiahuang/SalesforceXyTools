import sublime
import sublime_plugin
import os
from . import baseutil
from . import util
from .baseutil import SysIo
from . import codecreator
from . import setting
from .setting import SfBasicConfig
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
from .salesforce.core import ToolingApi, MetadataApi
from .uiutil import SublConsole



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
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        try:
            sf = util.sf_login(self.sf_basic_config)
            message = 'label, name, keyPrefix' + "\n"
            for x in sf.describe()["sobjects"]:
              message += baseutil.xstr(x["label"]) + "," + baseutil.xstr(x["name"]) + "," + baseutil.xstr(x["keyPrefix"]) + "\n"

            # self.sublconsole.show_in_new_tab(message)
            file_name = sf.settings["default_project"] + '_sobject_lst.csv'
            save_dir = self.sf_basic_config.get_work_dir()
            self.sublconsole.debug('file_name:' + file_name)
            
            self.sublconsole.save_and_open_in_panel(message, save_dir, file_name, True )

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return    

# Save the SFDC Object As Excel
# # use xlsxwriter to write excel
class SaveSfdcObjectAsExcelCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        self.dirs = ['Custom Sobject','Standard Sobject','All Sobject']
        self.window.show_quick_panel(self.dirs, self.panel_done,sublime.MONOSPACE_FONT)

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        sel_type = self.dirs[picked]
        self.is_custom_sobject = sel_type == 'Custom Sobject'
        self.is_standard_sobject = sel_type == 'Standard Sobject'
        self.is_all_sobject = sel_type == 'All Sobject'
        settings = self.settings
        
        if self.is_all_sobject :
            self.fullPath =  os.path.join(self.sf_basic_config.get_work_dir(), settings["default_project"] + '_all_sobject.xlsx')
        elif self.is_custom_sobject:
            self.fullPath =  os.path.join(self.sf_basic_config.get_work_dir(), settings["default_project"] + '_custom_sobject.xlsx')
        elif self.is_standard_sobject:
            self.fullPath =  os.path.join(self.sf_basic_config.get_work_dir(), settings["default_project"] + '_standard_sobject.xlsx')
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel("Please Input FullPath of fileName: " , 
            self.fullPath, self.on_input, None, None)

        self.sublconsole.thread_run(target=self.on_input)

    def on_input(self, args):
        self.sublconsole.thread_run(target=self.main_handle, args=(args, ))

    def main_handle(self, savePath = ''):
        try:
            self.sublconsole.showlog('save path : ' + savePath)
            dirPath = os.path.dirname(savePath)
            baseutil.makedir(dirPath)

            sf = util.sf_login(self.sf_basic_config)
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
              newSheet_1.write(index, 0, baseutil.xstr(x["label"]))
              newSheet_1.write(index, 1, baseutil.xstr(x["name"]))
              newSheet_1.write(index, 2, baseutil.xstr(x["keyPrefix"]))
              index = index + 1
              #print(sf.Kind__c.describe())
              #print(x["name"])
              #print(x["custom"])
              if self.is_all_sobject or (x["custom"] and self.is_custom_sobject) or ( not x["custom"] and self.is_standard_sobject):
                  sheetIndex += 1
                  
                  # sftype = SFType(baseutil.xstr(x["name"]), sf.session_id, sf.sf_instance, sf_version=sf.sf_version,
                  #               proxies=sf.proxies, session=sf.session)
                  sftype = sf.get_sobject(baseutil.xstr(x["name"]))

                  #print(x["name"])     
                  #write to xls
                  worksheet_name = baseutil.get_excel_sheet_name(x["label"])
                  if worksheet_name in sheetNameList:
                    worksheet_name = (x["label"])[0:25] + "_" + baseutil.random_str(4)
                  
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
                     #print(field)  
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
                                if 'label' in pv and 'value' in pv:
                                    picklistValuesStr += str(pv['label']) + ':' + str(pv['value']) + '\n'
                            fieldSheet_1.write(rowIndex, headerIndex, picklistValuesStr)
                        else:
                            fieldSheet_1.write(rowIndex, headerIndex, baseutil.xstr(field[header]))
                        headerIndex = headerIndex + 1

              #message += x["label"] + "\n"

            # book.save( settings["default_project"] + '_sobject.xls')
            self.sublconsole.show_in_dialog("Done! Please see the dir below: \n" + dirPath)
            # isOpen = sublime.ok_cancel_dialog('Do you want to open the directory?')
            # if isOpen:


        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return




# Soql Query
class SoqlQueryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        sel_area = self.view.sel()
        if sel_area[0].empty():
          self.sublconsole.show_in_dialog("Please select the SOQL !!")
          return
        else:
            soql_string = self.view.substr(sel_area[0])
            soql_string = baseutil.del_comment(soql_string)

        # TODO
        # sobject_name = baseutil.get_soql_sobject(soql_string)
        # if not sobject_name:
        #     self.sublconsole.show_in_dialog("Please select SOQL !")
        #     return

        self.sublconsole.thread_run(target=self.main_handle, args=(soql_string, ))

    def main_handle(self, sel_string = ''):
        try:
            sf = util.sf_login(self.sf_basic_config)

            soql_str = soql_format(sf,sel_string)

            self.sublconsole.debug('------>soql')
            self.sublconsole.debug(soql_str)
            
            soql_result = sf.query(soql_str)
            self.sublconsole.debug('----->soql_result')  
            self.sublconsole.debug(soql_result)  


            # header = [key for key in soql_result['records'].iterkeys()]
            # print(header)
            message = baseutil.get_soql_result(soql_str, soql_result)

            self.sublconsole.show_in_new_tab(message)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            return


# ToolingQueryCommand
class ToolingQueryCommand(sublime_plugin.TextCommand):
    def main_handle(self, sel_string = ''):
        try:
            # print("ToolingQueryCommand Start")

            sf = util.sf_login(self.sf_basic_config)
            
            params = {'q': sel_string}
            soql_result = sf.restful('tooling/query', params)
            # header = [key for key in soql_result['records'].iterkeys()]
            # print(header)
            message = baseutil.get_soql_result(sel_string, soql_result)

            self.sublconsole.show_in_new_tab(message)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return

    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        sel_area = self.view.sel()
        if sel_area[0].empty():
          self.sublconsole.show_in_dialog("Please select the Tooling SOQL !!")
          return
        else:            
            sel_string = self.view.substr(sel_area[0])
            sel_string = baseutil.del_comment(sel_string)

        self.sublconsole.thread_run(target=self.main_handle, args=(sel_string, ))

# RunApexScript
class RunApexScriptCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)

        sel_area = self.view.sel()
        if sel_area[0].empty():
          self.sublconsole.show_in_dialog("Please select the Tooling SOQL !!")
          return
        else:
            sel_string = self.view.substr(sel_area[0])
            sel_string = baseutil.del_comment(sel_string)
        self.sublconsole.thread_run(target=self.main_handle, args=(sel_string, ))

    def main_handle(self, sel_string = ''):
        try:
            sel_area = self.view.sel()
            sf = util.sf_login(self.sf_basic_config)
            settings = self.sf_basic_config.get_setting()
            debug_levels = settings['debug_levels']
            result = sf.execute_anonymous(sel_string, debug_levels)
            # print(result)
            self.sublconsole.show_in_new_tab(result["debugLog"])
             
        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return


# Login Salesforce
class LoginSfdcCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.dirs = self.sf_basic_config.get_browser_setting()
            dirs = []
            for dir in self.dirs:
                dirs.append(dir[0])

            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.browser = self.dirs[picked][0]
        self.broswer_path = self.dirs[picked][1]

        self.sublconsole.thread_run(target=self.main_handle)


    def main_handle(self):
        try:
            sf = util.sf_login(self.sf_basic_config)
            login_sf_home(self, self.sf_basic_config,sf, self.browser, self.broswer_path)
        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            return


# sfdc_dataviewer
class SfdcDataviewerCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.sf = util.sf_login(self.sf_basic_config)

            dirs = []
            self.results = []
            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]) +' : Export to Tab ')
                self.results.append(baseutil.xstr(x["name"]))
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        self.sftype = self.sf.get_sobject(self.picked_name)

        soql = 'SELECT '
        fields = []

        sftypedesc = self.sftype.describe()
        for field in sftypedesc["fields"]:
            fields.append(baseutil.xstr(field["name"]))
        soql += ' , '.join(fields)
        soql += ' FROM ' + self.picked_name
        if 'soql_select_limit' in self.settings:
            soql += ' LIMIT ' + baseutil.xstr(self.settings["soql_select_limit"])

        message = 'soql : ' + soql + '\n\n\n\n'

        soql_result = self.sf.query(soql)
        message += baseutil.get_soql_result(soql, soql_result)

        self.sublconsole.show_in_new_tab(message)





# sfdc_object_desc
class SfdcObjectDescCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.sf = util.sf_login(self.sf_basic_config)
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]))
                self.results.append(baseutil.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        self.sublconsole.thread_run(target=self.main_handle)


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
           message += baseutil.xstr(field["name"]) + "," + baseutil.xstr(field["label"]) \
                    + "," + baseutil.xstr(field["type"]) + "," + baseutil.xstr(field["length"]) + "," + baseutil.xstr(field["scale"]) + "\n"
          
        # self.sublconsole.show_in_new_tab(message)
        file_name = self.picked_name + '_sobject_desc.csv'
        sub_folder = 'sobject-desc'
        save_dir = os.path.join(self.sf_basic_config.get_work_dir(), sub_folder)
        self.sublconsole.save_and_open_in_panel(message, save_dir, file_name, True)

# soql create
class SoqlCreateCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.sf = util.sf_login(self.sf_basic_config)
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]))
                self.results.append(baseutil.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
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

        self.sublconsole.thread_run(target=self.main_handle)


    def main_handle(self):
        try:
            # sobject = self.picked_name
            # fields = get_sobject_fields(self.sf, sobject)
            # fields_str = ",".join(fields)
            # soql = ("select %s from %s " % (fields_str, sobject))
            # self.sublconsole.show_in_new_tab(soql)
            
            sobject = self.picked_name
            sftype = self.sf.get_sobject(sobject)
            sftypedesc = sftype.describe()
            soql = codecreator.get_soql_src(sobject, sftypedesc["fields"],self.sf, condition='', has_comment=True, 
                                    is_custom_only=self.is_custom_only,
                                    updateable_only=self.is_updateable,
                                    include_relationship=self.include_relationship)
            self.sublconsole.show_in_new_tab(soql)
        except Exception as e:
            self.sublconsole.showlog(e)
            return


# sfdc_object_desc
class CreateAllTestDataCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.sf = util.sf_login(self.sf_basic_config)

            message = ''
            for x in self.sf.describe()["sobjects"]:
                if x["custom"]:
                    objectApiName = baseutil.xstr(x["name"])
                    message += createTestDataStr(objectApiName=objectApiName, 
                                        sftype=self.sf.get_sobject(objectApiName), 
                                        isAllField=False)

            self.sublconsole.show_in_new_tab(message)
            
        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return


# sfdc_object_desc
class CreateTestDataNeedCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.sf = util.sf_login(self.sf_basic_config)
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]))
                self.results.append(baseutil.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]
        # print(self.picked_name)

        self.sublconsole.thread_run(target=self.main_handle)


    def main_handle(self):

        self.sftype = self.sf.get_sobject(self.picked_name)
        obj_name = baseutil.get_obj_name(self.picked_name)
        message = createTestDataStr(objectApiName=self.picked_name, 
                                    sftype=self.sftype, 
                                    isAllField=False)
        self.sublconsole.insert_str(message)
         

class CreateTestDataFromSoqlCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.sf_basic_config = SfBasicConfig()
        self.settings = self.sf_basic_config.get_setting()
        self.sublconsole = SublConsole(self.sf_basic_config)
        
        sel_area = self.view.sel()
        if sel_area[0].empty():
          self.sublconsole.show_in_dialog("Please select the SOQL !!")
          return
        else:
            sel_string = self.view.substr(sel_area[0])
            sel_string = baseutil.del_comment(sel_string)

        self.sublconsole.thread_run(target=self.main_handle, args=(sel_string, ))

    def main_handle(self, sel_string = ''):
        try:

            sf = util.sf_login(self.sf_basic_config)

            soql_result = sf.query(sel_string)

            object_name = baseutil.get_query_object_name(soql_result)

            if object_name:
                sftype = sf.get_sobject(object_name)
                sftypedesc = sftype.describe()
                fields = {}
                for field in sftypedesc["fields"]:
                    name = field['name'].lower()
                    fields[name] = field

                message = baseutil.get_soql_to_apex(fields, sel_string, soql_result)
            else :
                # print(header)
                message = 'Query Error!\n'

            self.sublconsole.insert_str(message)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return


# sfdc_object_desc
class CreateTestDataAllCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.sf = util.sf_login(self.sf_basic_config)
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]))
                self.results.append(baseutil.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.results):
            return
        self.picked_name = self.results[picked]

        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        # print(self.picked_name)
        self.sftype = self.sf.get_sobject(self.picked_name)

        obj_name = baseutil.get_obj_name(self.picked_name)
        message = createTestDataStr(objectApiName=self.picked_name, 
                                    sftype=self.sftype, 
                                    isAllField=True)
        # self.sublconsole.show_in_new_tab(message)
        self.sublconsole.insert_str(message)


def createTestDataStr(objectApiName, sftype, isAllField):
    obj_name = baseutil.get_obj_name(objectApiName)
    message = ("List<{T}> {objName}List = new List<{T}>();\n"
                .format(T=objectApiName,
                        objName=obj_name))
    message += "for(Integer i=0; i<5; i++){\n"
    message += ("\t{T} {objName} = new {T}();\n"
                .format(T=objectApiName,
                        objName=obj_name))

    sftypedesc = sftype.describe()
    for field in sftypedesc["fields"]:
        # self.sublconsole.showlog("defaultValue------->" + baseutil.xstr(field["defaultValue"]))  
        # self.sublconsole.showlog('\n')  
        # self.sublconsole.showlog(field)
        # self.sublconsole.showlog('\n')  
        # self.sublconsole.showlog(field["name"])
        # self.sublconsole.showlog('\n')  
        # self.sublconsole.showlog(field["defaultValue"])
        # self.sublconsole.showlog('\n')  
        # self.sublconsole.showlog(field["defaultValue"] is None)  
        # self.sublconsole.showlog('\n\n\n')  
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
            val = baseutil.random_data(data_type=field["type"],
                                  length=length,
                                  scale=field["scale"], 
                                  filed_name=field["name"], 
                                  picklistValues=picklistValues)
            message += ("\t{objName}.{field} = {value};    //{label}\n"
                 .format(objName=obj_name,
                         field=baseutil.xstr(field["name"]),
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
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            file_name = self.view.file_name()
            if file_name is None:
                return
            check = os.path.isfile(file_name) and ( file_name.find(".cls") > -1 ) 
            if not check:
                self.sublconsole.show_in_dialog('Error file type! Please select a cls file.')
                return

            sel_string = self.view.substr(sublime.Region(0, self.view.size()))
            test_code,sfdc_name_map = codecreator.get_testclass(sel_string)
            # self.sublconsole.show_in_new_tab(test_code)
            
            is_open = True
            file_name = sfdc_name_map['test_class_file']
            save_dir = os.path.join(self.sf_basic_config.get_sfdc_module_dir(), "code-creator-test", "src", "classes")
            self.sublconsole.save_and_open_in_panel(test_code, save_dir, file_name, is_open)
            
        except Exception as e:
            self.sublconsole.showlog(e)
            return

#Create VisualForce/Controller/DTO/DAO Code
class CreateSfdcCodeCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            self.sf = util.sf_login(self.sf_basic_config)
            dirs = []
            self.results = []

            for x in self.sf.describe()["sobjects"]:
                # dirs.append([baseutil.xstr(x["name"]), baseutil.xstr(x["label"])])
                dirs.append(baseutil.xstr(x["name"])+' : '+baseutil.xstr(x["label"]))
                self.results.append(baseutil.xstr(x["name"]))
                # print(x)
            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            # self.sublconsole.show_in_dialog('Exception Error!')
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

        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):

        self.sftype = self.sf.get_sobject(self.picked_name)

        sftypedesc = self.sftype.describe()
          
        # self.sublconsole.show_in_new_tab(util.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only))

        save_dir = self.sf_basic_config.get_sfdc_module_dir()
        classes_dir = os.path.join(self.sf_basic_config.get_sfdc_module_dir(), "code-creator", "src", "classes")
        pages_dir = os.path.join(self.sf_basic_config.get_sfdc_module_dir(), "code-creator", "src", "pages")
        sfdc_name_map = codecreator.get_sfdc_namespace(self.picked_name)

        is_open = False
        save_path_list = []

        # dto Code
        self.sublconsole.showlog('start to build dto')
        dto_code, class_name = codecreator.get_dto_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['dto_file']        
        save_path = self.sublconsole.save_and_open_in_panel(dto_code, classes_dir, file_name, is_open)
        save_path_list.append(save_path)

        # dao Code
        self.sublconsole.showlog('start to build dao')
        dao_code = codecreator.get_dao_class(self.picked_name, sftypedesc["fields"], self.sf, self.is_custom_only)
        file_name = sfdc_name_map['dao_file']
        save_path = self.sublconsole.save_and_open_in_panel(dao_code, classes_dir, file_name, is_open)
        save_path_list.append(save_path)

        # controller code
        self.sublconsole.showlog('start to build controller')
        controller_code, class_name = codecreator.get_controller_class(self.picked_name)
        file_name = sfdc_name_map['controller_file']
        save_path = self.sublconsole.save_and_open_in_panel(controller_code, classes_dir, file_name, is_open)
        save_path_list.append(save_path)

        # visualforce code
        self.sublconsole.showlog('start to build visualforce')
        vf_code, class_name = codecreator.get_vf_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['vf_file']
        save_path = self.sublconsole.save_and_open_in_panel(vf_code, pages_dir, file_name, is_open)
        save_path_list.append(save_path)

        # list controller code
        self.sublconsole.showlog('start to build list controller')
        list_controller_code, class_name = codecreator.get_list_controller_class(self.picked_name)
        file_name = sfdc_name_map['list_controller_file']
        save_path = self.sublconsole.save_and_open_in_panel(list_controller_code, classes_dir, file_name, is_open)
        save_path_list.append(save_path)

        # visualforce code
        self.sublconsole.showlog('start to build list visualforce')
        list_vf_code, class_name = codecreator.get_list_vf_class(self.picked_name, sftypedesc["fields"], self.is_custom_only, self.include_validate)
        file_name = sfdc_name_map['list_vf_file']
        save_path = self.sublconsole.save_and_open_in_panel(list_vf_code, pages_dir, file_name, is_open)
        save_path_list.append(save_path)

        # SfdcXyController
        self.sublconsole.showlog('start to build SfdcXyController')
        src_code = codecreator.get_sfdcxycontroller()
        file_name = 'SfdcXyController.cls'
        save_path = self.sublconsole.save_and_open_in_panel(src_code, classes_dir, file_name, is_open)
        save_path_list.append(save_path)

        if sublime.ok_cancel_dialog('Create Source Over,Do you want to open the sources? '):
            for save_path in save_path_list:
                self.sublconsole.open_file(save_path)
                


class OpenControllerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        isExist = False
        if file_name and ( file_name.find(".page") > -1 ):
            # XyzPage.page -> XyzController.cls
            # Xyz.page -> XyzController.cls
            page_folder = baseutil.get_slash() + "pages" + baseutil.get_slash()
            class_folder = baseutil.get_slash() + "classes" + baseutil.get_slash()
            file_name1 = file_name.replace(page_folder, class_folder).replace('.page', 'Controller.cls')
            file_name2 = file_name.replace(page_folder, class_folder).replace('Page.page', 'Controller.cls')
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
            self.sublconsole.showlog('file not found!\n')


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
            self.sublconsole.showlog('file not found!\n')

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
            page_folder = baseutil.get_slash() + "pages" + baseutil.get_slash()
            class_folder = baseutil.get_slash() + "classes" + baseutil.get_slash()
            file_name1 = file_name.replace(class_folder, page_folder).replace('Controller.cls', '.page')
            file_name2 = file_name.replace(class_folder, page_folder).replace('Controller.cls', 'Page.page')
            if os.path.isfile(file_name1): 
                self.view.window().open_file(file_name1)
                isExist = True
            elif os.path.isfile(file_name2): 
                self.view.window().open_file(file_name2)
                isExist = True

        if not isExist:
            self.sublconsole.showlog('file not found!\n')

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
            str_list = full_path.split(baseutil.get_slash())
            file_name = str(str_list[-1])
            sublime.set_clipboard(file_name)
            sublime.status_message("Copy File Name : %s " % file_name)


class ChangeAuthTypeCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)
            settings = self.settings
            auth_type = settings["authentication"]
            self.dirs = [setting.AUTHENTICATION_OAUTH2, setting.AUTHENTICATION_PASSWORD]
            show_dirs = []
            for dirstr in self.dirs:
                if auth_type == dirstr:
                    show_dirs.append('[○]' + dirstr)
                else:
                    show_dirs.append('[X]' + dirstr)

            self.window.show_quick_panel(show_dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.auth_type = self.dirs[picked]

        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        # print('self.auth_type-->')
        # print(self.auth_type)
        self.sf_basic_config.update_authentication_setting(self.auth_type)


class SwitchBrowserCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf_basic_config = SfBasicConfig()
            self.settings = self.sf_basic_config.get_setting()
            self.sublconsole = SublConsole(self.sf_basic_config)

            self.dirs = self.sf_basic_config.get_browser_setting2()
            dirs = []
            for dir in self.dirs:
                dirs.append(dir[0])

            self.window.show_quick_panel(dirs, self.panel_done,sublime.MONOSPACE_FONT)

        except Exception as e:
            self.sublconsole.showlog(e)
            return

    def panel_done(self, picked):
        if 0 > picked < len(self.dirs):
            return
        self.browser = self.dirs[picked][0]
        self.broswer_name = self.dirs[picked][1]

        self.sublconsole.thread_run(target=self.main_handle)

    def main_handle(self):
        self.sf_basic_config.update_default_browser(self.broswer_name)




class AboutHxyCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        sf_basic_config = SfBasicConfig()
        sublconsole = SublConsole(sf_basic_config)
        
        version_info = sublime.load_settings("sfdc.version.sublime-settings")
        version_msg = "%s v%s\n\n%s\n\nCopyright © 2016-2018 By %s\n\nEmail: %s\nHomePage: %s\n" % (
            version_info.get("name"),
            version_info.get("version"),
            version_info.get("description"),
            version_info.get("author"),
            version_info.get("email"),
            version_info.get("homepage")
        )
        sublconsole.show_in_dialog(version_msg)


class ReportIssueXyCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        sf_basic_config = SfBasicConfig()
        version_info = sublime.load_settings("sfdc.version.sublime-settings")
        util.open_in_default_browser(sf_basic_config, version_info.get("issue"))


class HomePageCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        sf_basic_config = SfBasicConfig()
        sublconsole = SublConsole(sf_basic_config)
        version_info = sublime.load_settings("sfdc.version.sublime-settings")
        util.open_in_default_browser(sf_basic_config, version_info.get("homepage"))


class ShowSalesforcexytoolsLogsCommand(sublime_plugin.ApplicationCommand):
    def run(command):
        sf_basic_config = SfBasicConfig()
        sublconsole = SublConsole(sf_basic_config)
        sublconsole.showlog('Open Salesforcexytools Logs Panel')



##########################################################################################
#Main Util
##########################################################################################
# salesforce_instance is Salesforce instance from simple-salesforce
def login_sf_home(self, sf_basic_config, salesforce_instance, browser='default', broswer_path=''):
        try:
            self.sublconsole.debug(">>login sf home")
            sf = salesforce_instance
            sfdesc = sf.describe()
             
            returl = '/home/home.jsp'
            login_url = ('https://{instance}/secur/frontdoor.jsp?sid={sid}&retURL={returl}'
                         .format(instance=sf.sf_instance,
                                 sid=sf.session_id,
                                 returl=returl))
            if browser == 'default':
                self.sublconsole.debug(">>default browser")
                util.open_in_default_browser(sf_basic_config, login_url)
            else:
                self.sublconsole.debug(">>other browser")
                util.open_in_browser(sf_basic_config, login_url,browser,broswer_path)


        except RequestException as e:
            self.sublconsole.showlog("Network connection timeout when issuing REST GET request")
            return
        except SalesforceExpiredSession as e:
            self.sublconsole.show_in_dialog('session expired')
            util.re_auth()
            return
        except SalesforceRefusedRequest as e:
            self.sublconsole.showlog('The request has been refused.')
            return
        except SalesforceError as e:
            err = 'Error code: %s \nError message:%s' % (e.status,e.content)
            self.sublconsole.showlog(err)
            return
        except Exception as e:
            self.sublconsole.showlog(e)
            return

# format soql ,
# format 'select * from Sojbect' -> add all field 
def soql_format(sf_instance,soql_str):
    import re

    soql = baseutil.del_comment(soql_str)
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
        fields.append(baseutil.xstr(field["name"]))
    return fields

