from utils.sraping import scrape_instagram_comments
from utils.llm import compute_comments_llm
from utils.scraping_post import scrape_youtube_caption
import json
 
# Data to be written
dictionary = scrape_youtube_caption("https://www.youtube.com/watch?v=i7K-_zALYdg")
print(dictionary)

with open("scraped_data/youtube_caption.json",'w') as f:
    f.write(json.dumps(dictionary))