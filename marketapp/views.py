import textwrap
import random
import datetime

from django.http import HttpResponse
from django.views.generic.base import View
from .forms import SignUpForm
from .forms import LoginForm
from django.shortcuts import render
from django.shortcuts import redirect
from models import userModel
from models import userSession
from django.core.mail import send_mail

class HomePageView(View):

	def dispatch(self, request, *args, **kwargs):
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
						#TODO this sucks hashes same random thing
						random.seed(request.POST['password'])
						tok = random.randint(1,9999999999)
						#########################################
						usersesh = userSession(umbc_id = request.POST['umbcid'], token = tok)
						result = usersesh.createEntry()
						if (result != 1):
							return HttpResponse("<html>Failed to create session %s</html>"% result)
						request.session['token'] = tok
						request.session['id'] = u.umbc_id
						return HttpResponse("<html><h1>%s</h1></html>" % str(request.session['token']))
						#return redirect('/djangotest/feed')
					#wrong password					
					else:
						return HttpResponse("<html><h1>Wrong password try again</h1></html>")
				#wrong username
				else:
					return HttpResponse("<html><h1>Wrong User Name</h1></html>")
					
		else:
			form = LoginForm()
		return render(request, 'marketapp/login.html', {'form':form})

class MainFeedView(View):
	
	def dispatch(self, request, *args, **kwargs):
		try:
			u = userSession(umbc_id=request.session['id'], token=request.session['token'])
		except:
			return HttpResponse("<html>User not logged in</html>")
			
		if (u.checkLogin() == 1):
			return HttpResponse("<html>User logged in: </html>")
		return HttpResponse("<html>User not logged in</html>")

		return render(request, 'marketapp/feed.html')












