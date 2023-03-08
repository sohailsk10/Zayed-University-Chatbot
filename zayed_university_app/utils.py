from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from .models import QA_Category 
from xhtml2pdf import pisa



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def truncate_list(uuid_list):
    qa_category = QA_Category.objects.all()
    temp = []
    for i in range(len(uuid_list)):
        if i == 0: temp.append(uuid_list[i].split("'")[1])
        elif i == len(uuid_list) - 1: temp.append(uuid_list[i].split("'")[1])
        else: temp.append(uuid_list[i].split("'")[1])
        
    temp_category = []
    for uid in temp:
        for category in qa_category:
            if str(category.id) == str(uid):
                temp_category.append(category.description)
    
    return temp_category