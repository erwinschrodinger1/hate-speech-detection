from selenium import webdriver
from selenium.webdriver.common.by import By
import time
url = input("Enter Youtube Video URL : ")
driver=webdriver.Chrome()
driver.get(url)

def scroll_to_bottom(driver):
    old_position = 0                #AUTOMATIC SCROLLING TILL PAGE ENDS
    new_position = None
    time.sleep(5)  #Sleep For Comment Section to Load
    
    scroll_limit = 10
    limit = 0
    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                  " window.pageYOffset : (document.documentElement ||"
                  " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(2)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                  " window.pageYOffset : (document.documentElement ||"
                  " document.body.parentNode || document.body);"))
        limit += 1
        
        if limit==scroll_limit:
            break
        
time.sleep(5)

try:
    scroll_to_bottom(driver)
    
    comments=driver.find_elements(By.XPATH, '//*[@id="content-text"]')
except:
    pass

i=1   

comments_list = []

for comment in comments:
    print(comment)
    comment_store = str(comment.text)
    comments_list.append(comment_store)
    file = open("Raw_Comments.txt","a", encoding="utf-8")
    file.write(f"{i}. {comment_store}\n")
    i = i+1
    file.close()
print("Completed !!! Data Stored To Raw_Comments.txt")    
driver.close()


from keras.preprocessing.sequence import pad_sequences
from tensorflow.python.keras.models import load_model
import pickle

# Load the model and tokenizer
loaded_model = load_model('fixedmodel.h5', custom_objects=None, compile=True)
with open('tokenizer.pickle', 'rb') as handle:
    loaded_tokenizer = pickle.load(handle)

# Initialize an empty list to store predictions
predictions = []

# Iterate through each sentence in the list
for txt in comments_list:
    # Convert the sentence to a sequence using the loaded tokenizer
    seq = loaded_tokenizer.texts_to_sequences([txt])
    # Pad the sequence to match the input shape of the model
    padded = pad_sequences(seq, maxlen=len(txt))
    # Predict the class label
    pred = loaded_model.predict_classes(padded)
    # Determine the prediction label based on the predicted class
    pred = (max(max(max(pred))))
    if pred == 1:
        processed_text = "High"
    else:
        processed_text = "Low"
    # Append the processed text to the predictions list
    predictions.append(processed_text)