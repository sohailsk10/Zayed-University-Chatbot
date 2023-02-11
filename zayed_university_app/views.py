from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from spacy_langdetect import LanguageDetector
import spacy
from spacy.tokens import Doc, Span
from googletrans import Translator
from spacy.language import Language
from .models import *
from difflib import SequenceMatcher
import json
import xml.etree.ElementTree as ET
import requests
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import render_to_pdf
from django.http import HttpResponse
from django.views.generic import View
import xlwt
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from autocorrect import Speller
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import pandas as pd
import nltk
from nltk.corpus import stopwords
from numpy import savetxt
from numpy import loadtxt
import numpy as np
import glob
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from keybert import KeyBERT
from .cosine_similarity_fn import *
from django.core.serializers import serialize
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib import messages

EXTENSTION_LIST = ["JPG", "PDF", "DOC", "PNG", "DOCX", "GIF", "XLSX", "JPEG", "ASPX", "ASP"]

tag_model = SentenceTransformer('bert-base-nli-mean-tokens')
# kw_model = KeyBERT(model='all-mpnet-base-v2')

TAG_DF = pd.DataFrame(list(Tag_QA.objects.all().values()))

try:
    TAG_DF['q_tag'] = np.arange(len(TAG_DF))
    TAG_DF['title'] = TAG_DF['question']
    TAG_DF['path'] = TAG_DF['answer']
    TAG_DF['bert_keyword'] = TAG_DF['keywords']
    print("TAGDF", TAG_DF.head())

    TAG_QUESTION_VEC = tag_model.encode(TAG_DF['title'])
except:
    pass

model = SentenceTransformer('bert-base-nli-mean-tokens')
kw_model = KeyBERT(model='all-mpnet-base-v2')

all_csv_ = []
q_tag = 0
file_path = r"zayed_university_app/remove_404_csv"
# file_path = r"zayed_university_app/Gcd_files_csv"
csv_files = glob.glob(os.path.join(file_path, "*.csv"))
for f in csv_files:
    df = pd.read_csv(f)
    for index, row in df.iterrows():
        try:
            path = row['path']
            try:
                title = row['title']
            except:
                title = row['name']
            try:
                created_on = row['created-on']
            except:
                created_on = row['created_on']
        except:
            title = row['ServiceName']
            path = row['GeneratedLink']
            created_on = 1

        all_csv_.append([q_tag, title, path, created_on])
        q_tag += 1

NEW_DF = pd.DataFrame(all_csv_, columns=['q_tag', 'title', 'path', 'timestamp'])
# print(NEW_DF.head())
print("IN Encoding")
# QUESTION_VEC = loadtxt('QUESTION_VEC.csv', delimiter=',')
# QUESTION_VEC = model.encode(NEW_DF['path'])
# np.save('data.npy', QUESTION_VEC)
QUESTION_VEC = np.load('data.npy')
# savetxt('QUESTION_VEC_ZUCC.csv', QUESTION_VEC, delimiter=",")
print("Encoding Done")



nltk.download('stopwords')
_stop_words = stopwords.words('english')
_stop_words_ar = stopwords.words('arabic')


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
            name = j[0]
            if i.upper().strip() in name.upper().strip() or i.upper().strip() == name.upper().strip():
                _main_list.append([string_similarity(i, name), j])

    return _main_list


def list_to_str(_list):
    _str = ""
    if len(_list) > 1:
        for i in _list:
            if i == _list[-1]:
                _str += i

            else:
                _str += i + " "

    return _str


workspace_id = 'lMpsX8-ivT4J5jaAZRo4cNUnotfqOO-_Vp2zia532An5'
workspace_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/dbb25da5-56bd-4b0c-ac66-62db88b266a6'
assistant_id_eng = '20a3ca09-8ae6-4c62-ae83-b9f9d1f7e394'
assistant_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/dbb25da5-56bd-4b0c-ac66-62db88b266a6'
assistant_id_ar = '67525f3e-6b3d-4474-a957-dfe0ee55730f'
assistant_id_crawl = '498b1e0a-15c0-47c9-9204-829053559b00'
assistant_crawl_json_id = '4c8f53fc-7293-43dd-970c-fba16887b8b2'

cont = {}
translator = ''
# assistant = ''
session_id_ = ''
spell = Speller(lang='en')


def create_lang_detector(nlp, name):
    return LanguageDetector()


Language.factory("language_detector", func=create_lang_detector)
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('language_detector', last=True)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


global assistant
authenticator = IAMAuthenticator(workspace_id)
assistant = AssistantV2(version='2021-06-14', authenticator=authenticator)
assistant.set_service_url(assistant_url)


def get_data(_dict):
    return _dict['event_type'], _dict['event_question'], _dict['user_email']


def string_similarity(str1, str2):
    result = SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()

def remove_duplicates(input_list):
    output_list = []
    for item in input_list:
        if item not in output_list:
            output_list.append(item)
    return output_list

@csrf_exempt
def get_response_from_watson(request):
    _data = JSONParser().parse(request)
    ip = request.META.get('REMOTE_ADDR')

    try:
        event_type, text, user_email = get_data(_data)
        session_id_ = _data['session_value']
    except:
        text = ''
        session_id_ = ''

    print('RIGHT SPELLING', spell(text),
          _data['spell_check_bool'], _data['spell_check_bool'] == True)
    if spell(text) != text and _data['spell_check_bool'] == True:
        uncorrect = spell(text).lower()
        if "university" in uncorrect.lower():
            u_list = uncorrect.split()
            uni_pos = u_list.index("university")
            print(u_list, uni_pos)
            try:
                if u_list[uni_pos-1] == "based":
                    u_list[uni_pos-1] = "zayed"
            except:
                pass
            print("----------", u_list)
            res = ' '.join([str(elem) for elem in u_list])

            if res.lower() != text.lower():
                return JsonResponse({'session_id': session_id_, 'answer': f'{res}', 'intent': 'spell'})

            else:
                text = res
            
    # return JsonResponse({'session_id': session_id_, 'answer': f'{spell(text)}', 'intent': 'spell'})

    doc = nlp(text.upper())

    if session_id_ == '' and doc._.language['language'] == 'ar':
        session_id_ = assistant.create_session(
            assistant_id_ar).get_result()['session_id']
        response = assistant.message(assistant_id=assistant_id_ar, session_id=session_id_, input={'text': text},
                                     context=cont)
    else:
        session_id_ = assistant.create_session(
            assistant_id_eng).get_result()['session_id']
        response = assistant.message(assistant_id=assistant_id_eng, session_id=session_id_, input={'text': text},
                                     context=cont)
        print("assistant_id_eng")

    res = response.get_result()
    # print('RESPONSE ', res)

    try:
        res_conf = res['output']['intents'][0]['confidence']
        print("CONF", res_conf)
    except:
        try:
            res_conf = res['output']['generic'][0]['primary_results'][0]['result_metadata']['confidence']
            print("--", res_conf)
        except:
            res_conf = 0 if res['output']['generic'][0]['header'] == "I searched my knowledge base, but did not find anything related to your query." else 0
            print("---", res_conf)
    print(len(res['output']['intents']) > 0, res_conf > 0.85)
    if len(res['output']['intents']) > 0 and res_conf > 0.85:
        intents = res['output']['intents'][0]['intent']
        print("intents", intents)
    else:
        intents = ""
        print("Empty Intent")

        _text = text.lower()
        _text = _text.replace("'", "")
        _text = text.lower().replace('zayed', '').replace('university', '')

        _input_list = text.split(' ')

        _input_list = remove_custom('i', _input_list)
        _input_list = remove_custom('a', _input_list)

        for i in _input_list:
            if i.lower().strip() in _stop_words:
                _text = _text.replace(i, "")

        for i in _input_list:
            for j in _stop_words_ar:
                if i.upper().strip() == j.upper().strip():
                    _text = _text.replace(i, "")

        _main_input = _text.split(" ")
        _main_input_list = [i for i in _main_input if i]

        _main_input_list = remove_custom('i', _main_input_list)
        _main_input_list = remove_custom('a', _main_input_list)

    
        keywords = kw_model.extract_keywords(text.strip().lower(), keyphrase_ngram_range=(1, 7), stop_words='english', use_mmr=True, diversity=0.7, highlight=False, top_n=10)
        print("keywords", keywords)
        print('Before command dictionary')
        keywords_list = list(dict(keywords).keys())
        print("keywords_list[0]", keywords_list[0])
        questions_asked = [keywords_list[0]]
        questions_asked_vec = tag_model.encode(questions_asked)
        # questions_asked_vec = loadtxt('questions_asked_vec.csv', delimiter=',')
        try:
            res, res_list, conf = cosine_similarity_fn(TAG_DF, questions_asked_vec, TAG_QUESTION_VEC)
        except:
            conf = 0.0
        print("conf", conf)
        if conf < 0.65:
            print("Checking on every file because of low confidence")
            questions_asked_vec = model.encode(questions_asked)
            res, res_list, conf = cosine_similarity_fn(NEW_DF, questions_asked_vec, QUESTION_VEC)
        print("#1", len(res_list), res_list)
        res_list = remove_duplicates(res_list)
        print(res_list)
        # res_list = list(set(res_list))
        # print("#2", len(res_list))
        print("res", res)
        # print("res_list", res_list)
        main_df = pd.DataFrame(res_list, columns=['path'])
        main_df.to_csv("Main_df.csv")
        main_df = main_df.drop_duplicates(subset="path", keep="last")
        # main_df = main_df.drop_duplicates()
        print(main_df.head(5))
        top_df1 = main_df.head(5).values.tolist()
        final_df = []
        temp = True
        for i in res_list:
            for j in EXTENSTION_LIST:
                if j.upper() in i.upper() and temp:
                    temp = False
                    final_df.append(i)
            if temp:
                final_df.append(i + ".aspx")
        final_df = final_df[:5]
        print("final_df", final_df)
        # top_df1 = [i[0] + ".aspx" for i in top_df1]
        # top_df1 = [i[0] if  in i[0]  else i[0] + ".aspx" for i in top_df1]


        df1_str = ""
        for i in final_df:
            df1_str += i + "\n"
        print("df1_str", df1_str)

        if len(top_df1) > 0:
            return JsonResponse({'session_id': session_id_, 'answer': df1_str, 'intent': 'General', 'url': final_df})

        else:
            eid = EventType.objects.get(id=int(5))
            Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=text,
                               event_answer='', intent='General')
            return JsonResponse(
                {'session_id': session_id_,
                    'answer': "Sorry, I am not able to detect the language you are asking."})

    try:
        output = res['output']['generic'][0]['primary_results'][0]['highlight']['answer']
    except:
        try:
            output = res['output']['generic'][0]['additional_results'][0]['highlight']['answer']
        except:
            try:
                output = res['output']['generic'][0]['text']
                print("OUTPUT", output, intents)
                if intents.lower() == "greetings" or intents.lower() == "start_greetings" or intents.lower() == "end_greetings" or intents.lower() == "live_agent":
                    return JsonResponse({'session_id': session_id_, 'answer': output, 'intent': intents})
            except:
                print("In 3rd Except")
                eid = EventType.objects.get(id=int(5))
                Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=text,
                                   event_answer='', intent=intents)
                return JsonResponse(
                    {'session_id': session_id_,
                     'answer': "Sorry, I am not able to detect the language you are asking."})

    if len(output) > 1:
        temp = ''
        for o in output:
            temp += o + ' '
        message = cleanhtml(temp)

    else:
        message = cleanhtml(output[0])
    if message == '':
        message = cleanhtml(res['output']['generic'][0]
                            ['primary_results'][0]['answers'][0]['text'])
    message = cleanhtml(message)
    eid = EventType.objects.get(id=int(event_type))
    Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=text,
                       event_answer=message, intent=intents)
    return JsonResponse({'session_id': session_id_, 'answer': message, 'intent': intents})


@csrf_exempt
def login(request):
    _data = JSONParser().parse(request)
    event_type, event_question, user_email = get_data(_data)
    ip = request.META.get('REMOTE_ADDR')
    intents = _data['intent']
    eid = EventType.objects.get(id=int(event_type))
    Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=event_question,
                       event_answer='', intent=intents)

    return JsonResponse({'status': 'success'})


@csrf_exempt
def wrong_answer(request):
    _data = JSONParser().parse(request)
    event_type, event_question, user_email = get_data(_data)
    ip = request.META.get('REMOTE_ADDR')
    event_answer = _data['event_answer']
    intents = _data['intent']
    eid = EventType.objects.get(id=int(3))
    print('[INFO]', event_type, event_question, user_email,
          ip, event_answer, intents, eid.description)
    Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=event_question,
                       event_answer=event_answer, intent=intents)

    return JsonResponse({'status': 'success'})


@csrf_exempt
def reset_count(request):
    _data = JSONParser().parse(request)
    event_type, event_question, user_email = get_data(_data)
    ip = request.META.get('REMOTE_ADDR')
    event_answer = _data['event_answer']
    intents = _data['intent']
    eid = EventType.objects.get(id=int(event_type))
    Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=event_question,
                       event_answer=event_answer, intent=intents)

    return JsonResponse({'status': 'success'})


def is_valid_queryparam(param):
    return param != '' and param is not None


# Common Global variable
log_exp = None


@login_required
def advance_filter(request):
    depart_name = request.session['depart']
    global log_exp

    if depart_name != 'SuperAdmin':
        log_ = Log.objects.filter(
            intent=depart_name).order_by('-user_datetime')
    else:
        log_ = Log.objects.all().order_by('-user_datetime')

    event_type_id_exact_query = request.GET.get('etype')
    print("type = ", type(event_type_id_exact_query))
    user_email = request.GET.get('email')
    event_question = request.GET.get('quest')
    event_answer = request.GET.get('ans')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    intent_exact_query = request.GET.get('dtype')

    if is_valid_queryparam(event_type_id_exact_query):
        log_ = log_.filter(event_type_id=event_type_id_exact_query)

    if is_valid_queryparam(user_email):
        log_ = log_.filter(user_email__icontains=user_email)

    if is_valid_queryparam(event_question):
        log_ = log_.filter(event_question__icontains=event_question)

    if is_valid_queryparam(event_question):
        log_ = log_.filter(event_question__icontains=event_question)
    if is_valid_queryparam(event_answer):
        log_ = log_.filter(event_answer__icontains=event_answer)

    if is_valid_queryparam(date_min):
        log_ = log_.filter(user_datetime__gte=date_min)

    if is_valid_queryparam(date_max):
        log_ = log_.filter(user_datetime__lte=date_max)

    if is_valid_queryparam(intent_exact_query):
        log_ = log_.filter(intent=intent_exact_query)

    dept = Log.objects.all().values_list('intent', flat=True).distinct()
    dept_list = [i for i in dept if i != '']

    event_ = EventType.objects.all()
    # event_list = [i for i in event_ if i != '']
    # print("event_type_id>>> ", event_.description)

    log_exp = log_

    context = {
        'log_': log_,
        'dept_list': dept_list,
        'event_': event_,
        'depart_name': depart_name,
        'admin_type': request.session['admin_type'],

        'event_type_id_exact_query': event_type_id_exact_query,
        'user_email': user_email,
        'event_question': event_question,
        'event_answer': event_answer,
        'date_min': date_min,
        'date_max': date_max,
        'intent_exact_query': intent_exact_query

    }

    return render(request, 'home/advance_filter.html', context)


# Opens up page as PDF
class ViewPDF(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'log_': Log.objects.all()
        }

        pdf = render_to_pdf('home/filter_template.html', context)
        if pdf:
            return HttpResponse(pdf, content_type='application/pdf')
        return HttpResponse("PDF Not Found.")

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


def admin_check(user):
    if user.is_staff or user.is_superuser:
        return True
    return False


@login_required
@user_passes_test(admin_check)
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Event ID', 'User Email', 'Question', 'Answer',
               'Date Time', 'Department']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Log.objects.all().values_list(
        'event_type_id__description', 'user_email', 'event_question',
        'event_answer', 'user_datetime', 'intent')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    if wb:
        return response
    return HttpResponse("No Data Found.")


# # Automatically downloads Filtered PDF file
# class FilterPDF(LoginRequiredMixin, View):

#     def get(self, request, *args, **kwargs):
#         global log_exp

#         context = {
#             'log_': log_exp,
#         }
#         pdf = render_to_pdf('home/filter_template.html', context)
#         if pdf:
#             return HttpResponse(pdf, content_type='application/pdf')
#         return HttpResponse("PDF Not Found.")

# Automatically downloads Filtered PDF file
class FilterPDF(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        global log_exp
        len_log = len(log_exp)
        temp_l = []

        for i in log_exp:
            if 'http' in i.event_answer:
                i = i.event_answer.split()
                # print(">> ", i)
                tmp_str = ''
                for i_ in i:
                    temp_i = ''
                    if i_.startswith('http') and len(i_) > 45:
                        while len(i_) > 45:
                            # print("in while 45", i_)
                            temp_i += i_[:45] + '\n'
                            i_ = i_[45:]
                        if len(i_) > 0:
                            temp_i += i_
                        tmp_str += '\n' + temp_i + ''
                    else:
                        tmp_str += i_ + ' '
                    # print("after if-else", tmp_str)
                temp_l.append(tmp_str.strip())
            else:
                temp_l.append(i.event_answer)

        context = {
            'len_log': len_log,
            'log_': log_exp,

            'zip_': zip(log_exp, temp_l)
        }
        pdf = render_to_pdf('home/filter_template.html', context)
        if pdf:
            return HttpResponse(pdf, content_type='application/pdf')
        return HttpResponse("PDF Not Found.")


# Automatically downloads Filtered Excel file
@login_required
def filter_excel(request):
    global log_exp
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Event ID', 'User Email', 'Question', 'Answer',
               'Date Time', 'Department']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = log_exp.values_list(
        'event_type_id__description', 'user_email', 'event_question',
        'event_answer', 'user_datetime', 'intent')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    if wb:
        return response
    return HttpResponse("No Data Found.")



@login_required
def answer_rectification(request):
    depart_name = request.session['depart']
    global log_exp

    if depart_name != 'SuperAdmin':
        log_ = Log.objects.filter(
            intent=depart_name).order_by('-user_datetime')
    else:
        log_ = Log.objects.all().order_by('-user_datetime')

    event_type_id_exact_query = request.GET.get('etype')
    # print("type = ", type(event_type_id_exact_query))
    user_email = request.GET.get('email')
    event_question = request.GET.get('quest')
    event_answer = request.GET.get('ans')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    intent_exact_query = request.GET.get('dtype')


    if is_valid_queryparam(event_type_id_exact_query):
        log_ = log_.filter(event_type_id=event_type_id_exact_query)

    if is_valid_queryparam(user_email):
        log_ = log_.filter(user_email__icontains=user_email)

    if is_valid_queryparam(event_question):
        log_ = log_.filter(event_question__icontains=event_question)

    if is_valid_queryparam(event_question):
        log_ = log_.filter(event_question__icontains=event_question)
    if is_valid_queryparam(event_answer):
        log_ = log_.filter(event_answer__icontains=event_answer)

    if is_valid_queryparam(date_min):
        log_ = log_.filter(user_datetime__gte=date_min)

    if is_valid_queryparam(date_max):
        log_ = log_.filter(user_datetime__lte=date_max)

    if is_valid_queryparam(intent_exact_query):
        log_ = log_.filter(intent=intent_exact_query)

    dept = Log.objects.all().values_list('intent', flat=True).distinct()
    dept_list = [i for i in dept if i != '']

    event_ = EventType.objects.all()

    log_exp = log_
    # print("<++++++++++++++>", log_)
    ans_lst = []
    for lg in log_:
        if "\n" in lg.event_answer or 'https:' in lg.event_answer:    
            print(">", ans_lst.append(lg.event_answer))
            # print("=>", ('\n'+lg.event_answer))
    # print("------",ans_lst)
    context = {
        'log_': log_,
        'dept_list': dept_list,
        'event_': event_,
        'depart_name': depart_name,
        'admin_type': request.session['admin_type'],
        'event_type_id_exact_query': event_type_id_exact_query,
        'user_email': user_email,
        'event_question': event_question,
        'event_answer': event_answer,
        'date_min': date_min,
        'date_max': date_max,
        'intent_exact_query': intent_exact_query,
        'rt_ans_list':ans_lst,
    }
    

    return render(request, 'home/rectification.html', context)


def get_keyword_KeyBERT(text):
    kw_model = KeyBERT(model='all-mpnet-base-v2')
    keywords = kw_model.extract_keywords(text, 
                                        keyphrase_ngram_range=(1, 7), 
                                        stop_words='english', 
                                        highlight=False,
                                        top_n=10)
    keywords_list= list(dict(keywords).keys())
    return keywords_list




@login_required
def get_qa_category(request):
    depart_name = request.session['depart']
    categories = QA_Category.objects.all()
    context = {
        'depart_name': depart_name,
        'admin_type': request.session['admin_type'],
        'categories' : categories
    }
    return render(request, 'home/qa_category_update.html', context)


def get_plain_string(_string):
    return ''.join(e for e in _string if e.isalnum())




@login_required
def get_tag_qa(request, id):
    # print("log id -", id)
    depart_name = request.session['depart']
    log_id = Log.objects.get(id =id)
    event_type_id = log_id.event_type_id
    user_email = log_id.user_email
    event_question = log_id.event_question
    event_answer = log_id.event_answer
    keyword_lst = get_keyword_KeyBERT(event_question)
    # print("keyword_lst - ", keyword_lst)
    intent = log_id.intent
    categories = QA_Category.objects.filter(parent_id__exact='')
    all_categories = QA_Category.objects.all()
    data = serialize("json",all_categories, fields=('id', 'parent_id','description'))
    if request.method == "POST":
        print(request.POST)
        question = request.POST['quest']
        extracted_key = request.POST['key_extracted']

        temp_ex_key = []
        for i in extracted_key.split(','):
            temp = ''
            for j  in i.split(' '):
                temp += get_plain_string(j) + " "
            temp_ex_key.append(temp)


        add_keywords = request.POST['add_key']
        temp_add_key =  []
        for i in add_keywords.split(','):
            temp = ''
            for j  in i.split(' '):
                temp += get_plain_string(j) + " "
            temp_add_key.append(temp)
        # print("temp_add_key - ", temp_add_key)
        mix_list = temp_ex_key + temp_add_key
        mix_list = list_to_str(mix_list)
        mix_list = mix_list.lower().replace("zayed", "")
        mix_list = mix_list.lower().replace("university", "")
        answer = request.POST['ans']
        ctype = request.POST.getlist('ctype')
        # print(">>>>>>>", ctype)
        save_data = Tag_QA(
            question=question,
            keywords= mix_list,
            answer =answer,
            category = ctype)

        save_data.save()   
        messages.success(request, "record updated sucessfully!!!")
        context = {
            'depart_name': depart_name,
            'admin_type': request.session['admin_type'],
        }
        return HttpResponseRedirect(reverse('advance_filter'))

    context = {
         'event_type_id' : event_type_id,
         'user_email' : user_email,
         'event_question' : event_question,
         'event_answer' : event_answer,
         'intent' : intent,
         'keyword_list':keyword_lst,
         'categories':categories,
         'data':data,
         'depart_name': depart_name,
         'admin_type': request.session['admin_type'],
    }
    return render(request, 'home/tag_qa_update.html', context)


@login_required
def get_tag_qa_1(request):
    depart_name = request.session['depart']

    tg_qa = Tag_QA.objects.all()
    context = {
        'depart_name': depart_name,
        'admin_type': request.session['admin_type'],
        'tag_and_qa' : tg_qa
    }
    return render(request, 'home/tag_qa_update.html', context)

def get_child_categories(request, parent):
    # print(">>", parent)
    categories =  QA_Category.objects.filter(parent_id = parent)
    # print("---", len(categories), categories)
    data = serialize("json",categories, fields=('id', 'description'))
    return HttpResponse(data, content_type="application/json")

## answer search
# @login_required
# def answer_search(request):
#     depart_name = request.session['depart']
    
#     question = request.GET.get('question')
#     answer = request.GET.get('answer')
#     keywords = request.GET.get('keywords')


#     if is_valid_queryparam(question):
#         tag_qa_ = Tag_QA.filter(question=question)

#     if is_valid_queryparam(answer):
#         tag_qa_ = tag_qa_.filter(answer__icontains=answer)

#     if is_valid_queryparam(keywords):
#         tag_qa_ = tag_qa_.filter(keywords__icontains=keywords)

   
#     context = {
#         'tag_qa': tag_qa_,
#         'id':id,
#         'depart_name': depart_name,
#         'admin_type': request.session['admin_type'],
#         'question': question,
#         'answer': answer,
#         'keywords': keywords,

#     }

#     return render(request, 'home/answer_search.html', context)