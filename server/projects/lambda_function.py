#
# Retrieves and returns all the projects for given userid in the 
# studyhelper database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: studyhelper_projects**")
    
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
    # userid from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
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
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # now retrieve all the projects for one user:
    #
    print("**Retrieving data**")


    #
    # first we need to make sure the userid is valid:
    #
    print("**Checking if userid is valid**")
    
    sql = "SELECT * FROM users WHERE userid = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [userid])
    
    if row == ():  # no such user
      print("**No such user, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such user...")
      }
    

    #
    # write sql query to select all projects from the 
    # users table, where userid is given
    #
    sql = "SELECT * from projects WHERE userid = %s ORDER BY projectid";
    
    rows = datatier.retrieve_all_rows(dbConn, sql, [userid])
    
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
