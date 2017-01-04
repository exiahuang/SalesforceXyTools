####################################
#START OF Bulk API
#Source is base on Salesforce Bulk
#https://github.com/heroku/salesforce-bulk
####################################
import sys
import re
import csv
import xml.etree.ElementTree as ET
from tempfile import TemporaryFile, NamedTemporaryFile
from collections import namedtuple

from .. import requests
from . import Soap
from . import SoapException

# Syntax sugar.
_ver = sys.version_info
#: Python 2.x?
is_py2 = (_ver[0] == 2)
#: Python 3.x?
is_py3 = (_ver[0] == 3)
if is_py2:
    import StringIO
    StringIO = BytesIO = StringIO.StringIO
elif is_py3:
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO

DEFAULT_API_VERSION = '37.0'
ABORTED = 'Aborted'
FAILED = 'Failed'
NOT_PROCESSED = 'Not Processed'
COMPLETED = 'Completed'

ERROR_STATES = (
    ABORTED,
    FAILED,
    NOT_PROCESSED,
)


UploadResult = namedtuple('UploadResult', 'id success created error')


class BulkApiError(Exception):

    def __init__(self, message, status_code=None):
        super(BulkApiError, self).__init__(message)
        self.status_code = status_code


class BulkJobAborted(BulkApiError):

    def __init__(self, job_id):
        self.job_id = job_id

        message = 'Job {0} aborted'.format(job_id)
        super(BulkJobAborted, self).__init__(message)


class BulkBatchFailed(BulkApiError):

    def __init__(self, job_id, batch_id, state_message):
        self.job_id = job_id
        self.batch_id = batch_id
        self.state_message = state_message

        message = 'Batch {0} of job {1} failed: {2}'.format(batch_id, job_id,
                                                            state_message)
        super(BulkBatchFailed, self).__init__(message)


class Bulk(Soap):
    def __init__(
            self, username=None, password=None, security_token=None,
            session_id=None, instance=None, instance_url=None,
            organizationId=None, sandbox=False, version=DEFAULT_API_VERSION,
            proxies=None, session=None, client_id=None, settings=None):
        super(Bulk, self).__init__(username, password, security_token,
            session_id, instance, instance_url,
            organizationId, sandbox, version,
            proxies, session, client_id, settings)

        self.sf_version = "36.0"
        # Bulk API:
        self.bulk_api_url = ('https://{instance}/services/async/{version}'
                         .format(instance=self.sf_instance,
                                 version=self.sf_version))

        self.jobNS = 'http://www.force.com/2009/06/asyncapi/dataload'
        self.jobs = {}  # dict of job_id => job_id
        self.batches = {}  # dict of batch_id => job_id
        self.batch_statuses = {}


    def bulk_headers(self, values={}):
        default = {"X-SFDC-Session": self.session_id,
                   "Content-Type": "application/xml; charset=UTF-8"}
        for k, val in values.items():
            default[k] = val
        return default

    # Register a new Bulk API job - returns the job id
    def create_query_job(self, object_name, **kwargs):
        return self.create_job(object_name, "query", **kwargs)

    def create_insert_job(self, object_name, **kwargs):
        return self.create_job(object_name, "insert", **kwargs)

    def create_upsert_job(self, object_name, external_id_name, **kwargs):
        return self.create_job(object_name, "upsert", external_id_name=external_id_name, **kwargs)

    def create_update_job(self, object_name, **kwargs):
        return self.create_job(object_name, "update", **kwargs)

    def create_delete_job(self, object_name, **kwargs):
        return self.create_job(object_name, "delete", **kwargs)


    def create_job(self, object_name=None, operation=None, contentType='CSV',
                   concurrency=None, external_id_name=None):
        assert(object_name is not None)
        assert(operation is not None)
        job_id = ''

        doc = self.create_job_doc(object_name=object_name,
                                  operation=operation,
                                  contentType=contentType,
                                  concurrency=concurrency,
                                  external_id_name=external_id_name)

        url = self.bulk_api_url + "/job"
        
        # print('------->doc')
        # print(doc)
        # print('------->url')
        # print(url)
        # print('------->self.bulk_headers')
        # print(self.bulk_headers)
        # resp = self._soap_post(url=url, request_body=doc, headers=self.bulk_headers())
        resp = requests.post(url, doc, headers=self.bulk_headers(), proxies=self.proxies, verify=False)
        content = resp.text
        # from . import requests
        # resp = requests.post(url, doc, headers=self.bulk_headers, proxies=self.proxies, verify=False)

        # print(resp)
        # print('resp.text------->')
        # print(resp.text)
        # print('resp.content----->')
        # print(resp.content)
        # print('resp.status_code----->')
        # print(resp.status_code)

        tree = ET.fromstring(content)
        job_id = tree.findtext("{%s}id" % self.jobNS)
        self.jobs[job_id] = job_id

        print("----->jobid " + job_id)

        return job_id

    def check_status(self, resp, content):
        if resp.status_code >= 400:
            msg = "Bulk API HTTP Error result: {0}".format(content)
            self.raise_error(msg, resp.status_code)

    def close_job(self, job_id):
        doc = self.create_close_job_doc()
        
        url = self.bulk_api_url + "/job/%s" % job_id
        # resp, content = http.request(url, "POST", headers=self.bulk_headers(),
        #                              body=doc)
        # resp = self._soap_post(url=url, request_body=doc, headers=self.bulk_headers())
        resp = requests.post(url, doc, headers=self.bulk_headers(), proxies=self.proxies, verify=False)
        content = resp.text

        self.check_status(resp, content)

    def abort_job(self, job_id):
        """Abort a given bulk job"""
        doc = self.create_abort_job_doc()
        
        url = self.bulk_api_url + "/job/%s" % job_id
        # resp, content = http.request(
        #     url,
        #     "POST",
        #     headers=self.bulk_headers(),
        #     body=doc
        # )
        # resp = self._soap_post(url=url, request_body=doc, headers=self.bulk_headers())
        resp = requests.post(url, doc, headers=self.bulk_headers(), proxies=self.proxies, verify=False)
        content = resp.text
        self.check_status(resp, content)


    def create_job_doc(self, object_name=None, operation=None,
                       contentType='CSV', concurrency=None, external_id_name=None):
        root = ET.Element("jobInfo")
        root.set("xmlns", self.jobNS)
        op = ET.SubElement(root, "operation")
        op.text = operation
        obj = ET.SubElement(root, "object")
        obj.text = object_name
        if external_id_name:
            ext = ET.SubElement(root, 'externalIdFieldName')
            ext.text = external_id_name

        if concurrency:
            con = ET.SubElement(root, "concurrencyMode")
            con.text = concurrency
        ct = ET.SubElement(root, "contentType")
        ct.text = contentType

        buf = BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="UTF-8")
        return buf.getvalue().decode("utf-8") 

    def create_close_job_doc(self):
        root = ET.Element("jobInfo")
        root.set("xmlns", self.jobNS)
        state = ET.SubElement(root, "state")
        state.text = "Closed"

        buf = BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="UTF-8")
        return buf.getvalue().decode("utf-8") 

    def create_abort_job_doc(self):
        """Create XML doc for aborting a job"""
        root = ET.Element("jobInfo")
        root.set("xmlns", self.jobNS)
        state = ET.SubElement(root, "state")
        state.text = "Aborted"

        buf = BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="UTF-8")
        return buf.getvalue().decode("utf-8") 

    # Add a BulkQuery to the job - returns the batch id
    def query(self, job_id, soql):
        if job_id is None:
            job_id = self.create_job(
                re.search(re.compile("from (\w+)", re.I), soql).group(1),
                "query")
        
        uri = self.bulk_api_url + "/job/%s/batch" % job_id
        print('uri-->')
        print(uri)
        
        headers = self.bulk_headers({"Content-Type": "text/csv"})
        resp = requests.post(uri, soql, headers=headers, proxies=self.proxies, verify=False)
        content = resp.text
        self.check_status(resp, content)

        tree = ET.fromstring(content)
        batch_id = tree.findtext("{%s}id" % self.jobNS)

        self.batches[batch_id] = job_id

        return batch_id

    def split_csv(self, csv, batch_size):
        #  TODO
        csv_io = StringIO(csv)
        batches = []

        for i, line in enumerate(csv_io):
            if not i:
                headers = line
                batch = headers
                continue
            if not i % batch_size:
                batches.append(batch)
                batch = headers

            batch += line

        batches.append(batch)

        return batches

    # Add a BulkUpload to the job - returns the batch id
    def bulk_csv_upload(self, job_id, csv, batch_size=2500):
        # Split a large CSV into manageable batches
        batches = self.split_csv(csv, batch_size)
        batch_ids = []

        uri = self.bulk_api_url + "/job/%s/batch" % job_id
        headers = self.bulk_headers({"Content-Type": "text/csv"})
        for batch in batches:
            resp = requests.post(uri, data=batch, headers=headers)
            content = resp.content

            if resp.status_code >= 400:
                self.raise_error(content, resp.status)

            tree = ET.fromstring(content)
            batch_id = tree.findtext("{%s}id" % self.jobNS)

            self.batches[batch_id] = job_id
            batch_ids.append(batch_id)

        return batch_ids

    def raise_error(self, message, status_code=None):
        if status_code:
            message = "[{0}] {1}".format(status_code, message)

        raise SoapException(message, status_code=status_code)


    def post_bulk_batch(self, job_id, csv_generator):
        uri = self.bulk_api_url + "/job/%s/batch" % job_id
        headers = self.bulk_headers({"Content-Type": "text/csv"})
        resp = requests.post(uri, data=csv_generator, headers=headers)
        content = resp.content

        if resp.status_code >= 400:
            self.raise_error(content, resp.status_code)

        tree = ET.fromstring(content)
        batch_id = tree.findtext("{%s}id" % self.jobNS)
        return batch_id

    # Add a BulkDelete to the job - returns the batch id
    def bulk_delete(self, job_id, object_type, where, batch_size=2500):
        query_job_id = self.create_query_job(object_type)
        soql = "Select Id from %s where %s Limit 10000" % (object_type, where)
        query_batch_id = self.query(query_job_id, soql)
        self.wait_for_batch(query_job_id, query_batch_id, timeout=120)

        results = []

        def save_results(tf, **kwargs):
            results.append(tf.read())

        flag = self.get_batch_results(
            query_job_id, query_batch_id)

        if job_id is None:
            job_id = self.create_job(object_type, "delete")
        
        # Split a large CSV into manageable batches
        batches = self.split_csv(csv, batch_size)
        batch_ids = []

        uri = self.bulk_api_url + "/job/%s/batch" % job_id
        headers = self.bulk_headers({"Content-Type": "text/csv"})
        for batch in results:
            resp = requests.post(uri, data=batch, headers=headers)
            content = resp.content

            if resp.status_code >= 400:
                self.raise_error(content, resp.status)

            tree = ET.fromstring(content)
            batch_id = tree.findtext("{%s}id" % self.jobNS)

            self.batches[batch_id] = job_id
            batch_ids.append(batch_id)

        return batch_ids

    def lookup_job_id(self, batch_id):
        try:
            return self.batches[batch_id]
        except KeyError:
            raise Exception(
                "Batch id '%s' is uknown, can't retrieve job_id" % batch_id)

    def job_status(self, job_id=None):
        job_id = job_id or self.lookup_job_id(batch_id)
        uri = urlparse.urljoin(self.bulk_api_url +"/",
            'job/{0}'.format(job_id))
        resp = requests.get(uri, headers=self.bulk_headers())
        if resp.status_code != 200:
            self.raise_error(resp.content, resp.status_code)

        tree = ET.fromstring(resp.content)
        result = {}
        for child in tree:
            result[re.sub("{.*?}", "", child.tag)] = child.text
        return result

    def job_state(self, job_id):
        status = self.job_status(job_id)
        if 'state' in status:
            return status['state']
        else:
            return None

    def batch_status(self, job_id=None, batch_id=None, reload=False):
        if not reload and batch_id in self.batch_statuses:
            return self.batch_statuses[batch_id]

        job_id = job_id or self.lookup_job_id(batch_id)

        
        uri = self.bulk_api_url + \
            "/job/%s/batch/%s" % (job_id, batch_id)
        # resp, content = http.request(uri, headers=self.bulk_headers())
        
        # resp = self._soap_post(url=uri, request_body="", headers=self.bulk_headers())
        resp = requests.get(uri, data=None, headers=self.bulk_headers(), proxies=self.proxies, verify=False)
        # response = requests.get(url, data=None, verify=False, headers=self.headers)

        content = resp.text

        print("------>uri ")
        print(uri)
        print("content-->")
        print(content)
        print("self.bulk_headers()-->")
        print(self.bulk_headers())

        self.check_status(resp, content)

        tree = ET.fromstring(content)
        result = {}
        for child in tree:
            result[re.sub("{.*?}", "", child.tag)] = child.text

        self.batch_statuses[batch_id] = result
        return result

    def batch_state(self, job_id, batch_id, reload=False):
        status = self.batch_status(job_id, batch_id, reload=reload)
        if 'state' in status:
            return status['state']
        else:
            return None

    def is_batch_done(self, job_id, batch_id):
        batch_state = self.batch_state(job_id, batch_id, reload=True)
        if batch_state in ERROR_STATES:
            status = self.batch_status(job_id, batch_id)
            raise BulkBatchFailed(job_id, batch_id, status['stateMessage'])
        return batch_state == COMPLETED

    # Wait for the given batch to complete, waiting at most timeout seconds
    # (defaults to 10 minutes).
    def wait_for_batch(self, job_id, batch_id, timeout=60 * 10,
                       sleep_interval=10):
        waited = 0
        while not self.is_batch_done(job_id, batch_id) and waited < timeout:
            time.sleep(sleep_interval)
            waited += sleep_interval

    def get_batch_result_ids(self, batch_id, job_id=None):
        job_id = job_id or self.lookup_job_id(batch_id)
        if not self.is_batch_done(job_id, batch_id):
            return False

        uri = urlparse.urljoin(
            self.bulk_api_url + "/",
            "job/{0}/batch/{1}/result".format(
                job_id, batch_id),
        )
        resp = requests.get(uri, headers=self.bulk_headers())
        if resp.status_code != 200:
            return False

        tree = ET.fromstring(resp.content)
        find_func = getattr(tree, 'iterfind', tree.findall)
        return [str(r.text) for r in
                find_func("{{{0}}}result".format(self.jobNS))]

    def get_all_results_for_batch(self, batch_id, job_id=None, parse_csv=False, logger=None):
        """
        Gets result ids and generates each result set from the batch and returns it
        as an generator fetching the next result set when needed

        Args:
            batch_id: id of batch
            job_id: id of job, if not provided, it will be looked up
            parse_csv: if true, results will be dictionaries instead of lines
        """
        result_ids = self.get_batch_result_ids(batch_id, job_id=job_id)
        if not result_ids:
            if logger:
                logger.error('Batch is not complete, may have timed out. '
                             'batch_id: %s, job_id: %s', batch_id, job_id)
            raise RuntimeError('Batch is not complete')
        for result_id in result_ids:
            yield self.get_batch_results(
                batch_id,
                result_id,
                job_id=job_id,
                parse_csv=parse_csv)

    def get_batch_results(self, batch_id, result_id, job_id=None,
                          parse_csv=False, logger=None):
        job_id = job_id or self.lookup_job_id(batch_id)
        logger = logger or (lambda message: None)

        uri = urlparse.urljoin(
            self.bulk_api_url + "/",
            "job/{0}/batch/{1}/result/{2}".format(
                job_id, batch_id, result_id),
        )
        logger('Downloading bulk result file id=#{0}'.format(result_id))
        resp = requests.get(uri, headers=self.bulk_headers(), stream=True)

        if not parse_csv:
            iterator = resp.iter_lines()
        else:
            iterator = csv.reader(resp.iter_lines(), delimiter=',',
                                  quotechar='"')

        BATCH_SIZE = 5000
        for i, line in enumerate(iterator):
            if i % BATCH_SIZE == 0:
                logger('Loading bulk result #{0}'.format(i))
            yield line

    def get_batch_result_iter(self, job_id, batch_id, parse_csv=False,
                              logger=None):
        """
        Return a line interator over the contents of a batch result document. If
        csv=True then parses the first line as the csv header and the iterator
        returns dicts.
        """
        status = self.batch_status(job_id, batch_id)
        if status['state'] != 'Completed':
            return None
        elif logger:
            if 'numberRecordsProcessed' in status:
                logger("Bulk batch %d processed %s records" %
                       (batch_id, status['numberRecordsProcessed']))
            if 'numberRecordsFailed' in status:
                failed = int(status['numberRecordsFailed'])
                if failed > 0:
                    logger("Bulk batch %d had %d failed records" %
                           (batch_id, failed))

        uri = self.bulk_api_url + \
            "/job/%s/batch/%s/result" % (job_id, batch_id)
        r = requests.get(uri, headers=self.bulk_headers(), stream=True)

        result_id = r.text.split("<result>")[1].split("</result>")[0]

        uri = self.bulk_api_url + \
            "/job/%s/batch/%s/result/%s" % (job_id, batch_id, result_id)
        r = requests.get(uri, headers=self.bulk_headers(), stream=True)

        if parse_csv:
            return csv.DictReader(r.iter_lines(chunk_size=2048), delimiter=",",
                                  quotechar='"')
        else:
            return r.iter_lines(chunk_size=2048)

    def get_upload_results(self, job_id, batch_id,
                           callback=(lambda *args, **kwargs: None),
                           batch_size=0, logger=None):
        job_id = job_id or self.lookup_job_id(batch_id)

        if not self.is_batch_done(job_id, batch_id):
            return False
        
        uri = self.bulk_api_url + \
            "/job/%s/batch/%s/result" % (job_id, batch_id)
        # resp, content = http.request(uri, method="GET", headers=self.bulk_headers())
        resp = self._soap_get(url=uri, headers=self.bulk_headers())
        content = resp.text

        tf = TemporaryFile()
        tf.write(content)

        total_remaining = self.count_file_lines(tf)
        if logger:
            logger("Total records: %d" % total_remaining)
        tf.seek(0)

        records = []
        line_number = 0
        col_names = []
        reader = csv.reader(tf, delimiter=",", quotechar='"')
        for row in reader:
            line_number += 1
            records.append(UploadResult(*row))
            if len(records) == 1:
                col_names = records[0]
            if batch_size > 0 and len(records) >= (batch_size + 1):
                callback(records, total_remaining, line_number)
                total_remaining -= (len(records) - 1)
                records = [col_names]
        callback(records, total_remaining, line_number)

        tf.close()

        return True

    def parse_csv(self, tf, callback, batch_size, total_remaining):
        records = []
        line_number = 0
        col_names = []
        reader = csv.reader(tf, delimiter=",", quotechar='"')
        for row in reader:
            line_number += 1
            records.append(row)
            if len(records) == 1:
                col_names = records[0]
            if batch_size > 0 and len(records) >= (batch_size + 1):
                callback(records, total_remaining, line_number)
                total_remaining -= (len(records) - 1)
                records = [col_names]
        return records, total_remaining

    def count_file_lines(self, tf):
        tf.seek(0)
        buffer = bytearray(2048)
        lines = 0

        quotes = 0
        while tf.readinto(buffer) > 0:
            quoteChar = ord('"')
            newline = ord('\n')
            for c in buffer:
                if c == quoteChar:
                    quotes += 1
                elif c == newline:
                    if (quotes % 2) == 0:
                        lines += 1
                        quotes = 0

        return lines

####################################
#END OF Bulk API
####################################