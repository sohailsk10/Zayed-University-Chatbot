from __future__ import unicode_literals
from django.db import models
import uuid


class EventType(models.Model):
    description = models.CharField(max_length=20)

    def __str__(self):
        return self.description


class MasterTable(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.TextField(max_length=8000)

    def __str__(self):
        return self.question


class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type_id = models.ForeignKey(EventType, on_delete=models.CASCADE)
    user_email = models.EmailField()
    user_ip = models.GenericIPAddressField()
    event_question = models.CharField(max_length=1000)
    event_answer = models.CharField(max_length=2000)
    user_datetime = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(default='', max_length=100)


    def __str__(self):
        return self.user_email

    # added
    class Meta:
        db_table = "zayed_university_app_log"

# added for QA and category utility
class QA_Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=500)
    parent_id = models.CharField(max_length=100, blank=True)

    def _str_(self):
        return str(self.id)

    
def check_acronyms(fields):
    print("Line 50", fields)


class Tag_QA(models.Model):
    tag = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=1000, default=check_acronyms(self))
    answer = models.CharField(max_length=1000)
    keywords = models.TextField()
    category = models.TextField()

    def _str_(self):
        return str(self.tag)


    
class Acronyms(models.Model):
    short_form = models.CharField(max_length=50)
    long_form = models.CharField(max_length=1000, blank=True)


    def str(self):
        return self.short_form
