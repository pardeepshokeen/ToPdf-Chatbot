from django.conf.urls import patterns, include, url
from chatbot.views import *

urlpatterns = patterns('',
	url(r'^$', index),
	url(r'^pdf$', pdf_view),
	url(r'^facebook_auth/?$', MyChatBotView.as_view()),
)