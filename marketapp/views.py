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

#TODO admin system
# Make admin page for pulling listings
# Redirect to admin sign in if its not signed in
# Give owner of listing ability to pull posts
#TODO stored passwords salted
#TODO Start making frontend look good
# Get some CSS up

class HomePageView(View):

	def dispatch(self, request, *args, **kwargs):
		return redirect('/feed')

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
				if (u.checkUserExists()):
					if (u.checkPassword()):
						t = os.urandom(64)
						tok = t.encode('base-64')
						usersesh = userSession(umbc_id = request.POST['umbcid'], token = tok)
						result = usersesh.createEntry()
						if (result != 1):
							return HttpResponse("<html>Failed to create session %s</html>"% "Either User doesnt exsist or password is wrong")
						#Else success!
						request.session['token'] = tok
						request.session['id'] = u.umbc_id
						#return HttpResponse("<html><h1>%s</h1></html>" % str(request.session['token']))
						return redirect('/feed')
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
		#userse = userSession.objects.get(pk='aa12345')
		#return HttpResponse("<html>%s</html>" % userse.checkTime())
		#Get Content
		#TODO For special queries and filtering add specialized request here instead of grabbing all entries
		stuff = self.getAllContent()

		#Get session info
		try:
			u = userSession(umbc_id=request.session['id'], token=request.session['token'])
		except:
			#If no cookie present they're not logged in
			ns = render_to_string('a.html')
			return render(request, 'marketapp/feed.html', {'results': stuff, 'notsignedinchunk': ns})

		#Post request..adding content	
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

		#Check param to logout
		lo = request.GET.get('logout','')	
		if (lo == 'logout'):
			u.delete()

		#Logged in Get request
		if (u.checkLogin() == 1):
			addform = addGoodForm()
			si = render_to_string('signedin.html', {'form': addform}, request=request)
			return render(request, 'marketapp/feed.html', {'results': stuff, 'signedinchunk': si})
	
		#Has Cookie but not valid
		ns = render_to_string('a.html')
		return render(request, 'marketapp/feed.html', {'results': stuff,'notsignedinchunk': ns})#,'signinlink': mark_safe('<a href="login">login here</a>')})


#Buy Item page
class BuyView(View):
	def dispatch(self, request, *args, **kwargs):
		if (request.method == 'GET'):
			p = request.GET.get('item','')
			if ( p != ''):
				try:
					p = productModel.objects.get(pk=int(p))
				except:
					return HttpResponse("<html>Object doesnt exsist</html>")
			return render(request, 'marketapp/buyit.html', {'item': p})
		elif ( request.method == 'POST'):
			try:
				u = userSession(umbc_id=request.session['id'], token=request.session['token'])
				#Verify User is logged in when trying to buy
				if (u.checkLogin() != 1):
					return HttpResponse("<html>Please sign in!</html>")
			except:
				return HttpResponse("<html>Please sign in!</html>")
			p = request.POST['item']

			try:
				p = productModel.objects.get(pk=int(p))
			except:
				return HttpResponse("<html>Object doesnt exsist</html>")
			#Bought a service so dont remove from listing
			if p.goodorservice == False:
				return HttpResponse("<html>%s</html>" % "Successfully purchased service!")
			#Bought a Good so remove from listing
			else:
				p.delete()
				return HttpResponse("<html>%s</html>" % "Successfully purchased good!")
			
			return HttpResponse("<html>Something went wrong</html>")
			
class AdminView(View):

	def dispatch(self, request, *args, **kwargs):
		#try:
		#	a = adminSession(email=request.session['email'], token=request.session['token'])
		#	if (a.checkLogin() != 1):
				#form = AdminLoginform()
				#return render(request, 'marketapp/login.html', {'form' : form})
		#except:
		#	pass

		stuff = productModel.objects.all()
		return render(request, 'marketapp/admin.html', {'results': stuff})


			









