from apify_client import ApifyClient
import os
import json

api_key = os.environ.get("APIFY_API_TOKEN")
print(api_key)

client = ApifyClient(api_key)


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
    datas = [{"user_name": item["ownerUsername"],
              "full_text": item["text"],
              "created_at": item["timestamp"]}for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "comments": datas
    }


def scrape_facebook_comments(link):
    run_input = {
        "includeNestedComments": True,
        "startUrls": [{"url": link}],
        "resultsLimit": 20,
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "apify/facebook-comments-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [{"user_name": item["profileName"],
              "full_text": item["text"],
              "created_at": item["date"]}
             for item in dataset.iterate_items()]

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
    datas = [{
        "user_name": item["user"]["name"],
        "full_text": item["full_text"],
        "created_at": item["created_at"]}
        for item in dataset.iterate_items()]

    return {
        "comments": datas
    }


link = "https://www.youtube.com/watch?v=9x9J6tpNT4Y"
youtube_comments = scrape_youtube_comments(link)
comments = []
# Iterate over each comment in the provided JSON data
for comment_data in youtube_comments["comments"]:
    # Extract relevant information from the comment_data
    username = comment_data["comment_author_name"]
    full_text = comment_data["comment_text"]
    created_at = comment_data["comment_date"]
    
    # Create a new JSON object for the comment
    comment_json = {
        "userName": username,
        "full_text": full_text,
        "created_at": created_at
    }
    
    # Append the comment JSON object to the comments list
    comments.append(comment_json)

# Create a JSON object with the comments list
output_json = {"comments": comments}

file_path = "youtube_comments.json"

# Write the JSON data to the file
with open(file_path, "w") as file:
    json.dump(output_json, file, indent=2)
