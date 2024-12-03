#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_users**")
    
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

    #
    # get userid from path
    #
    print("**Accessing event/pathParameters**")

    if "userid" in event:
      userid = event["userid"]
    elif "pathParameters" in event:
      if "userid" in event["pathParameters"]:
        userid = event["pathParameters"]["userid"]
      else:
        raise Exception("requires userid parameter in pathParameters")
    else:
        raise Exception("requires userid parameter in event") 
    print("userid:", userid)
    
    #
    # get body of request:
    # - projectname
    # - filename
    # - filedata
    #
    print("**Accessing request body**")
    
    if "body" not in event:
      raise Exception("event has no body")
      
    body = json.loads(event["body"]) # parse the json
    
    if "projectname" not in body:
      raise Exception("event has a body but no projectname")
    if "filename" not in body:
      raise Exception("event has a body but no filename")
    if "data" not in body:
      raise Exception("event has a body but no data")

    projectname = body["projectname"]
    filename = body["filename"]
    datastr = body["data"]
    
    print("projectname:", projectname)
    print("filename:", filename)
    print("datastr (first 10 chars):", datastr[0:10]) 

    #
    # TODO: get the project id
    # if project does not already exist, create it
    #

    #
    # TODO: upload the file to s3
    #

    #
    # TODO: upload the file to s3
    #

    #
    # TODO: update projectdocs table
    #

    #
    # TODO: extract text of uploaded file
    #

    #
    # TODO: update conversations table
    #

    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # now retrieve all the users:
    #
    print("**Retrieving data**")

    #
    # TODO #1 of 1: write sql query to select all users from the 
    # users table, ordered by userid
    #
    sql = "SELECT * from users ORDER BY userid";
    
    rows = datatier.retrieve_all_rows(dbConn, sql)
    
    for row in rows:
      print(row)

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning rows**")
    
    return {
      'statusCode': 200,
      'body': json.dumps(rows)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
