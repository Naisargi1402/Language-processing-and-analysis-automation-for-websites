
"""
Author: Naisargi Vadodariya
Title: Text Analysis & Web Scraping
"""
#importing the libraries and packages
import requests
import pandas as pd 
from bs4 import BeautifulSoup
import string
import spacy
import re
import urllib.request
from IPython.display import HTML
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
!pip install textstat
import textstat
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt')


#Web scraping
#Reading url from the excel sheet
dataset =pd.read_excel('Input.xlsx')
in2=37
for article in dataset[21:]['URL']:
  r = urllib.request.urlopen(article).read()
  soup = BeautifulSoup(r,"lxml")
  
  #Extracting the title and Content
  for text1 in soup.find_all('pre',class_='wp-block-preformatted'):
    #fname = f"{article[10]}.txt"
    file=open('raw.txt',"w")
    # if the URL is not having any content, abort the process
    for title in soup.find_all('h3'):
      if title.get_text() == 'Ooops... Error 404':
        exit
    for title in soup.find_all('h1'):
      file.write(title.get_text())
    for text in soup.find_all('div',class_='td-post-content tagdiv-type'):
      file.write(text.get_text())
  #Get the author of blog and store the string
    for text1 in soup.find_all('pre',class_='wp-block-preformatted'):
      text2=text1.get_text()
  
    try:
      with open('raw.txt', 'r') as fr:
          lines = fr.readlines()
          fname = f"{in2}.txt"
          in2+=1 
          with open(fname, 'w') as fw:
              for line in lines:
                  # if the content has author info, skip it and write all other info in the file.
                  if line.strip('\n') != text2 :
                      fw.write(line.replace('\n', ' '))
    #Exception catching
    except:
        print("Oops! something error")

#sentiment analysis Function
def sentiment_analysis(data):
    sentiment = TextBlob(data["content"]).sentiment
    return pd.Series([sentiment.polarity,sentiment.subjectivity ])

#Extract proper noun
def ProperNounExtractor(text):
    count = 0
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        for (word, tag) in tagged:
            if tag == 'PRP': # If the word is a proper noun
                count = count + 1 
        
    return(count)         
                
# Analysis function for all the URLs
def analysis(url,id):
  headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"}
  page = requests.get(url, headers=headers)
  df1= pd.DataFrame()
  soup = BeautifulSoup(page.content, 'html.parser')
  title=soup.find('h1',class_="entry-title")
  content=soup.findAll(attrs={'class':'td-post-content'})
  
  #if content is not present in the URL, return an empty dataframe
  if not (content):
    return df1
  content=content[0].text.replace('\n'," ")
  
  #Remove Punctuation
  content = content.translate(str.maketrans('', '', string.punctuation))
  
  #Tokenization
  text_tokens = word_tokenize(content)
  len(text_tokens)

  #Remove the stopwords
  my_stop_words = stopwords.words('english')
  my_stop_words.append('the')
  no_stop_tokens = [word for word in text_tokens if not word in my_stop_words]
  len(no_stop_tokens)

  #calculate total positive words
  with open("positive-words.txt","r") as pos:
    poswords = pos.read().split("\n")  
    poswords = poswords[5:]
  pos_count = " ".join ([w for w in no_stop_tokens if w in poswords])
  pos_count=pos_count.split(" ")

  Positive_score=len(pos_count)
  Positive_score=len(pos_count)
  
  #calculate total negaive words
  with open("negative-words.txt","r",encoding = "ISO-8859-1") as neg:
    negwords = neg.read().split("\n")
    
  negwords = negwords[36:]

  neg_count = " ".join ([w for w in no_stop_tokens if w in negwords])
  neg_count=neg_count.split(" ")
  Negative_score=len(neg_count)
  filter_content = ' '.join(no_stop_tokens)
  
  #creating a temporary dataframe
  data=[[id,url,title,content,filter_content,Positive_score,Negative_score]]
  data=pd.DataFrame(data,columns=["url_id","url","title","content","filter_content","Positive_Score","Negative_Score"])
  
  #Sentiment Analysis
  data[["polarity", "subjectivity"]] = data.apply(sentiment_analysis, axis=1)
  
  #AAverage Sentence Length
  AVG_SENTENCE_LENGTH = len(content.replace(' ',''))/len(re.split(r'[?!.]', content))
  data[["avg_sen_len"]] = AVG_SENTENCE_LENGTH
  
  #FOG index
  FOG_INDEX=(textstat.gunning_fog(content))
  data[["fog_index"]] = FOG_INDEX

  #Finding all the other attributes
  AVG_NUMBER_OF_WORDS_PER_SENTENCE = [len(l.split()) for l in re.split(r'[?!.]', content) if l.strip()]
  data[["avg-words_per_sen"]] = (sum(AVG_NUMBER_OF_WORDS_PER_SENTENCE)/len(AVG_NUMBER_OF_WORDS_PER_SENTENCE))

  def syllable_count(word):
    count = 0
    vowels = "AEIOUYaeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)): 
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
            if word.endswith("es"or "ed"):
                count -= 1
    if count == 0:
        count += 1
    return count

  COMPLEX_WORDS=syllable_count(content)
  data[["complex_words"]] = COMPLEX_WORDS

  Word_Count=len(content)
  data[["Word_count"]]=Word_Count

  pcw=(COMPLEX_WORDS/Word_Count)*100
  data[["Percent_of_CW"]]=pcw

  Personal_Pronouns=ProperNounExtractor(content)  
  data[["Personal Pronouns"]]=Personal_Pronouns

  Average_Word_Length=len(content.replace(' ',''))/len(content.split())
  data[["Avg_word_len"]]=Average_Word_Length

  word=content.replace(' ','')
  syllable_count=0
  for w in word:
        if(w=='a' or w=='e' or w=='i' or w=='o' or w=='y' or w=='u' or w=='A' or w=='E' or w=='I' or w=='O' or w=='U' or w=='Y'):
              syllable_count=syllable_count+1
  sc = syllable_count/len(content.split())
  data[["Syllable count"]]=sc

  data_final = data_final.append(data, ignore_index=True)
  return (data)

#Creating a new DataFrame
datafinal = pd.DataFrame()
i=36
for article in data[:]['URL']:
    i+=1
    datafinal = datafinal.append(analysis(article,i))

#Write the content in the excel file
writer = pd.ExcelWriter('Output.xlsx')
#Removing the index
datafinal.to_excel(writer,index=False)
#Save the excel
writer.save()
print('DataFrame is written successfully to Excel File.')

