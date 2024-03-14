import streamlit as st
from constants import labels_and_options
import os
import streamlit as st
from utils.utils import identify_social_media, convert_llm_res_dict
from utils.sraping import scrape_youtube_comments, scrape_twitter_comments, scrape_instagram_comments, scrape_facebook_comments
from utils.scraping_post import scrape_youtube_caption, scrape_facebook_group_posts, scrape_user_instagram_posts
from utils.llm import compute_comments_llm, compute_caption_llm, compute_post_llm
from streamlit_echarts import st_echarts
import json

SAD_LIMIT = 0.5
NEUTRAL_LIMIT = 0.3

st.set_page_config(layout="centered")

images = ['happy.gif', 'neutral.gif', 'loading.gif', 'sad.webp']
HAPPY = 0
NEUTRAL = 1
LOADING = 2
SAD = 3


def handle_image_change(index):
    image_section.image(f"assets/{images[index]}")


# Input and button section
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
    text_section = st.empty()
    handle_image_change(HAPPY)

st.divider()
if (submit_btn):
    handle_image_change(LOADING)
    if selection_option == "Comments" or selection_option == "Tweet":
        if link_of == "YouTube":
            scraped_data = scrape_youtube_comments(link)
        elif link_of == "Twitter":
            scraped_data = scrape_twitter_comments(link)
        elif link_of == "Instagram":
            scraped_data = scrape_instagram_comments(link)
        elif link_of == "Facebook":
            scraped_data = scrape_facebook_comments(link)

        with open("test.json", 'w') as f:
            f.write(json.dumps(scraped_data))

        response = convert_llm_res_dict(compute_comments_llm(scraped_data))
        print(type(response))
        if (response != {}):
            if response['numberOfHateComments']/response['totalComments'] > SAD_LIMIT:
                handle_image_change(SAD)
            elif response['numberOfHateComments'] > 1:
                handle_image_change(NEUTRAL)
            else:
                handle_image_change(HAPPY)

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
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content: space-between; width:100%;">
                    <strong> {comment['text']} </strong>
                    <p>{comment['timeStamp']}""", unsafe_allow_html=True)
                st.write(f"Reason: {comment['reason']}")
                st.write(f"Hate On: {', '.join(comment['hateOn'])}")
                st.write(f"Hate Percentage: {comment['hatePercentage']}")
        text_section.write(response["summary"])
    elif selection_option == "Post":
        if link_of == "Instagram":
            scraped_data = scrape_user_instagram_posts(link)
        elif link_of == "Facebook":
            scraped_data = scrape_facebook_group_posts(link)

        with open("test.json", 'w') as f:
            f.write(json.dumps(scraped_data))

        response = convert_llm_res_dict(compute_post_llm(scraped_data))
        with open("llmpost.json", "w") as f:
            f.write(json.dumps(response))

        if (response != {}):
            if response['numberOfHatePosts']/response['totalPosts'] > SAD_LIMIT:
                handle_image_change(SAD)
            elif response['numberOfHatePosts'] > 1:
                handle_image_change(NEUTRAL)
            else:
                handle_image_change(HAPPY)

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
                    **Total Posts** : {response["totalPosts"]} \n
                    **Total Hate Posts** : {response["numberOfHatePosts"]} \n
                    **Breakdown of Hate Speech:**
                    - Racial Hate Speech: {response["racialHateSpeech"]}
                    - Homophobic/Transphobic Speech: {response["homophobicTransphobicSpeech"]}
                    - Religious Hate Speech: {response["religiousHateSpeech"]}
                    - Sexist Speech: {response["sexistSpeech"]}
                    - Ableist Speech: {response["ableistSpeech"]}
                """)

        st.subheader("Hate Posts")
        for comment in response['hatePosts']:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content: space-between; width:100%;">
                    <strong> {comment['text']} </strong>
                    """, unsafe_allow_html=True)
                st.markdown(f""" **URL:**
                            {comment['url']}""")
                st.write(f"Reason: {comment['reason']}")
                st.write(f"Hate On: {', '.join(comment['hateOn'])}")
                st.write(f"Hate Percentage: {comment['hatePercentage']}")
        text_section.write(response["summary"])
    elif selection_option == "Video":
        if link_of == "YouTube":
            scraped_data = scrape_youtube_caption(link)

        response = convert_llm_res_dict(compute_caption_llm(scraped_data))
        with open("llmcaption.json", "w") as f:
            f.write(json.dumps(response))
        print(response)
        if response != {}:
            if response['numberOfHateComments'] > 1:
                handle_image_change(SAD)

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
                        **Total Hate Content** : {response["numberOfHateComments"]} \n
                        **Breakdown of Hate Speech:**
                        - Racial Hate Speech: {response["racialHateSpeech"]}
                        - Homophobic/Transphobic Speech: {response["homophobicTransphobicSpeech"]}
                        - Religious Hate Speech: {response["religiousHateSpeech"]}
                        - Sexist Speech: {response["sexistSpeech"]}
                        - Ableist Speech: {response["ableistSpeech"]}
                    """)

            st.subheader("Hate Content")
            for comment in response['hateContent']:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content: space-between; width:100%;">
                        <strong> {comment['text']} </strong>
                        """, unsafe_allow_html=True)
                    st.markdown(f"""isIn:
                                {comment['isIn']}""")
                    st.write(f"Reason: {comment['reason']}")
                    st.write(f"Hate On: {', '.join(comment['hateOn'])}")
                    st.write(f"Hate Percentage: {comment['hatePercentage']}")
            text_section.write(response["summary"])
