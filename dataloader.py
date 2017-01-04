####################################
#Dataloader
#Bluk API
####################################
import sublime
import sublime_plugin
import os
import threading
import time

from . import util
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
    SalesforceError,
    Bulk
    )

DIR_DATALOADER = 'dataloader'

class ExportSobjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            self.sf = util.sf_login(Soap_Type=Bulk)
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

        time_stamp = time.strftime("%Y%m%d%H%M", time.localtime())
        self.fullPath =  os.path.join(util.get_default_floder(), DIR_DATALOADER, "%s_%s.csv" % (self.picked_name, time_stamp))
        # show_input_panel(caption, initial_text, on_done, on_change, on_cancel)
        self.window.show_input_panel("Export CSV Path: " , 
            self.fullPath, self.on_input, None, None)

    def on_input(self, args):
        thread = threading.Thread(target=self.main_handle)
        thread.start()
        util.handle_thread(thread)


    def main_handle(self):
        try:
            self.sftype = self.sf.get_sobject(self.picked_name)
            sftypedesc = self.sftype.describe()
            soql = util.get_simple_soql_str(self.picked_name, sftypedesc["fields"])
            # print(soql)

            bulk = self.sf
            job = bulk.create_query_job(self.picked_name, contentType='CSV')
            batch = bulk.query(job, soql)
            
            print("job:" + job)
            print("batch:" + batch)

            while not bulk.is_batch_done(job, batch):
                time.sleep(10)

            print("job batch ok!")

            encoding = self.sf.settings["dataloader_encoding"]
            print("encoding : " + encoding)

            result = ''
            for row in bulk.get_batch_result_iter(job, batch, parse_csv=False):
                result += row.decode(encoding) + '\n'
   
            if result:
                util.save_file(self.fullPath,result)
   
        except Exception as e:
            util.show_in_panel(e)
            print(e)
        finally:
            bulk.close_job(job)

