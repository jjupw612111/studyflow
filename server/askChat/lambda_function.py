#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import boto3
import os
import datatier
from openai_helper_requests import openai_sheet_helper 

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: studyhelper_askChat**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'studyhelper-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    openai_key = configur.get('openai', 'openai_api_key')
    #
    # get body of request:
    # - projectid
    # - question
    #
    print("**Accessing request body**")
    
    if "body" not in event:
      raise Exception("event has no body")
      
    body = json.loads(event["body"]) # parse the json
    
    if "projectid" not in body:
      raise Exception("event has a body but no projectid")
    if "question" not in body:
      raise Exception("event has a body but no question")

    projectid = body['projectid']
    question = body['question'] 
    
    print("projectid:", projectid)
    print("question:", question)

 
    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # TODO: check if projectid is in the db
    #
    print("**Checking if projectid exists**")
    sql = "SELECT * from projects WHERE projectid = %s;"
    rows = datatier.retrieve_all_rows(dbConn, sql, [projectid])
    if len(rows) == 0:
      raise Exception("projectid not found in projects table")

    #
    # TODO: add question to conversations table 
    #
    print("**Adding question to conversations**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    # returns number of rows modified
    mods = datatier.perform_action(dbConn, sql, [question, projectid, "user"])
    if mods == 0:
      raise Exception("failed to insert question into conversations table")

    #
    # TODO: select all messages from conversations table where projectID = projectid; gets content for chatgpt
    #
    print("**Retrieving data**")
    sql = "SELECT * from conversations WHERE projectid = %s"
    rows = datatier.retrieve_all_rows(dbConn, sql, [projectid])
    for row in rows:
      print(row)
    
    #index 3 is the message
    content = " ".join([row[3] for row in rows])
    print("content given to ChatGPT:",content)

    #
    # TODO: send the messages to OpenAI to get a response
    #
    print("**Sending data to OpenAI**")
    gen_text = openai_sheet_helper(question, content, openai_key, 1) 

    #
    # TODO: store response in conversations table
    #
    print("**Store response**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    mods = datatier.perform_action(dbConn, sql, [gen_text, projectid, "assistant"])
    if mods == 0:
      raise Exception("failed to insert ChatGPT response into conversations table")


    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning ChatGPT response**")
    
    return {
      'statusCode': 200,
      'body': gen_text
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
