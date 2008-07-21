# -*- coding: utf-8 -*-
import datetime

from django.template.loader import render_to_string
from django.http import HttpResponse

def index(request):
    SAMPLE_BEST = {
            'todays_best_list': [
                {'title': '아라가 새로 바뀌었다!', 'date': datetime.datetime.now(), 'reply_count': 213},
                {'title': '아라 참 멋지네요', 'date': datetime.datetime.now(), 'reply_count':56},
                {'title': '우왕ㅋ국ㅋ', 'date': datetime.datetime.now(), 'reply_count':44},
                ],
            'weekly_best_list': [
                {'title': '아라가 새로 바뀌었다!', 'date': datetime.datetime.now(), 'reply_count': 213},
                {'title': '아라 참 멋지네요', 'date': datetime.datetime.now(), 'reply_count':56},
                {'title': '우왕ㅋ국ㅋ', 'date': datetime.datetime.now(), 'reply_count':44},
                ],
            }
    rendered = render_to_string('index.html', SAMPLE_BEST)
    return HttpResponse(rendered)