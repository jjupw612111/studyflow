#
# Retrieves and returns all the users in the 
# BenfordApp database.
#

import json
import base64
import boto3
import os
import datatier

from configparser import ConfigParser
from pypdf import PdfWriter

# /merge/{userid}
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
    print("--userid:", userid)

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
    print("--projectname:", projectname)


    #
    # open connection to the database:
    #
    print("**Opening connection**") 
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # get a list of project filenames in s3 we need to merge
    #
    print("**Retrieving s3 bucketfolder**")
    sql = """
      SELECT filename FROM projects 
                      JOIN users ON projects.userid = users.userid 
                      JOIN projectdocs ON projects.projectid = projectdocs.projectid
      WHERE users.userid = %s AND projectname = %s;
    """
    rows = datatier.retrieve_all_rows(dbConn, sql, [userid, projectname])
    if len(rows) == 0:
      raise Exception("no project docs found")
    print("--Found", len(rows), "files in project") 

    #
    # download all project files to tmp, collecting filenames
    #
    tmpfiles = []
    for i, row in enumerate(rows):
      bucketkey = row[0]
      print("**DOWNLOADING '", bucketkey, "'**")
      local_pdf_name = "/tmp/" + i + ".pdf"
      bucket.download_file(bucketkey, local_pdf_name)
      tmpfiles.append(local_pdf_name)

    #
    # Merge the pdfs
    #
    print("**Merging pdfs**")
    mergedTmp = "/tmp/merged-pdf.pdf"
    merger = PdfWriter()
    for pdf in tmpfiles:
        merger.append(pdf)
    merger.write(mergedTmp)
    merger.close()
    print("--Merge complete")
    
    #
    # Retrieve the bucketfolder of the project
    #
    print("**Retrieving project bucketfolder**")
    sql = """
      SELECT bucketfolder FROM projects 
                          JOIN users ON projects.userid = users.userid 
      WHERE users.userid = %s AND projectname = %s;
    """
    rows = datatier.retrieve_one_row(dbConn, sql, [userid, projectname])
    if len(rows) == 0:
      raise Exception("no project docs found")
    bucketfolder = rows[0]
    print("--Bucketfolder:", bucketfolder)

    #
    # Generate s3 filename of merged pdf
    #
    print("**Generating s3 filename of merged pdf**")
    mergedS3 = bucketfolder + "result/merged-pdf.pdf"
    print("--S3 filename:", mergedS3)

    #
    # Upload the merged pdf to s3
    #
    print("**Uploading file to s3**")
    bucket.upload_file(mergedTmp, 
                       mergedS3, 
                       ExtraArgs={
                         'ACL': 'public-read',
                         'ContentType': 'application/pdf'
                       }) 

    #
    # serialize merged pdf
    #
    print("**Serializing merged pdf**")

    infile = open(mergedTmp, "rb")
    bytes = infile.read()
    infile.close()

    data = base64.b64encode(bytes)
    datastr = data.decode()

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning merged pdf datastr**") 
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
