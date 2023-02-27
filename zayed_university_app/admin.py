from django.contrib import admin
from .models import Log, EventType, MasterTable, QA_Category, Tag_QA, Acronyms


class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_email', 'user_ip', 'event_question', 'event_answer', 'event_type_id', 'intent', 'user_datetime')
    list_filter = ('event_type_id', 'intent', 'user_datetime',)
    search_fields = ('user_email', 'user_ip', 'event_question', 'event_answer',)
    date_hierarchy = 'user_datetime'
    ordering = ['-user_datetime']



class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')


class MasterTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer')

# QA Category
class QA_CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')
    # list_filter = ('description',)

# Tag QA
class Tag_QAAdmin(admin.ModelAdmin):
    list_display = ('tag','question','answer','keywords','category')
    # list_filter = ('question','answer','keywords','category')

class AcronymsAdmin(admin.ModelAdmin):
    list_display = ('long_form','short_form')


admin.site.register(Log, LogAdmin)

admin.site.register(EventType, EventTypeAdmin)

admin.site.register(MasterTable, MasterTableAdmin)

admin.site.register(QA_Category, QA_CategoryAdmin)
admin.site.register(Tag_QA,Tag_QAAdmin)
admin.site.register(Acronyms,AcronymsAdmin)
