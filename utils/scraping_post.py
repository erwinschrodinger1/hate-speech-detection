from apify_client import ApifyClient
import os
import json

api_key = os.environ.get("APIFY_API_TOKEN")
print(api_key)

client = ApifyClient(api_key)


def scrape_youtube_caption(link):
    # Prepare the Actor input
    run_input = {
        "startUrls": [
            {"url": link},
        ],
        "language": "en",
        "useAsr":True
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "genial_candlestand/youtube-subtitles-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])


    # testData = [item for item in dataset.iterate_items()]
    
    # with open("test.json",'w') as f:
    #     f.write(json.dumps(testData))
    
    # Use list comprehension to populate datas list
    datas = [{"start": item['start'], "duration": item["duration"],
              "text": item["text"]} for item in dataset.iterate_items()]

    
    print(datas)
    # Return the result directly
    return {
        "description":next(dataset.iterate_items())["videoDescription"],
        "title":next(dataset.iterate_items())["videoTitle"],
        "caption": datas
    }


# def scrape_single_instagram_post(post_url):
#     # Prepare the Actor input
#     run_input = {
#         "startUrls": [{"url": post_url}],
#         "Proxy": {"useApifyProxy": True},
#     }

#     # Run the Actor and wait for it to finish
#     run = client.actor("anish0612/instagram-post-scraper").call(run_input=run_input)

#     # Initialize an empty list to store the scraped data
#     scraped_data = []

#     # Fetch and append Actor results from the run's dataset
#     dataset = client.dataset(run["defaultDatasetId"])
#     for item in dataset.iterate_items():
#         post_info = {}
        
#         # Extract post description
#         post_info["text"] = item["edge_media_to_caption"]["edges"][0]["node"]["text"]
#         post_info["url"] = post_url
        
#         scraped_data.append(post_info)

#     return scraped_data

# # # Example usage
# # post_url = "https://www.instagram.com/p/C4dDe3OvH8h/?utm_source=ig_web_copy_link"
# # insta_posts = scrape_single_instagram_post(post_url)
# # print(insta_posts)


def scrape_user_instagram_posts(username, results_limit=30):

    run_input = {
        "username": [username],
        "resultsLimit": results_limit,
    }

    # Run the Actor and wait for it to finish
    run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)

    # Initialize an empty list to store the scraped data
    scraped_data = []

    # Fetch and append Actor results from the run's dataset
    dataset = client.dataset(run["defaultDatasetId"])
    for item in dataset.iterate_items():
        # Extract post text and post URL
        post_text = item.get('caption', '')
        post_url = item.get('url', '')
        scraped_data.append({'text': post_text, 'url': post_url})

    return scraped_data

# # Example usage
# username = "https://www.instagram.com/coexistingelement/"
# results = scrape_user_instagram_posts(username)
# for item in results:
#     print(item)
    

def scrape_facebook_group_posts(group_url, results_limit=20):
   
    run_input = {
        "startUrls": [{"url": group_url}],
        "resultsLimit": results_limit,
    }
    
    # Run the Actor and wait for it to finish
    run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
    
    # Initialize an empty list to store the scraped data
    scraped_data = []
    
    # Fetch and append Actor results from the run's dataset
    dataset = client.dataset(run["defaultDatasetId"])
    for item in dataset.iterate_items():
        post_text = item.get("text", "")
        post_url = item.get("url", "")
        scraped_data.append({"text": post_text, "url": post_url})
    
    return scraped_data


# # Example usage
# group_url = "https://www.facebook.com/kiranjan.zarry"
# posts = scrape_facebook_group_posts(group_url, results_limit=20)

