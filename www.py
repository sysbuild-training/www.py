#!/usr/bin/python3
# -*- utf-8 -*-
#
# Copyright (C) 2021-2024 Ken'ichi Fukamachi
#   All rights reserved. This program is free software; you can
#   redistribute it and/or modify it under 2-Clause BSD License.
#   https://opensource.org/licenses/BSD-2-Clause
#
# mailto: fukachan@fml.org
#    web: https://www.fml.org/
# github: https://github.com/fmlorg
#
#        $FML: www.py,v 1.84 2024/12/10 13:59:04 fukachan Exp $
#   $Revision: 1.84 $
#        NAME: www.py
# DESCRIPTION: a standalone web server based on python3 modules,
#              which is used as a template for our system build exercises.
#              See https://github.com/sysbuild-training for more details.
#
import os
import sys
import pwd
import socket
import socketserver
import http.server
import http.cookies
import cgi
import json


############################################################
#
# Global Configurations
#
HTTP_HOST     = "0.0.0.0"
HTTP_PORT     = 80

# www.py specific directories and files
HTDOCS_DIR    = "/home/admin/htdocs"
INDEX_FILE    = HTDOCS_DIR + "/index.html"
UPLOADED_FILE = HTDOCS_DIR + "/file.uploaded"

# HTTP specific parameters
COOKIE_DOMAIN = "cloud.fml.org"
CONTENT_TYPE  = "text/html"

#
# Global Configurations ENDS
#
############################################################
#
# WWW server (HTTP) class definition
#


# WWW server example: Handler class, which handles www requests
# httpHandler inherits the superclass http.server.SimpleHTTPRequestHandler
class httpHandler(http.server.SimpleHTTPRequestHandler):
   def __init__(self, *args, **kwargs):
      self.cookie = http.cookies.SimpleCookie()
      self.cookie["_session"]           = ""
      self.cookie["_session"]["domain"] = COOKIE_DOMAIN
      super().__init__(*args, directory=HTDOCS_DIR, **kwargs)

   def _get_headers(self):
      self._get_cookie_from_header()
      self._init_session_cookie()

   def _set_headers(self, type):
      self.send_response(200)
      self.send_header("Content-type","{}; charset=utf-8".format(type))
      self._set_cors()
      self._set_cookie_to_header()
      self.end_headers()

   # CORS (Cross-Origin Resource Sharing)
   def _set_cors(self):
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")

   # cookie handling utility functions
   # - _{get,set}_cookie_{from,to}_header() handles HTTP headers directly.
   #     - load cookie info from "Cookie:" http header field
   #     - set "Set-Cookie:" http header field to send back to the client (WWW Browser)
   # - _{get,set}_cookie() handles the internal self.cookie dict variable.
   # - _{get,set,gen,init}_session_cookie() are prepared for convenience.
   def _get_cookie_from_header(self):
      if self.headers.get('Cookie'):
         self.cookie.load(self.headers['Cookie'])

   def _set_cookie_to_header(self):
      self.send_header("Set-Cookie", self.cookie.output(header=""))

   def _get_cookie(self, key):
      return self.cookie[ key ].value or ""

   def _set_cookie(self, key, val):
      self.cookie[key] = val or self._get_cookie(key) or ""

   def _gen_session_cookie(self):
      import time
      return time.time()

   def _get_session_cookie(self):
      return self._get_cookie("_session") or self._gen_session_cookie()

   def _set_session_cookie(self, key="_session", val=""):
      self._set_cookie(key, val or self._get_cookie(key) or self._gen_session_cookie())

   def _init_session_cookie(self):
      self._set_session_cookie("_session", self._get_session_cookie())


   def do_OPTIONS(self):
      self.send_response(200)
      self._set_cors()
      self.end_headers()


   def do_GET(self):
      return super().do_GET()


   def do_POST(self):
      # local variables
      type    = CONTENT_TYPE
      message = "***failed***\n" # string
      form    = cgi.FieldStorage(
         fp=self.rfile,
         headers=self.headers,
         environ={"REQUEST_METHOD": "POST"}
      )
      self._get_headers()

      # routing: call the corresponding method each URL path
      if self.path == "/api/lsform/v1":
         message = self.lsform(form)
      if self.path == "/api/upload/v1":
         message = self.upload(form)
      if self.path == "/api/cart/v1":
         message = self.cart(form)

      # set "Content-Type" http header field
      self._set_headers(type)
      # append debug info
      sid      = self._get_session_cookie()
      message += "\n\n{}\n".format(wwwpyUtils().debuginfo(type, sid))
      # return the message (STRING) to the browser
      self.wfile.write(bytes(message, "utf8"))


   # LSFORM = LiSt FORM key,value(s) as HTML TABLE
   def lsform(self, form):
      msg = ""    # return string
      msg = msg + "<p>list up form values\n"
      msg = msg + "<table border=0 frame=void cellspacing=30>\n"

      # check all FORM key,value and create a table row for each key,value
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
      return "uploaded: {} bytes written\n".format(count)


   # Exercise Template: Janken program web version
   # - hint: kekka = (3 + jibun - aite) % 3
   # - return value: STRING
   def janken(self,form):
      # (1)
      # (2)
      # (3)
      # (4)
      pass


   # Exercise Template: the simplest shopping cart
   # - return value: STRING
   def cart(self,form):
      # (1) INPUT
      user_id = "b2xxyyyy"
      session = self._get_session_cookie()
      # (1A)

      # (2) DO
      import bws
      cache = bws.cacheInit(redisHost, redisPort, redisPass, session)
      # (2A)

      # (3) OUTPUT
      msg = "<p>shopping cart\n<table border=0 frame=void cellspacing=30>\n"

      # (3A)
      for r_key in sorted(bws.cacheSmembers(cache, session)):
         msg = msg + "<tr><td>{}<td>{}</tr>\n".format(r_key,r_val)

      msg = msg + "</table>\n"
      return msg


   # Exercise Template: ISBN search by using OpenBD
   # - return value: STRING
   #     - hint: json.dumps() convert DICT to STRING
   def openbd(self,form):
      # (1)
      # (2)
      # (3)
      # (4)
      data = {} # dict
      return json.dumps(data, ensure_ascii=False)


   # Exercise Template: AWS Rekognition
   # - return value: STRING
   def rekognition(self, form):
      label = ""
      # (1)
      # (2)
      # (3)
      # (4)
      return label


#
# WWW server (HTTP) class definition ENDS
#
############################################################
#
# Utilities
#

# www.py specific utilities
# - If you read this, you must be interested in IT infrastructure ?
#   Welcome to H205 IT infra club :-)
# - You do not need to understand this for the lectures.
class wwwpyUtils:
    def __init__(self):
        pass

    def version(self):
       return "$Revision: 1.84 $".split(" ")[1]

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

    def gethostname(self):
       return socket.gethostname()

    def debuginfo(self, type, session_id=""):
       vers = self.version()
       host = self.gethostname()
       port = HTTP_PORT
       _msg = "www.py v{} serving at {}:{}/tcp".format(vers, host, port)
       if session_id is not None:
          _msg += " (session_id = {})".format(session_id)
       if   type == "text/html":
          # return "<!-- (debug) {} -->".format(_msg)
          return "<HR>(debug) {}".format(_msg)
       elif type == "application/json":
          data = { "(debug)": _msg }
          return json.dumps(data, ensure_ascii=False)
       elif type == "text/plain":
          return "(debug) " + _msg
       else:
          return "(debug) " + _msg

############################################################
#
# MAIN
#
if __name__ == "__main__":
   # not recommended but may be allowed since this practice is for personal use only.
   socketserver.TCPServer.allow_reuse_address = True

   # run python www server (httpd)
   with socketserver.TCPServer((HTTP_HOST, HTTP_PORT), httpHandler) as httpd:
      print(wwwpyUtils().debuginfo("text/plain"), file=sys.stderr)

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
