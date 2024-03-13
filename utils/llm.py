from langchain.agents import create_json_agent
from langchain_community.agent_toolkits import JsonToolkit
from langchain_community.tools.json.tool import JsonSpec
from langchain_openai import ChatOpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
llm_client = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.environ.get("OPENAI_API_KEY"), temperature=0)

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

