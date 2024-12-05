import openai
import os

def openai_sheet_helper(question, content, api_key):
    client = openai.OpenAI( api_key= api_key)


    # Define the prompt
    prompt = f"""
You are an assistant tasked with answering a student's question based solely on the lecture notes provided, ignoring any previous questions or answers in the merged text. Below is a combined text string containing both the lecture notes and the history of previous questions. Please focus only on the lecture notes section to answer the current question accurately and concisely.

### Merged Text:
{content}
### Current Student Question:
{question}
### Instructions:
1. Extract and use only the relevant content from the lecture notes section of the merged text to answer the question.
2. Ignore any content related to previous questions or answers.
3. Provide a detailed and accurate answer in a clear and concise manner.

### Answer:

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

#test:
#openai_sheet_helper("hi", "hello how are you", api_key)