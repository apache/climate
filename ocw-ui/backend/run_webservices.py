#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
''' OCW UI Backend web services initialization. '''

from bottle import Bottle, response, static_file
from local_file_metadata_extractors import lfme_app
from directory_helpers import dir_app
from rcmed_helpers import rcmed_app
from podaac_helpers import podaac_app
from processing import processing_app

app = Bottle()
app.mount('/lfme/', lfme_app)
app.mount('/dir/', dir_app)
app.mount('/rcmed/', rcmed_app)
app.mount('/podaac/', podaac_app)
app.mount('/processing/', processing_app)

@app.route('/')
@app.route('/index.html')
def index():
    return static_file('index.html', root='./frontend/app/')

@app.route('/bower_components/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/bower_components/')

@app.route('/styles/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/styles/')

@app.route('/scripts/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/scripts/')

@app.route('/views/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/views/')

@app.route('/img/:path#.+#')
def server_static(path):
     return static_file(path, root='./frontend/app/img/')

@app.route('/static/eval_results/<file_path:path>')
def get_eval_result_image(file_path):
    ''' Return static file.

    Return static file specified by root + filepath where root defaults to:
        /tmp/ocw

    The 'root' path should coincide with the work directory set used by the
    OCW toolkit for processing.

    :param filepath: The path component that when appended to the 'root' path
        header specifies a file to return.
    :type filepath: string

    :returns: The requested file resource
    '''
    return static_file(file_path, root="/tmp/ocw")

@app.hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == "__main__":
    app.run(host='localhost', port=8082)
