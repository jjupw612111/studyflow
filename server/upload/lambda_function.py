#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import boto3
import uuid
import pathlib
import base64
import os
import datatier

from configparser import ConfigParser
from pypdf import PdfReader

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
    # - filename
    # - data
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
    # Open connection to RDS
    #
    print("**Opening connection to RDS**") 
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # get user
    #
    print("**Retrieving user**")
    sql = "SELECT * from users WHERE userid = %s;"
    row = datatier.retrieve_one_row(dbConn, sql, [userid])
    if len(row) == 0:
      raise Exception("user not found")
    print("user:", row)
    username = row[3]    

    #
    # get the project id
    # if project does not already exist, create it
    #
    print("**Retrieving existing project**") 
    get_projectid_sql = "SELECT * from projects WHERE projectname = %s;"; 
    row = datatier.retrieve_one_row(dbConn, get_projectid_sql, [projectname])
    
    if len(row) == 0:
      print("**Creating new project**") 
      bucketfolder = "studyhelper/" + username + "-" + userid + "/" + projectname + "-" + projectid + "/"
      sql = "INSERT INTO projects (projectname, bucketfolder, userid) VALUES (%s, %s, %s);"
      # returns number of rows modified
      mods = datatier.perform_action(dbConn, sql, [projectname, bucketfolder, userid])
      if mods == 0:
        raise Exception("failed to insert row into projects")
      # get the projectid
      row = datatier.retrieve_one_row(dbConn, get_projectid_sql, [projectname])
      if len(row) == 0:
        raise Exception("something went teribly wrong with creating project")
      print("**Retrieved project:", row) 
    else:
      print("**Retrieved project:", row) 
    
    projectid = row[0]
    bucketfolder = row[3]

    #
    # prepare for s3 upload
    #

    print("**Generating raw bytes**")
    base64_bytes = datastr.encode()        # string -> base64 bytes
    bytes = base64.b64decode(base64_bytes) # base64 bytes -> raw bytes
    
    print("**Writing local data file**")
    local_filename = "/tmp/data.pdf"
    outfile = open(local_filename, "wb")
    outfile.write(bytes)
    outfile.close()
    
    print("**Generating unique s3 filename**")
    basename = pathlib.Path(filename).stem
    extension = pathlib.Path(filename).suffix 
    if extension != ".pdf" : 
      raise Exception("expecting filename to have .pdf extension") 
    s3filename = bucketfolder + basename + "-" + str(uuid.uuid4()) + ".pdf"  
    print("S3 file name:", s3filename)
    
    #
    # update projectdocs table
    #
    print("**Updating projectdocs table**") 
    sql = """
      INSERT INTO projectdocs(filename, projectid) VALUES(%s, %s);
    """
    mods = datatier.perform_action(dbConn, sql, [s3filename, projectid])
    if mods == 0:
      raise Exception("failed to insert row into projectdocs")
    print("**Inserted into projectdocs**") 

    #
    # upload the file to s3
    #
    print("**Uploading file to s3**")
    bucket.upload_file(local_filename, 
                      s3filename, 
                      ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': 'application/pdf'
                      })
    

    #
    # extract text of uploaded file
    #
    print("**Extracting text from pdf**")
    reader = PdfReader(local_filename)
    number_of_pages = len(reader.pages)

    texts = ""
    for i in range(0, number_of_pages):
      page = reader.pages[i]
      text = page.extract_text()
      texts += text
      print("** Page", i+1, ", text length", len(text))

    print("**DONE extracting text**")

    #
    # update conversations table
    #
    print("**Updating conversations table**") 
    sql = """
      INSERT INTO conversations(projectid, timestamp, role, message) VALUES(%s, NOW(), %s, %s);
    """
    mods = datatier.perform_action(dbConn, sql, [projectid, "user", texts])
    if mods == 0:
      raise Exception("failed to insert row into conversations")
    print("**Inserted into conversations**") 

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning filename in s3**")
    
    return {
      'statusCode': 200,
      'body': json.dumps(s3filename)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
