from utils.sraping import scrape_instagram_comments
from utils.llm import compute_comments_llm
import json
 
# Data to be written
dictionary = scrape_instagram_comments("https://www.instagram.com/p/C37aUtkP4DV/")
 
print(
    compute_comments_llm(dictionary)
)