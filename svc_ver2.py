import pandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import *
from sklearn.linear_model import LogisticRegression
from tqdm.notebook import tqdm
import spacy
from nltk.stem.snowball import SnowballStemmer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from tqdm import tqdm

train = pd.read_csv('c:/Users/user/Desktop/mbtidata/mbti.csv', encoding='utf-8')
test = train.drop(['type'], axis=1)
test.head()

# 설명변수
X = train['posts']
# 예측변수
Y = train['type']

print(f"{len(train['type'].unique())}개")
train['type'].value_counts()
train.isnull().sum()
train['posts'].nunique() == len(train['posts'])
print("train data : ", train.shape)
print("test data : ", test.shape)

# # NLTK 불용어 처리를 위해 불용어 리스트 다운로드
# nltk.download('stopwords')
# nltk.download('punkt')

# NLTK에서 사용할 SnowballStemmer 로드
s_stemmer = SnowballStemmer(language='english')

def removeStopwords(s):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(s)
    new_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(new_words)

# 어간 추출 함수
def replaceStemwords(s):
    words = word_tokenize(s)
    new_words = [s_stemmer.stem(word) for word in words]
    return ' '.join(new_words)

tqdm.pandas()
train['posts'] = train['posts'].progress_apply(removeStopwords)
train['posts'] = train['posts'].progress_apply(replaceStemwords)

train.posts = train.posts.progress_apply(lambda x: removeStopwords(replaceStemwords(x)))

# test data에도 적용
test.posts = test.posts.progress_apply(lambda x: removeStopwords(replaceStemwords(x)))

X = train.posts
Y= train.type

X_train, X_valid, Y_train, Y_valid = train_test_split(X, Y, test_size=0.2, random_state=1)

#모델 훈련
text_clf = Pipeline([('tfidf',TfidfVectorizer()),('clf',LinearSVC(C=0.3))])
text_clf.fit(X_train, Y_train)

# valid 데이터의 mbti 예측
pred = text_clf.predict(X_valid)
print("pred",pred)

# valid data에서의 정확도
accuracy = accuracy_score(pred, Y_valid)
print("accuracy",accuracy)

# # train 데이터프레임과 test 데이터프레임을 합친다고 가정
# data = pd.concat([train, test], axis=1)
# print(data.head())