#
# Takes a user input for : list of topics and projectID
# outputs a cheat sheet pdf
#
import json
import boto3
import os
import datatier
from openai_helper_requests import openai_sheet_helper 
from configparser import ConfigParser
from xml2pdf import xml2pdf 

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
    # TODO: Upload that txt of response to s3
    s3_profile = 's3readwrite'
    boto3.setup_default_session(profile_name=s3_profile)
    bucketname = configur.get('s3', 'bucket_name')
    print(bucketname)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)
    print(f"bucketname: {bucketname}")
    
    
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
    # open connection to the database:
    #
  
    #
    #TODO: Retrieve the list of topics and projectID from client
    #
    #
    # get body of request:
    # - projectid
    # - topics
    #
    print("**Accessing request body**")
    
    if "body" not in event:
      raise Exception("event has no body")
      
    body = json.loads(event["body"]) # parse the json
    
    if "projectid" not in body:
      raise Exception("event has a body but no projectid")
    if "topics" not in body:
      raise Exception("event has a body but no topics")

    projectid = body['projectid']
    topics = body['topics'] 
    
    print("projectid:", projectid)
    print("topics:", topics)

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
    # TODO: add topcs to conversations
    #
    print("**Adding topics to conversations**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    # returns number of rows modified
    mods = datatier.perform_action(dbConn, sql, [topics, projectid, "user"])
    if mods == 0:
      raise Exception("failed to insert topics into conversations table")
    
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
    gen_text = openai_sheet_helper(topics, content, openai_key, 2) 
    #
    # TODO: store response in conversations table
    #
    print("**Store response**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    mods = datatier.perform_action(dbConn, sql, [gen_text, projectid, "assistant"])
    if mods == 0:
      raise Exception("failed to insert ChatGPT response into conversations table")


    #
    # TODO: find bucketfolder for projectid
    #
    print("**Find bucketfolder**")
    sql = "SELECT bucketfolder from projects WHERE projectid = %s;"
    bucketfolder = datatier.retrieve_one_row(dbConn, sql, [projectid])[0]
    bucket_name = bucketfolder.split('/')[0]  # The first part is the bucket name
    folder_path = '/'.join(bucketfolder.split('/')[1:]).rstrip('/')  
    object_key = f"{folder_path}result/result.txt"
    print(f"object_key: {object_key}")

    print(f"bucketfolder: {bucketfolder}")
    if len(row) == 0:
      raise Exception("projectid not found in projects table")
    
    print("**Setup S3**")

    local_file_name = "/tmp/results.txt"

    print("**Write to file system**")
    with open(local_file_name, 'w') as file:
      file.write(gen_text)

    # Prepare object key
    bucket_name = bucketfolder.split('/')[0]  # First part is the bucket name
    folder_path = '/'.join(bucketfolder.split('/')[1:]).rstrip('/')
    object_key = f"{folder_path}/result/result.txt"  # Adjust the path

    print(f"Uploading to bucket: {bucket_name}, key: {object_key}")
    print("TRY THIS: ", bucket_name+'/'+object_key)
    # Upload the file
    bucket.upload_file(
        local_file_name,
        bucket_name+'/'+object_key,
        ExtraArgs={
            'ACL': 'public-read',
            'ContentType': 'text/plain'
        }
    )

    # #hard-coded inputs for testing:
    # with open('sample2.txt', 'r') as file:
    #   content = file.readlines()
    # with open('topics2.txt', 'r') as file:
    #   topics_list = file.readlines()
    # #
    # # Call openai api with the provided topics, content, and key
    # #
    # gen_text = openai_sheet_helper(topics_list, content, openai_key, 2) #we need projectID to get the relevant text for the document 


    # 
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning generated text**")

    print("**uploading to tmp storage...")
    xml2pdf()
    
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


#test
lambda_handler("test","test")