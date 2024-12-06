#
# Retrieves and returns all the projects for given userid in the 
# studyhelper database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

# GET /pdfs/{projectid}
def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: studyhelper_pdfs**")
    
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
    # get projectid from path
    #
    print("**Accessing event/pathParameters**")

    if "projectid" in event:
      projectid = event["projectid"]
    elif "pathParameters" in event:
      if "projectid" in event["pathParameters"]:
        projectid = event["pathParameters"]["projectid"]
      else:
        raise Exception("requires projectid parameter in pathParameters")
    else:
        raise Exception("requires projectid parameter in event") 
    print("projectid:", projectid)
  
    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # check that projectid is valid:
    #
    print("**Checking if projectid is valid**")
    
    sql = "SELECT * FROM projects WHERE projectid = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [projectid])
    
    if row == ():  # no such project
      print("**No such project, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such project...")
      } 

    #
    # Get all pdf filenames for this project from RDS
    #
    print("**Getting pdf filenames from this project**")
    sql = "SELECT * from projectdocs WHERE projectid = %s ORDER BY projectid;"
    
    rows = datatier.retrieve_all_rows(dbConn, sql, [projectid])
    
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
