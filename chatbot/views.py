from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from reportlab.pdfgen import canvas
import json, requests

VERIFY_TOKEN = '13thnov2016'
PAGE_ACCESS_TOKEN='EAADKnMFiOeABAHj30Am6HxYXAUd7IwJV3zNt5STau6yKADNHS8OPAxqBe2MCQ98CLuUDOZA4bqFZCoqCBT4oBMMff91oFpJ2Cos5dAwMy9DiFHA28faUciQqeGqmZByKoNrsOZCSaQFa1WOTmoDwdv8kNgof10EAJUW9ilzG2wZDZD'
c=canvas.Canvas('file.pdf')

def index(request):
	return HttpResponse('hi')

def handle_quickreply(fbid,payload):
	pass

def logg(text,symbol='*'):
	return symbol*10 + text + symbol*10

def post_fb_msg(fbid,message):
	post_fb_url='https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	output_text = message
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": output_text }})
	status1 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg)
	print status1.json()

class MyChatBotView(generic.View):
	def get(self,request,*args,**kwargs):
		if self.request.GET['hub.verify_token']==VERIFY_TOKEN:
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('oops invalid token')

	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return generic.View.dispatch(self,request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		incoming_message=json.loads(self.request.body.decode('utf-8'))
		print incoming_message
		for entry in incoming_message['entry']:
			for message in entry['messaging']:
				try:
					if 'quick_reply' in message['message']:
						handle_quickreply(message['sender']['id'],message['message']['quick_reply']['payload'])
						return HttpResponse()

				except Exception as e:
					print e

				try:
					sender_id = message['sender']['id']
					message_text = message['message']['text']
					post_fb_msg(sender_id,message_text)
				except Exception as e:
					print e

				try:
					if 'attachments' in message['message']:
						url = message['message']['attachments'][0]['payload']['url']
						print 'Image URL=%s' %url
					else:
						print logg(message['message'],'<>')
				except Exception as e:
					print e

		return HttpResponse()