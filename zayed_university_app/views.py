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
from .models import Log, EventType
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
from gensim.parsing.preprocessing import remove_stopwords
from autocorrect import Speller
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import pandas as pd
import nltk
from nltk.corpus import stopwords
from datetime import datetime
import http.client
from urllib.parse import urlsplit
import glob
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .cosine_similarity_fn import *
from keybert import KeyBERT
import numpy as np
from .models import *
from django.core.serializers import serialize
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib import messages
import difflib


workspace_id = 'lMpsX8-ivT4J5jaAZRo4cNUnotfqOO-_Vp2zia532An5'
workspace_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/dbb25da5-56bd-4b0c-ac66-62db88b266a6'
assistant_id_eng = '20a3ca09-8ae6-4c62-ae83-b9f9d1f7e394'
assistant_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/dbb25da5-56bd-4b0c-ac66-62db88b266a6'
assistant_id_ar = '67525f3e-6b3d-4474-a957-dfe0ee55730f'
assistant_id_crawl = '498b1e0a-15c0-47c9-9204-829053559b00'
assistant_crawl_json_id = '4c8f53fc-7293-43dd-970c-fba16887b8b2'

nltk.download('stopwords')
_stop_words = stopwords.words('english')
_stop_words_ar = stopwords.words('arabic')
_stop_words.append('get')

tag_model = SentenceTransformer('bert-base-nli-mean-tokens')
model = SentenceTransformer('bert-base-nli-mean-tokens')
kw_model = KeyBERT(model='all-mpnet-base-v2')

EXTENSTION_LIST = ["JPG", "PDF", "DOC", "PNG", "DOCX", "GIF", "XLSX", "JPEG", "ASPX", "ASP"]


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
            name = j[1]
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



cont = {}
translator = ''
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
    return _dict['event_type'], _dict['event_question'].lower(), _dict['user_email']


def remove_duplicates(input_list):
    output_list = []
    for item in input_list:
        if item not in output_list:
            output_list.append(item)
    return output_list


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
    
    uncorrect = spell(text).lower()
    u_list = uncorrect.split()
    temp = u_list.copy()
    temp_1 = text.split()
    if "university" in uncorrect or "university?" in uncorrect:
        try:
            uni_pos = u_list.index("university")
        except:
            try:
                uni_pos = u_list.index("university?")
            except:
                uni_pos = u_list.index("university's")
        try:
            if u_list[uni_pos - 1] == "based":
                u_list[uni_pos - 1] = "zayed"
            
            temp[uni_pos] = "university"
        except:
            pass

    res = ' '.join([str(elem) for elem in u_list])
    if res.lower() != text.lower() and _data['spell_check_bool'] == True:
        print({'session_id': "session_id_", 'answer': f'{res}', 'intent': 'spell'})
        return JsonResponse({'session_id': session_id_, 'answer': f'{res}', 'intent': 'spell'})

    else:
        res = ' '.join([str(i) for i in temp_1])
        text = res

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

    res = response.get_result()

    try:
        res_conf = res['output']['intents'][0]['confidence']
    except:
        try:
            res_conf = res['output']['generic'][0]['primary_results'][0]['result_metadata']['confidence']
        except:
            res_conf = 0 if res['output']['generic'][0][
                                'header'] == "I searched my knowledge base, but did not find anything related to your query." else 0
    if len(res['output']['intents']) > 0 and res_conf > 0.85:
        intents = res['output']['intents'][0]['intent']
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
    

    else:
        _text = text.lower()
        _main_input = str_to_list(_text)
        _text = remove_zu(_main_input, "zayed university")
        _main_input = str_to_list(_text)
        _main_input_list = [i for i in _main_input if i]
        _main_input_list = remove_custom('i', _main_input_list)
        _main_input_list = remove_custom('a', _main_input_list)
        _main_input_list = remove_custom('the', _main_input_list)
        _main_input_string = list_to_str(_main_input_list)
        try:
            tag_df = pd.DataFrame(list(Tag_QA.objects.all().values()))
            tag_df['q_tag'] = np.arange(len(tag_df))
            tag_df['title'] = tag_df['question']
            tag_df['path'] = tag_df['answer']
            tag_df['bert_keyword'] = tag_df['keywords']

            all_csv = []
            df_ratios = get_ratios_from_df([_main_input_string], tag_df, all_csv)

            tag_df_ratios = pd.DataFrame(df_ratios, columns=['ratio', 'question', 'answer'])
            main_df = tag_df_ratios.drop_duplicates(subset="answer", keep="last")

            top_tag_df = main_df.sort_values('ratio', ascending=False).head(5).values.tolist()
            tag_df_top_ratio = top_tag_df[0][0]
        except Exception as e:
            print("In Exception", e)
            tag_df_top_ratio = 0.0
        
        if float(tag_df_top_ratio) > 0.60:
            top_tag_df_links = [i[2] for i in top_tag_df]
            top_tag_df_extension = get_proper_extension(top_tag_df_links)

            tag_df_str = ""
            for i in top_tag_df_extension:
                tag_df_str += i + "\n"
                
            if len(top_tag_df_extension) > 0:
                return JsonResponse({'session_id': session_id_, 'answer': tag_df_str, 'intent': 'General', 'url': top_tag_df_extension})

        intents = ""
        main_df = pd.DataFrame()
        all_csv_ = []

        path = r"zayed_university_app/remove_404_csv"
        csv_files = glob.glob(os.path.join(path, "*.csv"))
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
                    path = row['ServiceUrl']
                    created_on = 1

                all_csv_.append([path, title, created_on])

    all_csv = []
    all_csv = get_ratios(_main_input_list, all_csv_, all_csv)
    
    _main_input_string = list_to_str(_main_input_list)
    
    links_ratio = []
    for i in all_csv:
        links_ratio.append([i[0], string_similarity(i[1][1], _main_input_string), i[1][1], i[1][0], i[1][2]])

    max_ratio = max(links_ratio, key=lambda x: x[1])[1]
    print("max_ratio", max_ratio)
    
    df1 = pd.DataFrame(links_ratio, columns=['single_ratio', 'actual_ratio', 'name', 'path', 'timestamp'])
    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    main_df = df1.drop_duplicates(subset="path", keep="last")
    top_df1 = main_df.sort_values('actual_ratio', ascending=False).head(5).values.tolist()
    
    top_df1 = [i[3] for i in top_df1]
    top_df_extension = get_proper_extension(top_df1)

    df1_str = ""
    for i in top_df_extension:
        df1_str += i + "\n"
        
    if len(top_df_extension) > 0:
        return JsonResponse({'session_id': session_id_, 'answer': df1_str, 'intent': 'General', 'url': top_df_extension})

    else:
        eid = EventType.objects.get(id=int(5))
        Log.objects.create(event_type_id=eid, user_email=user_email, user_ip=ip, event_question=text,
                        event_answer='', intent='General')
        return JsonResponse(
            {'session_id': session_id_,
            'answer': "Sorry, I am not able to detect the language you are asking."})


def get_keyword_KeyBERT(text):
    kw_model = KeyBERT(model='all-mpnet-base-v2')
    keywords = kw_model.extract_keywords(text, 
                                        keyphrase_ngram_range=(1, 7), 
                                        stop_words='english', 
                                        highlight=False,
                                        top_n=10)
    keywords_list= list(dict(keywords).keys())
    keywords_list = ','.join(keywords_list)
    return keywords_list

def get_plain_string(_string):
    return ''.join(e for e in _string if e.isalnum())

@login_required
def get_tag_qa(request, id):
    depart_name = request.session['depart']
    log_id = Log.objects.get(id =id)
    event_type_id = log_id.event_type_id
    user_email = log_id.user_email
    event_question = log_id.event_question
    event_answer = log_id.event_answer
    keyword_lst = get_keyword_KeyBERT(event_question)
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
        mix_list = temp_ex_key + temp_add_key
        mix_list = list_to_str(mix_list)
        mix_list = mix_list.lower().replace("zayed", "")
        mix_list = mix_list.lower().replace("university", "")
        answer = request.POST['ans']
        ctype = request.POST.getlist('ctype')
        save_data = Tag_QA(
            question=question,
            keywords= mix_list,
            answer =answer,
            category = ctype)

        save_data.save()   
        TAG_DF = pd.DataFrame(list(Tag_QA.objects.all().values()))
        TAG_DF['q_tag'] = np.arange(len(TAG_DF))
        TAG_DF['title'] = TAG_DF['question']
        TAG_DF['path'] = TAG_DF['answer']
        TAG_DF['bert_keyword'] = TAG_DF['keywords']
        print("TAGDF", TAG_DF.head())

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
         'event_answer' : event_answer.strip(),
         'intent' : intent,
         'keyword_list':keyword_lst,
         'categories':categories,
         'data':data,
         'depart_name': depart_name,
         'admin_type': request.session['admin_type'],
    }
    return render(request, 'home/tag_qa_update.html', context)

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
    categories =  QA_Category.objects.filter(parent_id = parent)
    data = serialize("json",categories, fields=('id', 'description'))
    return HttpResponse(data, content_type="application/json")


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


from django.http import JsonResponse

def q_key_extract(request, id):
    keywords_ = get_keyword_KeyBERT(id)
    data = {
        'keywords': keywords_,
    }
    return JsonResponse(data)