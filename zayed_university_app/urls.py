from django.urls import path
# from .views import *
from django.conf.urls import url
from . import views
urlpatterns = [
    path('login/', views.login),
    path('watson-assistant/', views.get_response_from_watson, name="watson-assistant"),
    path('reset/', views.reset_count),
    path('wrong_answer/', views.wrong_answer, name="wrong_answer"),
    # path('advance_filter/', advance_filter, name='advance_filter')
    path('advance_filter/', views.advance_filter, name='advance_filter'),

    path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    path('filter_pdf/', views.FilterPDF.as_view(), name="filter_pdf"),

    path('export_excel/', views.export_excel, name="export_excel"),
    path('filter_excel/', views.filter_excel, name="filter_excel"),
    
    # path('answer_rectification/', views.answer_rectification, name='answer_rectification'),

    # qa_category
    path('get_qa_category/', views.get_qa_category, name='get_qa_category'),
    # tag_qa
    path('get_tag_qa/<id>/', views.get_tag_qa,  name='get_tag_qa'),
    path('get_tag_qa/', views.get_tag_qa_1,  name='get_tag_qa'),
    path('get_child_categories/<parent>/', views.get_child_categories,  name='get_child_categories'),

]



    # path('answer_search/', answer_search, 'answer_search')