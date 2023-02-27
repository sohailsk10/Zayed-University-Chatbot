from django.forms import ModelForm
from .models import Log, Acronyms


class LogForm(ModelForm):
    class Meta:
        model = Log
        fields = '__all__'


class AcronymsForm(ModelForm):
    class Meta:
        model = Acronyms
        fields = '__all__'
        
