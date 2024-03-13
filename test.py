import json
from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')


client = OpenAI(api_key=api_key)

# Read JSON data from file
def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data



def invoke_openai_chat(json_data, prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": json.dumps(json_data)},
        {"role": "assistant", "content": prompt},
    ])
    return response.choices[0].message.content


def main():

    json_data = read_json('nirju.json')
    
    

    prompt = """ You are a company hate speech detector that only speaks in JSON. Do not generate output that isn't in properly formatted JSON.
                
                Your task is to analyse the data and return me results based on the hate speech of following types:
                    - Racial Hate Speech
                    - Homophobic and Transphobic Speech
                    - Religious Hate Speech
                    - Sexist Speech
                    - Ableist Speech
                    
                Results should be in the format:

            {
                    "totalComments": "number of total comments analysed",
                    "numberOfHateComments": "number of hate comments based on above points",
                    "racialHateSpeech": "number of comments that contain racial hate speech",
                    "homophobicTransphobicSpeech": "number of comments that contain homophobic or transphobic hate speech",
                    "religiousHateSpeech": "number of comments that contain religious hate speech",
                    "sexistSpeech": "number of comments that contain sexist speech",
                    "ableistSpeech": "number of comments that contain ableist speech",
                    "hateComments": [
                        {
                            "text": "actual comment",
                            "username": "username of user commenting",
                            "profileName": "profile name of user commenting",
                            "reason": "reason why the following comment was a hate comment",
                            "hateOn": ["list of types of hate speech that was triggered"],
                            "hatePercentage": "percentage in which the hate is from 1 to 100 how harsh is it"
                        }
                    ]
                }

                If no comments are there, simply write in the Summary section: "No Comments". Do not make stuff up.
                If there are no hate comments made just give the json with empty values. 
"""

    response = invoke_openai_chat(json_data, prompt)

    print("Response:", response)

if __name__ == "_main_":
    main()
    
    
    
    {
    "prompt": "Given a JSON object representing comments on a social media post, analyze each comment to identify hate speech. Compute the following statistics:\n\n1. Total number of comments.\n2. Number of comments containing racial hate speech.\n3. Number of comments containing homophobic or transphobic hate speech.\n4. Number of comments containing religious hate speech.\n5. Number of comments containing sexist speech.\n6. Number of comments containing ableist speech.\n7. Total number of hate comments.\n8. If hate comments are found, provide details of each hate comment including the text, username, profile name, reason for classification as hate speech, types of hate speech identified, and a measure of the intensity of hate speech.\n\nEnsure that the hate speech detection is sensitive to context and nuances, and that the intensity measure reflects the severity of the hate speech. Output the results in the following format:\n\n```json\n{\n    \"totalComments\": \"\",\n    \"racialHateSpeech\": \"\",\n    \"homophobicTransphobicSpeech\": \"\",\n    \"religiousHateSpeech\": \"\",\n    \"sexistSpeech\": \"\",\n    \"ableistSpeech\": \"\",\n    \"numberOfHateComments\": \"\",\n    \"hateComments\": [\n        {\n            \"text\": \"\",\n            \"username\": \"\",\n            \"profileName\": \"\",\n            \"reason\": \"\",\n            \"hateOn\": [],\n            \"hatePercentage\": \"\"\n        }\n    ]\n}\n```"
}
