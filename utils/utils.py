import base64
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
from fpdf import FPDF



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




def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'
