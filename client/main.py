#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law.
#
# Authors:
#   << YOUR NAME >>
#
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import random

from utils import web_service_get, web_service_post

from configparser import ConfigParser


############################################################
#
# classes
#
class User:
  def __init__(self, row):
    self.userid = row[0]
    self.email = row[1]
    self.lastname = row[2]
    self.firstname = row[3]

class Project:
  def __init__(self, row):
    self.projectid = row[0]
    self.userid = row[1]
    self.projectname = row[2]
    self.bucketfolder = row[3]

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => users")
    print("   2 => create user")
    print("   3 => projects")
    print("   4 => pdfs")
    print("   5 => upload")
    print("   6 => ask chat")
    print("   7 => merge")
    print("   8 => cheatsheet")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()

    #
    # let's map each row into a User object:
    #
    users = []
    for row in body:
      user = User(row)
      users.append(user)
    #
    # Now we can think OOP:
    #
    if len(users) == 0:
      print("no users...")
      return

    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.firstname, user.lastname)
    #
    return

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
#
# create user
#
def createUser(baseurl):
  """
  Prompts the user for a email, first name, and last name.
  Inserts this user into our users table.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  userid: the id of the user we just created
  """

  try:
    #
    # Prompt user
    #
    print("Enter first name>")
    firstname = input()

    print("Enter last name>")
    lastname = input()

    print("Enter email>")
    email = input()

    #
    # Call the web service
    #
    data = {"email": email, 
            "lastname": lastname, 
            "firstname": firstname}
    api = '/createuser'
    url = baseurl + api
    res = web_service_post(url, data)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else: #failed
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      return

    #
    # success, we get the userid back
    #
    body = res.json()

    print("success:", body)

    return body

  except Exception as e:
    logging.error("**ERROR: createUser() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# projects
#
def projects(baseurl):
  """
  Given the userid,
  Prints out all the projects of a user

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # Prompt user
    #
    print("Enter userid>")
    userid = input()

    #
    # call the web service:
    #
    api = '/projects'
    url = baseurl + api + "/" + userid
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract projects:
    #
    body = res.json()

    #
    # let's map each project into a Project object:
    #
    projects = []
    for row in body:
      proj = Project(row)
      projects.append(proj)
      
    #
    # Now we can think OOP:
    #
    if len(projects) == 0:
      print("no projects...")
      return

    for project in projects:
      print(project.projectid)
      print(" ", project.userid)
      print(" ", project.projectname)
      print(" ", project.bucketfolder)
    return

  except Exception as e:
    logging.error("**ERROR: projects() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

  ############################################################
#
# ask chat
#
def askchat(baseurl):
  """
  Given the projectid and question,
  Print answer from ChatGPT to question using messages with projectid

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # Prompt user
    #

    print("Enter projectid>")
    projectid = input()

    print("Enter question>")
    question = input()

    #
    # call the web service:
    #
    api = '/askchat/'
    url = baseurl + api 
    data = {"projectid":projectid, "question":question}
    #
    # call the web service:
    #
    res = web_service_post(url, data)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract projects:
    #
    response = res.json() #causes users failed
    
    #print answer:
    print(f"Answer from ChatGPT: {response}")

    return

  except Exception as e:
    logging.error("**ERROR: askchat() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
  
  
############################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (PDF) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  The filename in S3
  """

  try:
    print("Enter PDF filename>")
    local_filename = input()

    if not pathlib.Path(local_filename).is_file():
      print("PDF file '", local_filename, "' does not exist...")
      return

    print("Enter user id>")
    userid = input()

    print("Enter project name>")
    projectname = input()

    #
    # build the data packet. First step is read the PDF
    # as raw bytes:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the pdf as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    # write to outfile
    outfile = open("out.out", "w")
    outfile.write(datastr)
    outfile.close()

    data = {"projectname": projectname, 
            "filename": local_filename, 
            "data": datastr}

    #
    # call the web service:
    #
    url = baseurl + '/pdf/' + userid
    res = web_service_post(url, data)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    elif res.status_code == 400: # no such user
      body = res.json()
      print(body)
      return
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, we get the filename in s3 back
    #
    body = res.json()

    print("success:", body)

    return body

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

##########################################################
#
# pdfs
#
def pdfs(baseurl):
  """
  Given a project id, tells you what pdfs are in it.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  pass

##########################################################
#
# merge
#
def merge(baseurl):
  """
  Merge all the pdfs in a project into a single pdf.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  try:
    #
    # Get user input
    #
    print("Enter project id>")
    projectid = input()
    print("Enter local filename of downloaded file>")
    local_filename = input()
    # file already exists: append 1 to filename
    if pathlib.Path(local_filename).is_file():
      local_filename = local_filename + " (1)"

    #
    # Call web service
    #
    data = {"projectid": projectid}
    api = '/merge/'
    url = baseurl + api
    res = web_service_post(url, data)
    
    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      return
    
    #
    # success, we got pdf datastr back
    #
    datastr = res.json()

    #
    # write binary data to a local file
    #
    bytes = base64.b64decode(datastr)
    outfile = open(local_filename, "wb")
    outfile.write(bytes)
    print("Downloaded merged pdf and saved as '", local_filename, "'")
    
  except Exception as e:
    logging.error("**ERROR: merge() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

##########################################################
#
# cheatsheet
#
def cheatsheet(baseurl):
  """
  Given a list of topics and a project id, 
  generates and downloads a cheat sheet to help you
  study those topics.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  pass

############################################################
# main
#
try:
  print('** Welcome to Study Helper **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'studyhelper-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      createUser(baseurl)
    elif cmd == 3:
      projects(baseurl)
    elif cmd == 4:
      pdfs(baseurl)
    elif cmd == 5:
      upload(baseurl)
    elif cmd == 6:
      askchat(baseurl)
    elif cmd == 7:
      merge(baseurl)
    elif cmd == 8:
      cheatsheet(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
