from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

def add(image,c):
	c.drawImage(image, 0,0, width=600,height=800,mask='auto')
	c.showPage()

c=Canvas('file.pdf')
while True:
	url = raw_input()
	# 'https://i.ytimg.com/vi/GD5ozrtGCyk/maxresdefault.jpg'
	if url == '':
		break
	image = ImageReader(url)
	add(image,c)

c.save()