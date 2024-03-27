#!/usr/bin/python3
# -*- utf-8 -*-
#
# Copyright (C) 2021-2023 Ken'ichi Fukamachi
#   All rights reserved. This program is free software; you can
#   redistribute it and/or modify it under 2-Clause BSD License.
#   https://opensource.org/licenses/BSD-2-Clause
#
# mailto: fukachan@fml.org
#    web: https://www.fml.org/
# github: https://github.com/fmlorg
#
# $FML: www.py,v 1.7 2023/04/07 06:57:31 fukachan Exp $
# $Revision: 1.7 $
#        NAME: www.py
# DESCRIPTION: a standalone web server based on python3 modules,
#              which is used as a template for our system build exercises.
#              See https://sysbuild-entrance.fml.org/ for more details.
#
import os
import sys
import http.server
import socketserver
import json

#
# Configurations
#
HTTP_HOST       = "0.0.0.0"
HTTP_PORT       = 8080
HTDOCS_DIR      = "/var/www/html"


# WWW server example: Handler class, which handles www requests
# httpHandler inherits ths superclass http.server.SimpleHTTPRequestHandler
class httpHandler(http.server.SimpleHTTPRequestHandler):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, directory=HTDOCS_DIR, **kwargs)

   def _set_headers(self):
      self.send_response(200)
      self.send_header('Content-type','application/json; charset=utf-8')
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")
      self.end_headers()

   def do_OPTIONS(self):
      self.send_response(200)
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With,Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")
      self.end_headers()

   def do_GET(self):
      return super().do_GET()

   def do_POST(self):
      self._set_headers()
      data = {}
      message = json.dumps(data, ensure_ascii=False)
      self.wfile.write(bytes(message, "utf8"))

   def jibun(self):
      pass

   def aite(self):
      pass

   def janken(self):
      pass

   def openbd(self):
      pass

   def db_connect(self):
      pass

   def db_insert(self, jibun, aite, kekka):
      connection            = self.db_connect()
      connection.autocommit = True

      pass

      connection.close

   def db_show(self):
      connection            = self.db_connect()
      connection.autocommit = True

      pass

      connection.close


#
# MAIN
#
if __name__ == "__main__":
   # run python www server (httpd)
   with socketserver.TCPServer((HTTP_HOST, HTTP_PORT), httpHandler) as httpd:
      print("(debug) serving at port", HTTP_PORT, file=sys.stderr)
      httpd.serve_forever()
