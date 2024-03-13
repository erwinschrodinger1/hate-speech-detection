from openai import OpenAI
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.agent_toolkits import JsonToolkit
from langchain.agents import create_json_agent
import os
import re
import streamlit as st
import time
from apify_client import ApifyClient
import matplotlib.pyplot as plt
import json


api_key = os.environ.get("APIFY_API_TOKEN")
print(api_key)
# Initialize the ApifyClient with your Apify API token
client = ApifyClient(api_key)
open_ai_api_key = os.environ.get('OPENAI_API_KEY')

client_open_ai = OpenAI(api_key=open_ai_api_key)


def identify_social_media(url):
    pattern = r'\b(?:https?://)?(?:www\.)?(?:(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)|(?:instagram\.com/(?:p/|tv/|reel/))([\w.-]+)/?|twitter\.com/[a-zA-Z0-9_]+/status/\d+|(?:facebook\.com|fb\.me)/[\w-]+(?:/posts/\d+)?|linkedin\.com/posts/[a-zA-Z0-9-]+)\b'
    match = re.search(pattern, url)
    if match:
        platforms = {
            'youtube.com': 'YouTube',
            'youtu.be': 'YouTube',
            'twitter.com': 'Twitter',
            'instagram.com': 'Instagram',
            'facebook.com': 'Facebook',
            'fb.me': 'Facebook',
            'linkedin.com': 'LinkedIn'
        }
        for platform in platforms.keys():
            if platform in match.group(0):
                return True, platforms[platform]
    return False, None


# COMMENT_PROMPT = """
#                 You are a company hate speech detector that only speaks in JSON. Do not generate output that isn't in properly formatted JSON.
                
#                 Your task is to analyse the data and return me results based on the hate speech of following types:
#                     - Racial Hate Speech
#                     - Homophobic and Transphobic Speech
#                     - Religious Hate Speech
#                     - Sexist Speech
#                     - Ableist Speech
#                 Compute
#                     1. Total number of comments.
#                     2. Number of comments containing racial hate speech.
#                     3. Number of comments containing homophobic or transphobic hate speech.
#                     4. Number of comments containing religious hate speech.
#                     5. Number of comments containing sexist speech.
#                     6. Number of comments containing ableist speech.
#                     7. Total number of hate comments.
#                     8. If hate comments are found, provide details of each hate comment including the text, username, profile name, reason for classification as hate speech, types of hate speech identified, and a measure of the intensity of hate speech.
#                 Results should be in the format:

#             {
#                     "totalComments": "LENGTH of comments in jsons",
#                     "racialHateSpeech": "length of comments that contain racial hate speech",
#                     "homophobicTransphobicSpeech": "length of comments that contain homophobic or transphobic hate speech",
#                     "religiousHateSpeech": "length of comments that contain religious hate speech",
#                     "sexistSpeech": "length of comments that contain sexist speech",
#                     "ableistSpeech": "length of comments that contain ableist speech",
#                     "numberOfHateComments": "SUM of hate comments",
#                     "hateComments": [
#                         {
#                             "text": "actual comment",
#                             "username": "username of user commenting",
#                             "profileName": "profile name of user commenting",
#                             "reason": "reason why the following comment was a hate comment",
#                             "hateOn": ["list of types of hate speech that was triggered"],
#                             "hatePercentage": "percentage in which the hate is from 1 to 100 how harsh is it"
#                         }
#                     ]
#                 }

#                 If no comments are there, simply write in the Summary section: "No Comments". Do not make stuff up.
#                 If there are no hate comments made just give the json with empty values        
#                 """

COMMENT_PROMPT = """
You've been assigned the task of analyzing comments for hate speech and you can only talk JSON format. Your analysis should encompass the following:

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
            "username": "Username of the commenter",
            "profileName": "Profile name of the commenter",
            "reason": "Reason for classifying the comment as hate speech",
            "hateOn": ["Types of hate speech identified"],
            "hatePercentage": "Intensity of hate speech (percentage)"
        }
    ]
}
```

For the summary:
- If there are no comments, output: "No Comments".
- If there are no hate comments, provide JSON with empty values.
"""


def invoke_openai_chat(json_data, prompt):
    response = client_open_ai.chat.completions.create(model="gpt-3.5-turbo-1106",temperature=0,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": json.dumps(json_data)},
        {"role": "assistant", "content": prompt},
    ])
    return response.choices[0].message.content

def handle_comments(link_of, link):
    with st.status("Analysing data..."):
        st.write("Scraping data...")
        if (link_of == "Instagram"):
            data = scrape_instagram_comments(link)
        elif (link_of == "Facebook"):
            data = scrape_facebook_comments(link)
        elif (link_of == "LinkedIn"):
            data = scrape_linkedin_comments(link)
        elif (link_of == "YouTube"):
            data = scrape_youtube_comments(link)
        st.write("Data Scraped.")
        st.write("Analaysing data...")
        response = invoke_openai_chat(data,COMMENT_PROMPT)
        print(response)
        st.write(response)

        # json_spec = JsonSpec(dict_=data, max_value_length=4000)
        # json_toolkit = JsonToolkit(spec=json_spec)
        # json_agent_executor = create_json_agent(
        #     llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        #     toolkit=json_toolkit, max_iteration=1000, verbose=False, handle_parsing_errors=True)
        # try:
        #     response = json_agent_executor.run(
        #                                        )
        # except ValueError as e:
        #     st.write("Parsing Error! Please try again")
        #     st.error(e)
        #     st.write("Data Analaysed.")
        #     response = {}
    # response = { "totalComments": 5, "numberOfHateComments": 2, "racialHateSpeech": 1, "homophobicTransphobicSpeech": 0, "religiousHateSpeech": 1, "sexistSpeech": 0, "ableistSpeech": 0, "hateComments": [ { "text": "nigga", "username": "nirjal_bhurtel", "profileName": "nirjal_bhurtel", "reason": "racial hate speech", "hateOn": ["racialHateSpeech"], "hatePercentage": "100" }, { "text": "Religions are bad", "username": "nirjal_bhurtel", "profileName": "nirjal_bhurtel", "reason": "religious hate speech", "hateOn": ["religiousHateSpeech"], "hatePercentage": "100" } ] }
    st.write(data)
    st.write(response)
    # if(response != {}):
    #   # Extract hate speech counts for each type
    #     hate_types = ["racialHateSpeech", "homophobicTransphobicSpeech", "religiousHateSpeech", "sexistSpeech", "ableistSpeech"]
    #     hate_counts = {hate_type: response.get(hate_type, 0) for hate_type in hate_types}

    #     # Create doughnut chart
    #     labels = list(hate_counts.keys())
    #     sizes = list(hate_counts.values())
    #     my_circle = plt.Circle( (0,0), 0.7, color='white')

    #     # Custom wedges
    #     plt.pie(sizes, labels=labels, wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'black' })
    #     p = plt.gcf()
    #     p.gca().add_artist(my_circle)
    #     plt.show()
    #     fig, ax = plt.subplots()
    #     ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
    #     ax.axis('equal')  # Equal aspect ratio ensures that pie is
    #     fig.patch.set_alpha(0.0)
    #     st.pyplot(fig)


def scrape_instagram_comments(link):
    # Prepare the Actor input
    run_input = {
        "directUrls": [
            link
        ],
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "apify/instagram-comment-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [item for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "comments": datas
    }


def scrape_facebook_comments(link):
    run_input = {
        "startUrls": [{"url": link}],
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "apify/facebook-comments-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [item for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "comments": datas
    }


def scrape_youtube_comments(link):
    run_input = {
        "start_urls": [{ "url": link }],
        "max_comments": 100,
        "proxySettings": { "useApifyProxy": False },
    }
    
    run = client.actor(
        "deeper/youtube-comment-scrapper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [item for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "comments": datas
    }


def scrape_linkedin_comments(link):
   # Prepare the Actor input
    run_input = {
        "postUrl": link,
        "sortType": "RELEVANCE",
        "startPage": 1,
        "minDelay": 2,
        "maxDelay": 7,
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "curious_coder/linkedin-comment-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [item for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "comments": datas
    }


def handle_youtube_video(link):
    with st.status("Downloading data..."):
        st.write("Searching for data...")
        time.sleep(2)
        st.write("Found URL.")
        time.sleep(1)
        st.write("Downloading data...")
        time.sleep(1)


def handle_youtube_comment(link):
    st.write("Handling YouTube Comment...")


def handle_facebook_post(link):
    st.write("Handling Facebook Post...")


def handle_facebook_comment(link):
    st.write("Handling Facebook Comment...")


def handle_instagram_post(link):
    st.write("Handling Instagram Post...")


def handle_instagram_comment(link):
    st.write("Handling Instagram Post...")


def handle_twitter_tweet(link):
    st.write("Handling Twitter Tweet...")


def handle_linkedin_post(link):
    st.write("Handling LinkedIn Post...")


def handle_linkedin_comment(link):
    st.write("Handling LinkedIn Post...")
