from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
# from .utils import string_similarity


STOP_WORDS = stopwords.words('english')
STOP_WORDS.remove('about')
STOP_WORDS.append('get')
STOP_WORDS.append('pull')
STOP_WORDS.append('list')

STOP_WORDS_AR = set(stopwords.words('arabic'))
PS = PorterStemmer()
LEMMATIZER = WordNetLemmatizer()


def remove_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in STOP_WORDS])


def pre_process(text):
    text = text.lower().replace(",", " ").replace(".", " ").replace("_", " ").replace("-", " ")
    text = remove_stopwords(text)
    words = word_tokenize(text)
    text = ""
    for word in words:
        if word == words[-1]: text += LEMMATIZER.lemmatize(PS.stem(word))
        else: text += LEMMATIZER.lemmatize(PS.stem(word)) + " "
    return text
