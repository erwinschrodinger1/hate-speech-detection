import os
from langchain_openai import ChatOpenAI
import streamlit as st
from constants import labels_and_options
from dotenv import load_dotenv
from enum import Enum
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
from streamlit_echarts import st_echarts
from fpdf import FPDF
import base64
from utils.utils import create_download_link
SAD_LIMIT = 0.5
NEUTRAL_LIMIT = 0.3

st.set_page_config(layout="centered")

load_dotenv()

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


images = ['welcome.gif', 'happy.gif']

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


def invoke_openai_chat(json_data, prompt):
    response = client_open_ai.chat.completions.create(model="gpt-3.5-turbo-1106", temperature=0,
                                                      messages=[
                                                          {"role": "system",
                                                              "content": "You are a helpful assistant."},
                                                          {"role": "user", "content": json.dumps(
                                                              json_data)},
                                                          {"role": "assistant",
                                                              "content": prompt},
                                                      ])
    return response.choices[0].message.content


def handle_comments(link_of, link):
    handle_image_change(0)

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
        elif (link_of == "Twitter"):
            data = scrape_twitter_comments(link)
        st.write("Data Scraped.")
        st.write("Analaysing data...")
        response_string = invoke_openai_chat(data, COMMENT_PROMPT)

    handle_image_change(1)
    st.write(data)

    # response_string = """```json
    #         {
    #     "totalComments": 7,
    #     "racialHateSpeech": 1,
    #     "homophobicTransphobicSpeech": 0,
    #     "religiousHateSpeech": 1,
    #     "sexistSpeech": 0,
    #     "ableistSpeech": 0,
    #     "numberOfHateComments": 2,
    #     "hateComments": [
    #         {
    #         "text": "nigga",
    #         "timeStamp": "2024-03-12T13:08:05.000Z",
    #         "username": "nirjal_bhurtel",
    #         "profileName": "nirjal_bhurtel",
    #         "reason": "Racial hate speech",
    #         "hateOn": [
    #             "Racial"
    #         ],
    #         "hatePercentage": 100
    #         },
    #         {
    #         "text": "Religions are bad",
    #         "timeStamp": "2024-03-12T13:09:57.000Z",
    #         "username": "nirjal_bhurtel",
    #         "profileName": "nirjal_bhurtel",
    #         "reason": "Religious hate speech",
    #         "hateOn": [
    #             "Religious"
    #         ],
    #         "hatePercentage": 100
    #         }
    #     ]
    #     }```"""

    print("First json ")

    print(response_string)
    response_string = response_string.strip("```json").strip("`")
    print("Json after")
    print(response_string)
    print(type(response_string))

    response = json.loads(response_string)
    # st.write(response)
    if (response != {}):
        # if response['numberOfHateComments']/response['totalComments'] > SAD_LIMIT:
        #     avatar_status = AvatarStatus.SAD
        # elif response['numberOfHateComments']/response['totalComments'] > NEUTRAL_LIMIT:
        #     avatar_status = AvatarStatus.NEUTRAL
        # else:
        #     avatar_status = AvatarStatus.HAPPY

        # Prepare data for pie chart
        dougnut_data = []
        for key, value in response.items():
            if key.endswith("Speech"):
                label = key.replace("Speech", "")
                dougnut_data.append({"value": value, "name": label})

        options = {
            "backgroundColor": "#000000",
            "tooltip": {"trigger": "item"},
            "legend": {"top": "5%", "left": "center", "textStyle": {
                "color": "#fff"
            }, },
            "series": [
                {
                    # "color":"#000",
                    "name": "Dougnut",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#000",
                        "borderWidth": 2,
                    },
                    "label": {"show": False, "position": "center", "textStyle": {
                        "color": "#fff"
                    }},
                    "emphasis": {
                        "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                    },
                    "labelLine": {"show": False},
                    "data": dougnut_data,
                }
            ],
        }

        col1, col2 = st.columns((1, 1))
        with col1:
            # Display the pie chart
            st_echarts(options=options, height="500px")
        with col2:
            with st.container(border=True):
                st.markdown(f"""
                    **Total Comments** : {response["totalComments"]} \n
                    **Total Hate Comments** : {response["numberOfHateComments"]} \n
                    **Breakdown of Hate Speech:**
                    - Racial Hate Speech: {response["racialHateSpeech"]}
                    - Homophobic/Transphobic Speech: {response["homophobicTransphobicSpeech"]}
                    - Religious Hate Speech: {response["religiousHateSpeech"]}
                    - Sexist Speech: {response["sexistSpeech"]}
                    - Ableist Speech: {response["ableistSpeech"]}
                """)

        st.subheader("Hate Comments")
        for comment in response['hateComments']:
            with st.container(border=True):
                st.markdown(f"""
                    <div style="display:flex; justify-content: space-between; width:100%;">
                        <p>{comment['username']}</p>
                        <p>{comment['profileName']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content: space-between; width:100%;">
                    <strong> {comment['text']} </strong>
                    <p>{comment['timeStamp']}""", unsafe_allow_html=True)
                st.write(f"Reason: {comment['reason']}")
                st.write(f"Hate On: {', '.join(comment['hateOn'])}")
                st.write(f"Hate Percentage: {comment['hatePercentage']}")


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
        "start_urls": [{"url": link}],
        "max_comments": 100,
        "proxySettings": {"useApifyProxy": False},
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


def scrape_twitter_comments(link):
   # Prepare the Actor input
    run_input = {
        "maxTweets": 5,
        "urls": [link],
    }

    # Run the Actor and wait for it to finish
    run = client.actor(
        "microworlds/twitter-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [{"fulltext": item['full_text'], }
             for item in dataset.iterate_items()]

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


def handle_image_change(index):
    img_url = f"./assets/{images[index]}"
    image_section.image(img_url)

# st.title("Hate Speech Detection")
# st.write("Application that detects Hate Speech using OpenAI apis and apify")
# st.markdown(body="""
#             ##### It rated the posts on following basis:
#             - Racial Hate Speech
#             - Homophobic and Transphobic Speech
#             - Religious Hate Speech
#             - Sexist Speech
#             - Ableist Speech
#             """)


col1, col2 = st.columns((3, 1))
with col1:
    col1i, coli2 = st.columns((4, 1))
    with col1i:
        link = st.text_input(
            "Input link", placeholder="Allowed Links: Youtube, Twitter, Instagram, LinkedIn")

        submit_btn_dis = True
        selection_option = ""
        is_link, link_of = (False, 'None')
        if link:
            is_link, link_of = identify_social_media(link)
            # is_link, link_of = True, "YouTube"
            print(link_of)
            if (is_link):
                submit_btn_dis = False
                for item in labels_and_options:
                    if item["platform"].lower() == link_of.lower():
                        selection_option = st.selectbox(
                            label="Hate Speech Detection on", options=item["labels"])
                        break
        st.markdown(
            """
            <style>
            .stButton > button {
                transform: translateY(75%);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    with coli2:
        submit_btn = st.button("Submit", disabled=submit_btn_dis)

with col2:
    image_section = st.empty()
    handle_image_change(1)
    # if (avatar_status == AvatarStatus.WELCOME):
    #     st.image("./assets/welcome.gif")
    # if avatar_status == AvatarStatus.LOADING:
    #     st.image("./assets/heppy.gif")

st.divider()
if True:
    # (submit_btn):
    if selection_option == "Comments" or selection_option == "Tweet":
        handle_comments(link_of, link)

# export_as_pdf = st.button("Export Detailed Report")
# def create_download_link(val, filename):
#     b64 = base64.b64encode(val)  # val looks like b'...'
#     return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'
# if export_as_pdf:
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font('Arial', 'B', 16)
#     # pdf.cell(40, 10, report_text)

#     html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")

#     st.markdown(html, unsafe_allow_html=True)


export_as_pdf = st.button("Export Detailed Report")

if export_as_pdf:
    # Create a PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Add content to the PDF (you can add content similar to what you display on the Streamlit app)
    pdf.cell(200, 10, txt="Detailed Report", ln=True, align="C")
    pdf.cell(200, 10, txt="", ln=True, align="C")  # Add empty line
    
    # Add more content here as needed
    
    # Get the binary content of the PDF
    pdf_content = pdf.output(dest="S").encode("latin-1")
    
    # Create a download link for the PDF
    download_link = create_download_link(pdf_content, "detailed_report")
    
    # Display the download link
    st.markdown(download_link, unsafe_allow_html=True)
