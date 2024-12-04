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
    print("**lambda: studyhelper_createUser**")
    
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
    # get body of request:
    # - email
    # - lastname
    # - firstname
    #
    print("**Accessing request body**")
    
    if "body" not in event:
      raise Exception("event has no body")
      
    body = json.loads(event["body"]) # parse the json
    
    if "email" not in body:
      raise Exception("event has a body but no email")
    if "lastname" not in body:
      raise Exception("event has a body but no lastname")
    if "firstname" not in body:
      raise Exception("event has a body but no fistname")

    email = body["email"]
    lastname = body["lastname"]
    firstname = body["firstname"]
    
    print("email: " + email)
    print("lastname: " + lastname)
    print("firstname: " + firstname)

    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # insert into users table
    #
    print("**Inserting into users table**")
    sql = "INSERT INTO users (email, lastname, firstname) VALUES (%s, %s, %s);" 
    # returns number of rows modified
    mods = datatier.perform_action(dbConn, sql, [email, lastname, firstname])
    if mods == 0:
      raise Exception("failed to insert row into projects")
    # get the userid of new user
    sql = "SELECT userid FROM users WHERE email = %s"
    row = datatier.retrieve_one_row(dbConn, sql, [email]) 
    if len(row) == 0:
      raise Exception("insertion error: new user not found")
    userid = row[0]
    print("userid: " + str(userid))

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning new userid**")
    
    return {
      'statusCode': 200,
      'body': json.dumps(userid)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
