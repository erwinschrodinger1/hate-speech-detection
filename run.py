from utils.sraping import scrape_instagram_comments
import json
 
# Data to be written
dictionary = scrape_instagram_comments("https://www.instagram.com/p/CztUZmMrJOf/?img_index=1")
 
with open("scraped_data/instagram_comments.json", "w") as outfile:
    json.dump(dictionary, outfile)