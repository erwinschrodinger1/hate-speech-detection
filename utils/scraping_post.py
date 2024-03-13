from apify_client import ApifyClient
import os

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
    }
    # Run the Actor and wait for it to finish
    run = client.actor(
        "apify/instagram-post-scraper").call(run_input=run_input)

    # Store dataset object in a variable to avoid repeated calls
    dataset = client.dataset(run["defaultDatasetId"])

    # Use list comprehension to populate datas list
    datas = [{"start": item['start'], "duration": item["duration"],
              "text": item["text"]} for item in dataset.iterate_items()]

    # Return the result directly
    return {
        "description":next(dataset.iterate_items())["videoDescription"],
        "title":next(dataset.iterate_items())["videoTitle"],
        "caption": datas
    }


def scrape_instagram_post(post_url):
    # Prepare the Actor input
    run_input = {
        "startUrls": [{"url": post_url}],
        "Proxy": {"useApifyProxy": True},
    }

    # Run the Actor and wait for it to finish
    run = client.actor("anish0612/instagram-post-scraper").call(run_input=run_input)

    # Initialize an empty list to store the scraped data
    scraped_data = []

    # Fetch and append Actor results from the run's dataset
    dataset = client.dataset(run["defaultDatasetId"])
    for item in dataset.iterate_items():
        post_info = {}

        # Extract post title
        post_info["title"] = item["edge_media_to_caption"]["edges"][0]["node"]["text"]

        # Extract post description
        post_info["description"] = item["edge_media_to_caption"]["edges"][0]["node"]["text"]

        # Convert timestamp to human-readable date
        import datetime
        created_timestamp = int(item["taken_at_timestamp"])
        created_date = datetime.datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # Extract created date
        post_info["created_date"] = created_date

        # Append extracted post info to the list
        scraped_data.append(post_info)

    return scraped_data


# Example usage
post_url = "https://www.instagram.com/p/C4dDe3OvH8h/?utm_source=ig_web_copy_link"
insta_posts = scrape_instagram_post(post_url)
print(insta_posts)