import openai 
import os
#from dotenv import load_dotenv
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_sheet_helper(topics, content, api_key):
  openai.api_key = api_key
  client = openai.OpenAI()
  completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": f'''Below, you are given two pieces of information. First, content for which we want you to make a review sheet.
            Second, a list of topics for making a review sheet. Please output a review sheet where for each topic, you list the topic
            and the relevant information about it. 
            Content: {content}
            List of Topics: {topics}
            '''
          }
        ]
      }
    ]
  )
  gentext = completion.choices[0].message.content
  return gentext

