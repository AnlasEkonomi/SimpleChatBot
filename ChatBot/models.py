import json
import random
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab') 


with open('intents.json','r',encoding='utf-8') as file:
    intents=json.load(file)

stop_words=set(stopwords.words('turkish'))

def preprocess_text(text):
    text=text.translate(str.maketrans('', '', string.punctuation))
    text=text.lower()
    tokens=word_tokenize(text)
    tokens=[token for token in tokens if token not in stop_words]
    return ' '.join(tokens)


patterns=[]
responses=[]
tags=[]

for intent in intents['intents']:
    for pattern in intent['patterns']:
        patterns.append(preprocess_text(pattern))
        responses.append(intent['responses'])
        tags.append(intent['tag'])


vectorizer=TfidfVectorizer()
X=vectorizer.fit_transform(patterns)

def get_response(user_input):
    processed_input=preprocess_text(user_input)
    input_vector=vectorizer.transform([processed_input])
    similarities=cosine_similarity(input_vector, X)
    
    max_sim_idx=np.argmax(similarities[0])
    
    if similarities[0][max_sim_idx]>0.3:
        return random.choice(responses[max_sim_idx])
    else:
        return "Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir sorununuza yardımcı olabilir miyim?"
