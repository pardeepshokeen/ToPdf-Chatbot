from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
import json, requests, os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VERIFY_TOKEN = '13thnov2016'
PAGE_ACCESS_TOKEN='EAADKnMFiOeABAMeUxrHrzp8X9lLxLa93BErKfI3oZBdDyvKZCXmBawIZALjL2en73JDFAbipf9EqAMGObAB4TKZAbvslp4ujRhaJqRntTl3IRZB0NG6b8i4onZBRm9FGDRIcTNZAte1VNwup7d2F52ZA8OBGqVBuyLL5AZBuE8XVrmwZDZD'
c=None
WIDTH = 'LETTER'
HEIGHT = 'LETTER'

def index(request):
	# with open(os.path.join(BASE_DIR,'file.pdf'), 'r') as pdf:
	# 	response = HttpResponse(pdf.read(), content_type='application/pdf')
	# 	response['Content-Disposition'] = 'inline;filename=some_file.pdf'
	# 	return response
	# pdf.closed
	# add('1', image)
	# quick_response('1')
	return HttpResponse('ok')

def logg(text,symbol='*'):
	return symbol*10 + text + symbol*10

def pdf_view(request):
    with open(os.path.join(BASE_DIR,'file.pdf'), 'r') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response
    pdf.closed

def add(fbid, image):
	global c
	if c is None:
		c=Canvas('file.pdf', pagesize='LETTER')
	c.drawImage(image, 0,0, width=WIDTH,height=HEIGHT)
	c.showPage()
	post_fb_url = "https://graph.facebook.com/v2.6/me/messages?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": 'Image Added Successfully' }})
	status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg)
	print status2.json()

def handle_quickreply(fbid,payload):
	post_fb_url = "https://graph.facebook.com/v2.6/me/messages?access_token=%s"%PAGE_ACCESS_TOKEN
	global c

	if 'add' in payload:
		response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": 'Ok Give us an image' }})
		status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg)
		print status2.json()
		return HttpResponse()
	
	else:	
		c.save()
		response_msg = {
				"recipient":{
				    "id": fbid
				  },
				  "message":{
				    "attachment":{
				      "type":"file",
				      "payload":{
				        "url": 'https://pdfconv.herokuapp.com/chatbot/pdf'
				      }
				    }
				  }
		}
		response_msg = json.dumps(response_msg)
		status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg_quick)
		print status2.json()
		c=None
		return HttpResponse()

def quick_response(fbid):
	post_fb_url='https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg_quick = {
				"recipient":{
				    "id":fbid
				  },
				  "message":{
				    "text":"Prepare PDF",
				    "quick_replies":[
				      {
				        "content_type":"text",
				        "title":"Add Image",
				        "payload":"add"
				      },
				      {
				        "content_type":"text",
				        "title":"Save and Exit",
				        "payload":"exit"
				      }
				    ]
				  }
	}
	response_msg_quick = json.dumps(response_msg_quick)
	status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg_quick)
	print status2.json()


def post_fb_msg(fbid,message,image=False):
	post_fb_url='https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	output_text = message
	print image
	global c

	if image:
		output_text = 'Image Url : \n' + message
		post_fb_url2 = "https://graph.facebook.com/me/messages?access_token=%s"%PAGE_ACCESS_TOKEN
		share_button = {
				"recipient":{
				    "id": fbid
				  },
				  "message":{
				    "attachment":{
				      "type":"template",
				      "payload":{
				        "template_type":"generic",
				        "elements":[
				          {
				            "title":"Image URL",
				            "buttons":[
				              {
				                "type":"element_share"
				              }              
				            ]
				          }
				        ]
				      }
				    }
				  }
		}
		response_msg = json.dumps(share_button)
		status1 = requests.post(post_fb_url2, headers={"Content-Type": "application/json"},data=response_msg)
		print status1.json()
		response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": output_text }})
		status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg)
		print status2.json()

		image = ImageReader(message)
		add(fbid, image)
		quick_response(fbid)

	else:
		response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text": 'Hi! You can create a pdf from your images.\nJust give us an image' }})
		status2 = requests.post(post_fb_url, headers={"Content-Type": "application/json"},data=response_msg)
		print status2.json()

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
					post_fb_msg(sender_id,message_text, False)
					return HttpResponse()
				except Exception as e:
					print e

				try:
					if 'attachments' in message['message']:
						url = message['message']['attachments'][0]['payload']['url']
						print 'Image URL=%s' %url
						post_fb_msg(sender_id, url, True)
					else:
						print logg(message['message'],'<>')
				except Exception as e:
					print e

		return HttpResponse()