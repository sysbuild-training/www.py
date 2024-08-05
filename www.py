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
# $FML: www.py,v 1.60 2024/04/21 10:54:16 fukachan Exp $
# $Revision: 1.60 $
#        NAME: www.py
# DESCRIPTION: a standalone web server based on python3 modules,
#              which is used as a template for our system build exercises.
#              See https://sysbuild-entrance.fml.org/ for more details.
#
import os
import sys
import pwd
import socketserver
import http.server
import http.cookies
import cgi
import json


#
# Global Configurations
#
HTTP_HOST     = "0.0.0.0"
HTTP_PORT     = 80
HTDOCS_DIR    = "/home/admin/htdocs"
INDEX_FILE    = HTDOCS_DIR + "/index.html"
UPLOADED_FILE = HTDOCS_DIR + "/file.uploaded"



# WWW server example: Handler class, which handles www requests
# httpHandler inherits the superclass http.server.SimpleHTTPRequestHandler
class httpHandler(http.server.SimpleHTTPRequestHandler):
   def __init__(self, *args, **kwargs):
      self.cookie = http.cookies.SimpleCookie()      
      self.cookie["_session"]           = ""
      self.cookie["_session"]["domain"] = "cloud.fml.org"      
      super().__init__(*args, directory=HTDOCS_DIR, **kwargs)

   def _set_headers(self, type):
      self.send_response(200)
      self.send_header("Content-type","{}; charset=utf-8".format(type))
      self._set_cors()
      self._set_cookie()
      self.end_headers()

   # CORS (Cross-Origin Resource Sharing)
   def _set_cors(self):
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")

   # get cookies in Cookie: field sent from WWW client (Browser)
   # - return value: STRING
   def _get_cookie(self):
      if self.headers.get('Cookie'):
         self.cookie.load(self.headers['Cookie'])
      if "_session"  in self.cookie:
         return self.cookie[ "_session" ].value
      else:
         return ""
      
   # set Set-Cookie to send cookie information to the client (WWW Browser)
   def _set_cookie(self):
      self.send_header("Set-Cookie", self.cookie.output(header=""))


   def do_OPTIONS(self):
      self.send_response(200)
      self._set_cors()
      self.end_headers()


   def do_GET(self):
      return super().do_GET()


   def do_POST(self):
      # local variables
      type    = "text/html"      # default Content-Type
      message = "***failed***\n" # string
      form    = cgi.FieldStorage(
         fp=self.rfile,
         headers=self.headers,
         environ={"REQUEST_METHOD": "POST"}
      )

      # routing: call the corresponding method for the URL path
      if self.path == "/api/lsform/v1":
         message = self.lsform(form)
      if self.path == "/api/upload/v1":
         message = self.upload(form)
         
      # set the HTTP "Content-Type" header field to type
      self._set_headers(type)
      # return the message (STRING) to the browser
      self.wfile.write(bytes(message, "utf8"))


   # LSFORM = LiSt FORM key,value(s) as HTML TABLE
   def lsform(self, form):
      msg = ""    # return string
      msg = msg + "<p>list up form values\n"
      msg = msg + "<table border=0 frame=void cellspacing=30>\n"

      # check all FORM key,value and create each table row
      keys = sorted(form.keys())
      for key in keys:
         val = form[key].value
         msg = msg + "<tr><td>{}<td>{}</tr>\n".format(key,val)

      msg = msg + "</table>\n"
      return msg


   # UPLOAD: uploaded data is written to UPLOADED_FILE(= /home/admin/htdocs/file.uploaded)
   def upload(self, form):
      count = 0
      with open(UPLOADED_FILE, mode="wb") as fp:
         count = fp.write(form["file"].file.read())
      # exercise: AWS Rekognition extension
      return "uploaded: {} bytes written\n".format(count)


   # Exercise Template: Janken program web version
   # - hint: kekka = (3 + jibun - aite) % 3
   def janken(self,form):
      pass


   # Exercise Template: ISBN search
   # - hint: json.dumps() convert DICT to STRING
   def openbd(self,form):
      data = {} # dict
      return json.dumps(data, ensure_ascii=False)



# www.py specific utilities
# - If you read this, you must be interested in IT infrastructure ?
#   Welcome to H205 IT infra club :-)
# - You do not need to understand this for the lectures.
class wwwpyUtils:
    def __init__(self):
        pass

    def create_hompepage_if_not_found(self, dir = HTDOCS_DIR, file = INDEX_FILE):
       self.mkdir_if_not_found(dir)

       if not os.path.exists(file):
          with open(file, mode="x") as fp:
             fp.write("welcome to my homepage\n")

    def mkdir_if_not_found(self, dir):
       if not os.path.isdir(dir):
          os.mkdir(dir, mode=0o755)

    def set_userenv(self):
       user = os.getenv("SUDO_USER")
       if not user:
          user = os.getlogin()
       p = pwd.getpwnam(user)
       os.seteuid(p.pw_uid)

    def get_userenv(self):
       if os.getenv("DEBUG"):
          euid = os.geteuid()
          egid = os.getegid()
          print("(debug) euid={}, egid={}".format(euid,egid))


#
# MAIN
#
if __name__ == "__main__":
   # not recommended but may be allowed since this practice is for personal use only.
   socketserver.TCPServer.allow_reuse_address = True

   # run python www server (httpd)
   with socketserver.TCPServer((HTTP_HOST, HTTP_PORT), httpHandler) as httpd:
      print("(debug) serving at port", HTTP_PORT, file=sys.stderr)

      # - this process runs as "root" under "sudo ..." by default,
      #   which is required to listen 80/tcp.
      # - So, we change back the effective UID to "admin" after 80/tcp open.
      wwwpyUtils().set_userenv()
      wwwpyUtils().get_userenv()

      # create "/home/admin/htdocs/index.html" if not exists
      wwwpyUtils().mkdir_if_not_found(HTDOCS_DIR)
      wwwpyUtils().create_hompepage_if_not_found(file=INDEX_FILE)

      # run the www server forever (infinite loop)
      httpd.serve_forever()
