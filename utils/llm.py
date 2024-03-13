from langchain.agents import create_json_agent
from langchain_community.agent_toolkits import JsonToolkit
from langchain_community.tools.json.tool import JsonSpec
from langchain_openai import ChatOpenAI
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
import scraping_post

load_dotenv()

client_openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

llm_client = ChatOpenAI(model="gpt-3.5-turbo",
                        api_key=os.environ.get("OPENAI_API_KEY"), temperature=0)


def compute_comments_llm(data):
    COMMENT_PROMPT = """You've been assigned the task of analyzing comments for hate speech and you can only talk JSON format. Your analysis should encompass the following:

    - Total number of comments 
    - Number of comments containing racial hate speech
    - Number of comments containing homophobic or transphobic hate speech
    - Number of comments containing religious hate speech
    - Number of comments containing sexist speech
    - Number of comments containing ableist speech
    - Total number of hate comments
    - Details of each hate comment including text, username, profile name, reason, types of hate speech, and hate intensity

    Results should adhere to this structure:

    ```json
    {
        "totalComments": "Total number of comments in JSON format",
        "racialHateSpeech": "Number of comments with racial hate speech",
        "homophobicTransphobicSpeech": "Number of comments with homophobic or transphobic hate speech",
        "religiousHateSpeech": "Number of comments with religious hate speech",
        "sexistSpeech": "Number of comments with sexist speech",
        "ableistSpeech": "Number of comments with ableist speech",
        "numberOfHateComments": "Total number of hate comments",
        "hateComments": [
            {
                "text": "Content of the hate comment",
                "timeStamp":"Time of the comment in YY/MM/DD HH:MM:SS format",
                "username": "Username of the commenter",
                "profileName": "Profile name of the commenter",
                "reason": "Reason for classifying the comment as hate speech",
                "hateOn": ["Types of hate speech identified"],
                "hatePercentage": Intensity of hate speech (percentage) in integer
            }
        ]
    }
    ```

    For the summary:
    - If there are no comments, output: "No Comments".
    - If there are no hate comments, provide JSON with empty values.
    """

    json_spec = JsonSpec(dict_=data, max_value_length=4000)
    json_toolkit = JsonToolkit(spec=json_spec)

    json_agent_executor = create_json_agent(
        llm=llm_client, toolkit=json_toolkit, verbose=True
    )

    response = json_agent_executor.run(
        COMMENT_PROMPT
    )

    print(response)
    return response


def invoke_openai_chat(json_data, prompt):
    response = client_openai.chat.completions.create(model="gpt-3.5-turbo", temperature=0, messages=[
        {"role": "system",
         "content": "You are a helpful assistant."},
        {"role": "user", "content": json.dumps(
            json_data)},
        {"role": "assistant",
         "content": prompt},
    ])
    return response.choices[0].message.content


def compute_caption_llm(data):
    CAPTION_PROMPT = """You've been assigned the task of analyzing hate speech in YouTube videos, and you're required to present your findings in JSON format. Your analysis should cover the following aspects:
    - Determine if there is hate speech in the video title.
    - Identify hate speech in the video comments.
    - Extract sections of the video description containing:
    - Racial hate speech
    - Homophobic or transphobic hate speech
    - Religious hate speech
    - Sexist speech
    - Ableist speech
    - Determine the intensity of hate speech in the video description as a percentage.
    - Determine if there is hate speech in the video captions.
    - Extract sections of the video captions containing:
    - Racial hate speech
    - Homophobic or transphobic hate speech
    - Religious hate speech
    - Sexist speech
    - Ableist speech
    - Determine the intensity of hate speech in the video captions as a percentage.
    - Calculate the overall percentage of hate speech in the video.
    Results should adhere to this structure:
    ```json
    {
        "sections": {
            "description": {
                "racial_hate_speech": "Section of description containing racial hate speech",
                "homophobic_transphobic_hate_speech": "Section of description containing homophobic or transphobic hate speech",
                "religious_hate_speech": "Section of description containing religious hate speech",
                "sexist_speech": "Section of description containing sexist speech",
                "ableist_speech": "Section of description containing ableist speech",
                "hate_description_section": "Section of hate description"
            },
            "caption": {
                "contains_hate_speech": "Is there any hate speech in caption?",
                "racial_hate_speech": "Section of caption containing racial hate speech",
                "homophobic_transphobic_hate_speech": "Section of caption containing homophobic or transphobic hate speech",
                "religious_hate_speech": "Section of caption containing religious hate speech",
                "sexist_speech": "Section of caption containing sexist speech",
                "ableist_speech": "Section of caption containing ableist speech",
                "hate_caption_section": "Section of hate caption"
            },
            "title": {
                "hate_caption_section": "Section of hate caption in the video title"
            }
        },
        "intensity": {
            "hate_speech_percentage_description": 25,
            "hate_speech_percentage_caption": 15,
            "overall_hate_percentage": 20
        }
    }```
    For the summary:
    - If there are no caption, output: "No Captions".
    - If there are no hate comments, provide JSON with empty values.
    """

    response = invoke_openai_chat(data, CAPTION_PROMPT)

    print(response)
    return response


def compute_post_llm(json_data):
    # Define the prompt for processing posts
    POST_PROMPT = """You've been assigned the task of analyzing posts for hate speech and you can only talk JSON format. Your analysis should include the following:
    - Determine if there is hate speech in the post text.
    - Extract sections of the post text containing:
        - Racial hate speech
        - Homophobic or transphobic hate speech
        - Religious hate speech
        - Sexist speech
        - Ableist speech
    - Determine the intensity of hate speech in the post text as a percentage.
    - Provide the URL of the post.
    
    Results should adhere to this structure:
    ```json
    {
        "sections": {
            "text": {
                "contains_hate_speech": "Is there any hate speech in the post text?",
                "racial_hate_speech": "Section of text containing racial hate speech",
                "homophobic_transphobic_hate_speech": "Section of text containing homophobic or transphobic hate speech",
                "religious_hate_speech": "Section of text containing religious hate speech",
                "sexist_speech": "Section of text containing sexist speech",
                "ableist_speech": "Section of text containing ableist speech"
            },
            "url": "URL of the post"
        },
        "intensity": {
            "hate_speech_percentage": 15
        }
    }```
    
    For the summary:
    - If there are no posts, output: "No Posts".
    - If there are no hate posts, provide JSON with empty values.
    """

    # Invoke OpenAI chat API to process the data
    response = invoke_openai_chat(json_data, POST_PROMPT)

    return response
