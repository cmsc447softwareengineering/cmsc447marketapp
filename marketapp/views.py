import textwrap
import random
import os
import datetime

from django.http import HttpResponse
from django.views.generic.base import View
from .forms import SignUpForm
from .forms import LoginForm
from .forms import addGoodForm
from django.shortcuts import render
from django.shortcuts import redirect
from models import userModel
from models import userSession
from models import productModel
from django.core.mail import send_mail
from django.utils.html import mark_safe
from django.template.loader import render_to_string
#from django.core.exceptions import MultiValueDictKeyError

class HomePageView(View):

	def dispatch(self, request, *args, **kwargs):
		return redirect('/djangotest/feed')
		response_text = textwrap.dedent('''\
            <html>
            <head>
                <title>Greetings to the world</title>
            </head>
            <body>
                <h1>Greetings to the world</h1>
                <p>Hello, world!</p>
            </body>
			<h1>%s</h1>
			</html>
		''')
		return HttpResponse(response_text)

class CreateUserView(View):

	def dispatch(self, request, *args, **kwargs):

		if (request.method == 'POST'):
			form = SignUpForm(request.POST)
			if (form.is_valid()):
				u = userModel(	name = request.POST['name'], 
								password = request.POST['password'],
								email = request.POST['email'],
								umbc_id = request.POST['umbcid'])
				result = u.createEntry() 
				if( result == 1):# 1 means user was created
					u.verifyEmail()
				else:
					return HttpResponse("Failed to Create user because %s" % str(result))
				#Success!
				return HttpResponse("It worked posted %s " % request.POST)
			else:
				return HttpResponse("It didnt work")
		else:
			form = SignUpForm()
		return render(request, 'marketapp/createuser.html', {'form':form})

class LoginView(View):
	def dispatch(self, request, *args, **kwargs):
		if (request.method == 'POST'):
			form = LoginForm(request.POST)
			if (form.is_valid()):
				u = userModel(	umbc_id = request.POST['umbcid'],
								password = request.POST['password'])
				if (u.checkUserExists()[0]):
					if (u.checkPassword()):
						t = os.urandom(64)
						tok = t.encode('base-64')
						usersesh = userSession(umbc_id = request.POST['umbcid'], token = tok)
						result = usersesh.createEntry()
						if (result != 1):
							return HttpResponse("<html>Failed to create session %s</html>"% result)
						#Else success!
						request.session['token'] = tok
						request.session['id'] = u.umbc_id
						#return HttpResponse("<html><h1>%s</h1></html>" % str(request.session['token']))
						return redirect('/djangotest/feed')
					#wrong password					
					else:
						return HttpResponse("<html><h1>Wrong password try again</h1></html>")
				#wrong username
				else:
					return HttpResponse("<html><h1>Wrong User Name</h1></html>")
		#Its a Get request			
		else:
			form = LoginForm()
		return render(request, 'marketapp/login.html', {'form':form})

class MainFeedView(View):
	#for debug purpose shold be in models.py
	def getAllContent(self):
		stuff = productModel.objects.all()

		return stuff
	
	def dispatch(self, request, *args, **kwargs):
		#Get Content
		stuff = self.getAllContent()

		#Get session info
		try:
			u = userSession(umbc_id=request.session['id'], token=request.session['token'])
		except:
			#If no cookie present they're not logged in
			ns = render_to_string('a.html')
			return render(request, 'marketapp/feed.html', {'results': stuff, 'notsignedinchunk': ns})#,'signinlink': mark_safe('<a href="login">login here</a>')})
		
		#adding content	
		if (request.method == 'POST'):
			if (u.checkLogin() == 1):
				goodform = addGoodForm(request.POST)
				#TODO Django's checkbox is stupid sets 'on' for True and throws errors on False 
				try:
					g = request.POST['goodorservice']
				except:
					g = False
				if g == 'on':
					g = True
				#invalid data sent
				else:
					g = False
				if (goodform.is_valid()):
					pm = productModel(title=request.POST['title'],  goodorservice=g, description=request.POST['description'], price=request.POST['price'], owner=request.session['id'])
					pm.createEntry()
					stuff = self.getAllContent() #update newly added thing
		
			addform = addGoodForm()
			si = render_to_string('signedin.html', {'form': addform}, request=request)
			return render(request, 'marketapp/feed.html', {'results': stuff, 'signedinchunk': si})		

		#Logged in Get request
		if (u.checkLogin() == 1):
			addform = addGoodForm()
			si = render_to_string('signedin.html', {'form': addform}, request=request)
			return render(request, 'marketapp/feed.html', {'results': stuff, 'signedinchunk': si})
	
		#Has Cookie but not valid
		ns = render_to_string('a.html')
		return render(request, 'marketapp/feed.html', {'results': stuff,'notsignedinchunk': ns})#,'signinlink': mark_safe('<a href="login">login here</a>')})



			









