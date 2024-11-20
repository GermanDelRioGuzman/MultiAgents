
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import threading
import agentpy as ap
from matplotlib import pyplot as plt
import IPython
import random
from owlready2 import *

class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html') 
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        response_data = get_response()
        self._set_response()
        self.wfile.write(str(response_data).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), json.dumps(post_data))

        response_data = post_response(post_data)

        self._set_response()
        self.wfile.write(str(response_data).encode('utf-8'))

    def run(server_class=HTTPServer, handler_class=Server, port=8585):
        logging.basicConfig(level=logging.INFO)
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        logging.info("Starting httpd...\n") 
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:   
            pass
        httpd.server_close()
        logging.info("Stopping httpd...\n")

def post_response(data):

    model.environment = data
    model.post_flag = 1

    return model.step(data)

onto = get_ontology("file://onto.owl")
with onto:

    class RobotAgent(ap.Agent):

        _id_counter = 0

        def setup(self):
            """
            Inicialization function.
            """

            self.colisiontuple = (0,0,0,0) 

            self.havebox = 0 

            RobotAgent._id_counter += 1
            self.id = RobotAgent._id_counter

            self.actions = (
                self.move_N,
                self.move_S,
                self.move_E,
                self.move_W,
                self.move_random
            )

            self.rules = (
                self.rule_1,
                self.rule_2,
                self.rule_3
            )

        def see(self,e):
            
            data = e
            self.colisiontuple = data["Tuple"]
            self.havebox = data["boxes"]

            pass

        def next(self):
           pass

        def step(self):
           
            self.see(self.model.environment)
            self.next() 
        pass

        def update(self):
            pass

        def end(self):
            pass

        def rule_1(self):

            pass

        def rule_2(self):

            pass

        def rule_3(self):

            pass

    class RobotModel(ap.Model):

        def setup(self):
            
            self.environment = {}
            self.post_flag = 0

            self.robots = ap.AgentList(self, self.p.robots, RobotAgent)

            pass

        def step(self, data):
            """
            Función paso a paso
            """

            if self.post_flag == 1:
                self.robots.step() 
                self.post_flag = 0

            pass

        def update(self):
            pass

        def end(self):
            pass

parameters = {
    'robots': 5,
}

if _name_ == '_main_':
    from sys import argv

    p = threading.Thread(target=run, args = tuple(),daemon=True)
    p.start()

    model = RobotModel(parameters)
    results = model.run()