'''
author: huangxy
homepage: http://www.ibmer.info
linence: 
'''
import base64
import os
import sys
import threading
from .cherrypy import wsgiserver
from . import bottle
# bottle.debug(True)
from .bottle import Bottle, ServerAdapter
from .bottle import static_file, request, template
# Create a new app stack
app = Bottle()


@app.route('/auth/callback', method=['GET', 'POST'])
def do_callback():
    html = '''
<html>
  <head>
    <title>SalesforceXyTools OAuth</title>
  </head>
  <body>
      <script type="text/javascript">
        var url = window.location.href;
        var arg=url.split("#");
        if (arg[1] === "undefined") {
        }else{
            var reUrl = "/auth/finish?" +arg[1];
            window.location.href=reUrl;  
        }
      </script>
  </body>
</html>
'''
    query = request.query_string
    params = {}
    if 'error' in query:
        params['error'] = request.query['error']
        params['error_description'] = ''
        if 'error_description' in query:
            params['error_description'] = request.query['error_description']
        err_page = '''
<html>
  <head>
    <title>SalesforceXyTools OAuth</title>
  </head>
  <body>
    <span style="background-color:#ff0000;">Login Error!!</span><br/>
    <span style="background-color:#ff0000;">{error_description}</span>
  </body>
</html>
'''
        return err_page.format(error_description=params['error_description'])

    return html

@app.route('/auth/finish', method=['GET', 'POST'])
def do_finish():
    query = request.query_string
    params = {}
    if 'access_token' in query:
        params['access_token'] = request.query['access_token']

        pyDict={}
        for item in request.params:
           pyDict[item]=request.params.get(item)

        from .. import util
        util.save_session(pyDict)
        html = '''
    <html>
      <head>
        <title>SalesforceXyTools OAuth</title>
      </head>
      <body>
          <span style="">Login Success!!</span><br/>
          <span style="">Please close the windows!!</span><br/>
          <script type="text/javascript">
            //window.close();
          </script>
      </body>
    </html>
'''
    else:
        html = '''
    <html>
      <head>
        <title>SalesforceXyTools OAuth</title>
      </head>
      <body>
          <span style="background-color:#ff0000;">Login Error!!</span><br/>
          <span style="">Please close the windows!!</span><br/>
          <script type="text/javascript">
            //window.close();
          </script>
      </body>
    </html>
'''
    # if 'refresh_token' in query:
    #     params['refresh_token'] = request.query['refresh_token']
    # if 'instance_url' in query:
    #     params['instance_url'] = request.query['instance_url']
    # if 'token_type' in query:
    #     params['token_type'] = request.query['token_type']

    
    # print('request.query-->')
    # print(request.query)
    
    return html



class StoppableCherryPyServer(ServerAdapter):
    """HACK for making a stoppable server"""

    def __int__(self, *args, **kwargs):
        super(ServerAdapter, self).__init__(*args, **kwargs)
        self.srv = None

    def run(self, handler):
        self.srv = wsgiserver.CherryPyWSGIServer(
            (self.host, self.port), handler, numthreads=2, timeout=2, shutdown_timeout=2
        )
        self.srv.start()

    def shutdown(self):
        try:
            if self.srv is not None:
                self.srv.stop()
        except:
            raise Exception('Error on shutting down cherrypy server')
        self.srv = None

def bottle_run(server):
    try:
        print("Bottle v%s server starting up..." % (bottle.__version__))
        print("Listening on http://%s:%d/" % (server.host, server.port))
        server.run(app)
    except:
        raise

class Server(object):
    class ServerThread(threading.Thread):
        def __init__(self, server):
            threading.Thread.__init__(self)
            self.server = server

        def run(self):
            bottle_run(server=self.server)

    def __init__(self, host='127.0.0.1', port='56888'):
        self.server = StoppableCherryPyServer(host=host, port=port)
        self.runner = Server.ServerThread(self.server)
        self.runner.daemon = True
        self.runner.start()

    def stop(self):
        print('Bottle server shuting down...')
        self.server.shutdown()
        self.runner.join()
