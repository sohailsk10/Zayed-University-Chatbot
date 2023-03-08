from __future__ import unicode_literals
from django.db import models
import uuid


def list_to_str(text_list):
    return " ".join([i for i in text_list])


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


class Tag_QA(models.Model):
    tag = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=8000)
    keywords = models.TextField()
    category = models.TextField()

    def save(self) -> None:
        acr_list = Acronyms.objects.all()
        str_list = self.question.split()
        
        for i in str_list:
            for zu_acr in acr_list:
                if zu_acr.short_form.lower() == i.lower():
                    idx = str_list.index(i)
                    str_list.insert(idx, zu_acr.long_form)
                    str_list.pop(idx + 1)
        
        self.question = list_to_str(str_list)
        return super().save()

    def _str_(self):
        return str(self.tag)


class Acronyms(models.Model):
    short_form = models.CharField(max_length=50)
    long_form = models.CharField(max_length=1000, blank=True)


    def str(self):
        return self.short_form
