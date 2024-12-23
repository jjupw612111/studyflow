#
# Takes a user input for : list of topics and projectID
# outputs a cheat sheet pdf
#
import json
import base64
import boto3
import os
import datatier
from openai_helper_requests import openai_sheet_helper 
from configparser import ConfigParser
from xml2pdf_complex import xml2pdf_complex

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
    #  Upload file to s3
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
    # Retrieve the list of topics and projectID from client
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
    #  check if projectid is in the db
    #
    print("**Checking if projectid exists**")
    sql = "SELECT * from projects WHERE projectid = %s;"
    rows = datatier.retrieve_all_rows(dbConn, sql, [projectid])
    if len(rows) == 0:
      raise Exception("projectid not found in projects table")
    
    #
    #  add topcs to conversations
    #
    print("**Adding topics to conversations**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    # returns number of rows modified
    mods = datatier.perform_action(dbConn, sql, [topics, projectid, "user"])
    if mods == 0:
      raise Exception("failed to insert topics into conversations table")
    
    #
    #  select all messages from conversations table where projectID = projectid; gets content for chatgpt
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
    #  send the messages to OpenAI to get a response
    #
    print("**Sending data to OpenAI**")
    gen_text = openai_sheet_helper(topics, content, openai_key, 2) 
    #
    #  store response in conversations table
    #
    print("**Store response**")
    sql = "INSERT INTO conversations (message, projectid,role,timestamp) VALUES (%s, %s, %s, NOW());"
    mods = datatier.perform_action(dbConn, sql, [gen_text, projectid, "assistant"])
    if mods == 0:
      raise Exception("failed to insert ChatGPT response into conversations table")


    #
    #  find bucketfolder for projectid
    #
    print("**Find bucketfolder**")
    sql = "SELECT bucketfolder from projects WHERE projectid = %s;"
    bucketfolder = datatier.retrieve_one_row(dbConn, sql, [projectid])[0]
    bucket_name = bucketfolder.split('/')[0]  # The first part is the bucket name
    folder_path = '/'.join(bucketfolder.split('/')[1:]).rstrip('/')  
    object_key = f"{folder_path}result/result.pdf"
    print(f"object_key: {object_key}")

    print(f"bucketfolder: {bucketfolder}")
    if len(row) == 0:
      raise Exception("projectid not found in projects table")
    
    print("**Setup S3**")
   
    print("**uploading to tmp storage...")
    xml2pdf_complex(gen_text)
    pdf_file_name = "/tmp/cheatsheet.pdf"
    print("**cheat sheet stored in tmp storage at :", pdf_file_name)

    print(f"Uploading to bucket: {bucket_name}, key: {object_key}")
    print("path:",bucket_name+'/'+object_key)
    # Upload the file
    bucket.upload_file(
        pdf_file_name,
        bucket_name+'/'+object_key,
        ExtraArgs={
            'ACL': 'public-read',
            'ContentType': 'application/pdf'
        }
    )
    print("successfully uploaded to s3 at: ", bucket_name+'/'+object_key)

    #generate datastr byte string to respond with
    print("**Serializing the cheatsheet pdf**")

    infile = open(pdf_file_name, "rb")
    bytes = infile.read()
    infile.close()

    data = base64.b64encode(bytes)
    datastr = data.decode()

    # 
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning generated byte string in response**")
    
    return {
      'statusCode': 200,
      'body': json.dumps(datastr)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
