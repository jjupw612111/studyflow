#
# Takes a user input for : list of topics and projectID
# outputs a cheat sheet pdf
#
import openai
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
    print("**Opening connection**")
    #dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    #TODO: Retrieve the list of topics and projectID from client
    #


    #
    # now retrieve the text from the conversations table:
    #
    # print("**Retrieving data**")

    sql = "SELECT * from conversions WHERE projectID = %s "

    # #TODO: retrieve the text from the conversations table 
    # with open("sample.txt", "r") as file:
    #   content = file.read()
    #   print(content)

    #hard-coded inputs for testing:
    topics_list  = "rainforest trees, understory, biodiversity"
    content = '''
Tropical vegetation is a vibrant and diverse ecosystem, characterized by its lush greenery and variety of plant species. The dense, towering trees form the backbone of the tropical rainforest, creating layers of growth that foster a unique environment. These forests, found in regions close to the equator, experience consistent warmth and rainfall year-round, providing an ideal setting for plant life to thrive.

At the heart of tropical vegetation are the towering rainforest trees, such as mahogany, rubber trees, and towering hardwoods. These trees often have broad, leathery leaves to capture sunlight in the dense forest canopy. Their roots are adapted to the wet conditions, sometimes growing above ground to help with nutrient absorption. The high canopy acts as a protective layer, allowing smaller plants below to grow in the shade, while providing a habitat for a vast array of wildlife.

In addition to the towering trees, the understory of the tropical rainforest supports a variety of smaller shrubs and plants. These plants are specially adapted to grow in low light conditions, with larger leaves that help maximize photosynthesis. Ferns, orchids, and various types of moss thrive here, creating a delicate, layered ecosystem.

Tropical vegetation is also famous for its biodiversity, as the constant climate and varied plant life create an environment where species can evolve and interact. This richness supports countless forms of life, from insects to larger mammals, and even hosts some of the most spectacular flowering plants. The vibrant blossoms of tropical flowers, like hibiscus and plumeria, add a touch of color to the otherwise green landscape, attracting pollinators and adding to the ecosystem's complex web.

In summary, tropical vegetation is a dynamic and intricate system that balances towering trees, a lush understory, and a remarkable diversity of life, all nurtured by the steady warmth and rainfall characteristic of tropical climates.'''

    #
    # Call openai api with the provided topics, content, and key
    #
    gen_text = openai_sheet_helper(topics_list, content, openai_key) #we need projectID to get the relevant text for the document 
    

    # 
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning generated text**")
    
    return {
      'statusCode': 200,
      'body': 'text'
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