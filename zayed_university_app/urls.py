from django.urls import path
from django.conf.urls import url
from . import views
from django.conf.urls import url, include
from django.views.generic import TemplateView


urlpatterns = [
    path('login/', views.login),
    path('watson-assistant/', views.get_response_from_watson, name="watson-assistant"),
    path('reset/', views.reset_count),
    path('wrong_answer/', views.wrong_answer, name="wrong_answer"),
    path('advance_filter/', views.advance_filter, name='advance_filter'),
    path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    path('filter_pdf/', views.FilterPDF.as_view(), name="filter_pdf"),
    path('export_excel/', views.export_excel, name="export_excel"),
    path('filter_excel/', views.filter_excel, name="filter_excel"),
    path('get_qa_category/', views.get_qa_category, name='get_qa_category'),
    path('get_tag_qa/<id>/', views.get_tag_qa,  name='get_tag_qa'),
    path('get_tag_qa/', views.get_tag_qa_1,  name='get_tag_qa'),
    path('get_child_categories/<parent>/', views.get_child_categories,  name='get_child_categories'),
    path('q_key_extract/<id>/', views.q_key_extract, name ='q_key_extract'),
    
    path(r'^acronyms/$', views.acronyms_list, name='acronyms_list'),
    path(r'^acronyms/create/$', views.acronyms_create, name='acronyms_create'),
    path(r'^acronyms/(?P<pk>\d+)/update/$', views.acronyms_update, name='acronyms_update'),
    path(r'^acronyms/(?P<pk>\d+)/delete/$', views.acronyms_delete, name='acronyms_delete'),
    
    path('rectified_list', views.rectified_list, name='rectified_list'),
    path('rectification_update/<pk>/update/', views.rectification_update, name='rectification_update'),
    path('rectification_delete/<pk>/delete/', views.rectification_delete, name='rectification_delete'),

]



    