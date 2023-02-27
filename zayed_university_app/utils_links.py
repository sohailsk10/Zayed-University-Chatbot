from difflib import SequenceMatcher
import nltk
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
import hashlib
import numpy as np


EXTENSTION_LIST = ["JPG", "PDF", "DOC", "PNG", "DOCX", "GIF", "XLSX", "JPEG", "ASPX", "ASP"]
nltk.download('stopwords')
STOP_WORDS = stopwords.words('english')
STOP_WORDS.append('get')

VECTORIZE_MODEL = SentenceTransformer('bert-base-nli-mean-tokens')


def remove_custom(_char, _list):
    for i in _list:
        try:
            _list.remove(_char)
        except:
            pass

    return _list


def string_similarity(str1, str2):
    result = SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()


def get_ratios(_input_list_, _sys_, _main_list):
    for i in _input_list_:
        for j in _sys_:
            name = j[2]
            try:
                if i.upper().strip() in name.upper().strip() or i.upper().strip() == name.upper().strip():
                    _main_list.append([string_similarity(i, name), j])
            except:
                pass
    return _main_list


def get_ratios_from_df(_input_list_, _df_, _main_list):
    for i in _input_list_:
        for index, row in _df_.iterrows():
            name = row.question
            # print("name", name)
            try:
                # if i.upper().strip() in name.upper().strip() or i.upper().strip() == name.upper().strip():
                _main_list.append([string_similarity(i, name), row.question, row.answer])
            except:
                pass
    return _main_list


def list_to_str(_list):
    _str = ""
    if len(_list) >= 1:
        for i in _list:
            if i == _list[-1]:
                _str += i

            else:
                _str += i + " "

    return _str


def get_proper_extension(_list):
    final_df = []
    index_links = [link for link in _list if 'index' in link]
    other_links = [link for link in _list if 'index' not in link]
    result = index_links + other_links
    
    for i in result:
        if 'https://eservices.zu.ac.ae' in i:
            final_df.append(i)
        else:
            temp = True
            for j in EXTENSTION_LIST:
                if j in i.split("/")[-1].upper() and temp:
                    temp = False
                    final_df.append(i)
                    break
            if temp:
                final_df.append(i + ".aspx")
    
    return final_df


def remove_zu(_str_list, _str_to_insert, _sub_str="zu"):
    print("Length", len(_str_list))
    if len(_str_list) == 1:
        return _str_list[0]
    
    for i in _str_list:
        if _sub_str in i:
            idx = _str_list.index(i)
            _str_list.insert(idx, _str_to_insert)
            _str_list.pop(idx + 1)
    
    return list_to_str(_str_list)


def str_to_list(_str):
    if _str.find(" "):
        _main_input = _str.split(" ")
    else:
        _main_input = [_str]
        
    return _main_input


def remove_stopwords(_list, _original_text):
    for i in _list:
            for j in STOP_WORDS:
                if i.upper().strip() == j.upper().strip():
                    _original_text = _original_text.replace(i, "")
    
    return _original_text


def get_proper_link(link):

    _link_after = link.split(".zu.ac.ae")[-1]
    _link_before = link.split(".zu.ac.ae")[0][12:]

    if "/main/" in _link_after:
        return (_link_before + _link_after.split("/main")[-1]).replace("/", " ").replace("_", " ").replace(".", " ").strip()
    
    else:
        return (_link_before + _link_after).replace("/", " ").replace("_", " ").replace(".", " ").strip()


def get_vectorize_dict(message):
    message_dict = {}
    for word in message:
        message_dict[hashlib.sha256(word.encode('utf-8')).hexdigest()] = VECTORIZE_MODEL.encode(word)
    
    return message_dict


def transpose(char_arr):
    transposed = []
    for i in range(len(char_arr[0])):
        transposed.append([])
        for j in range(len(char_arr)):
            transposed[i].append(char_arr[j][i])
    return transposed


def ranking_cosines(cosines_list, index):
    rankings = {}
    average = np.average(cosines_list)
    rankings[index] = average

    return rankings