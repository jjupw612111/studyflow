import openai
import os

def openai_sheet_helper(topics, content, api_key):
    client = openai.OpenAI( api_key= api_key)


    # Define the prompt
    prompt = f"""
    Below, you are given two pieces of information. First, content for which we want you to make a review sheet.
    Second, a list of topics for making a review sheet. Please output a review sheet where for each topic, you list
    the topic and the relevant information about it.
    Content: {content}
    List of Topics: {topics}
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": prompt
            }
            ]
        }
        ]
    )
    
    gentext = completion.choices[0].message.content
    print(gentext)
    return gentext
