from django.forms import ModelForm
from .models import Log, Acronyms, Tag_QA


class LogForm(ModelForm):
    class Meta:
        model = Log
        fields = '__all__'


class AcronymsForm(ModelForm):
    class Meta:
        model = Acronyms
        fields = '__all__'
        
class Tag_QAForm(ModelForm):
    class Meta:
        model = Tag_QA
        fields = ['question','answer']
        
