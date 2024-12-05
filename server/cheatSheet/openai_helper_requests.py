import requests

api_key = "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"

def openai_sheet_helper(context, content, api_key, prompt_choice):
    # Define the OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Construct the payload
    prompt_cheatsheet = f"""
    Below, you are given two pieces of information. First, content for which we want you to make a review sheet.
    Second, a list of topics for making a review sheet. Please output a review sheet where for each topic, you list
    the topic and the relevant information about it. 
    Content: {content}
    List of Topics: {context}
    """

    prompt_ask_chat = f"""
    You are a helpful study assistant. You are given study content and a question to answer about it:
    Content: {content}
    List of Topics: {context}
    """

    prompt = prompt_ask_chat if prompt_choice == 1 else prompt_cheatsheet

    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # Send the POST request to the OpenAI API
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        gentext = response.json()["choices"][0]["message"]["content"]
        print(gentext)
        return gentext
    else:
        # Handle API errors
        print(f"Error: {response.status_code} - {response.text}")
        return None

#test
#openai_sheet_helper("hi", "hello how are you", api_key)