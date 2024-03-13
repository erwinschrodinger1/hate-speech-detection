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
        "genial_candlestand/youtube-subtitles-scraper").call(run_input=run_input)

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
