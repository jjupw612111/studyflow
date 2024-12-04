#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

# /merge/{userid}/{projectid}
def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: studyhelper_merge**")
    
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
    # configure for s3 access
    #
    s3_profile = 's3readwrite'
    boto3.setup_default_session(profile_name=s3_profile)
    
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname) 

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
    #
    print("**Accessing request body**") 

    if "body" not in event:
      raise Exception("event has no body") 
    body = json.loads(event["body"]) # parse the json 
    if "projectname" not in body:
      raise Exception("event has a body but no projectname")
    projectname = body["projectname"]    
    print("projectname:", projectname)


    #
    # open connection to the database:
    #
    print("**Opening connection**") 
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # TODO: get s3 bucket folder for the project
    #
    print("**Retrieving s3 bucketfolder**")
    sql = """
      SELECT bucketfolder FROM projects JOIN users ON projects.userid = users.userid WHERE userid = %s AND projectname = %s;
    """
    row = datatier.retrieve_one_row(dbConn, sql, [userid, projectname])
    if len(row) == 0:
      raise Exception("bucketfolder not found")
    bucketfolder = row[0]
    print("bucketfolder:", bucketfolder) 

    #
    # TODO: download each pdf at a time, merge it
    #
    
    #
    # TODO: resulting merged pdf uploaded to s3
    # in results folder
    #

    #
    # TODO: return the s3 download url
    # 

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning rows**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("hello world")
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
