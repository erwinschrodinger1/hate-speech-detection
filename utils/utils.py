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

def convert_llm_res_dict(string_response):
    return json.loads( string_response.strip("```json").strip("`"))