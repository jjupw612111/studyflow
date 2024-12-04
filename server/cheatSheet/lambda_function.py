#
# Takes a user input for : list of topics and projectID
# outputs a cheat sheet pdf
#

import json
import boto3
import os
import datatier
from openai_helpers import openai_sheet_helper 
from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: cheatSheet**")
    #
    # setup AWS based on config file:
    #
    config_file = 'studyhelper-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)

    # #
    # # configure for RDS access
    # #
    # rds_endpoint = configur.get('rds', 'endpoint')
    # rds_portnum = int(configur.get('rds', 'port_number'))
    # rds_username = configur.get('rds', 'user_name')
    # rds_pwd = configur.get('rds', 'user_pwd')
    # rds_dbname = configur.get('rds', 'db_name')

    # #
    # # open connection to the database:
    # #
    # print("**Opening connection**")
    
    # dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #get information from user:
    print("input the list of topics")
    topics_list = input()
    print("input the project ID to retrieve the data from S3")
    project_id = input()

    #
    # now retrieve the text from the conversations table:
    #
    print("**Retrieving data**")
    #TODO: retrieve the text from the conversations table 

    with open("sample.txt", "r") as file:
      content = file.read()
      print(content)
    
    gen_text = openai_sheet_helper(topics_list, content) #we need projectID to get the relevant text for the document 

    # 
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning generated text**")
    
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
