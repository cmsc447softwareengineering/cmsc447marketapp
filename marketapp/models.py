from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import datetime
import re
from datetime import timedelta
from django.utils import timezone

p = re.compile('[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9]')

###############################################################
class adminModel(models.Model):
	email = models.CharField(max_length=64)
	password = models.CharField(max_length=64)
	def createEntry(self):
		self.clean()
		existStatus= self.checkUserExists()
		idValid = self.checkIdisValid()
		if( not existStatus and idValid):
			self.verified = True
			self.save()
			return 1#UserCreated!
		else:
			return 0

	def checkUserExists(self):
		ErrorMsg = ""
		try:
			adminModel.objects.get(email = self.email)
		except ObjectDoesNotExist:
			return False #User doesnt exist 
		except:
			return True	
		#Otherwise useralready exsists
		return True

	def checkPassword(self):
		try:
			if( adminModel.objects.get(email = self.email).password == self.password):
				return True
			else:
				return False
		except:
			pass


	def __str__(self):
		return "Email: " + self.email + ' Password: ' + self.password 

###############################################################
class userModel(models.Model):
	name = models.CharField(max_length=64)
	password = models.CharField(max_length=64)
	email = models.CharField(max_length=64)
	umbc_id = models.CharField(max_length=7, primary_key=True)
	verified = models.BooleanField()
	#TODO implement rating
	#rating = models.IntegerField()
	
	def createEntry(self):
		self.clean()
		ErrorMsg = ''
		existStatus = self.checkUserExists()
		idValid = self.checkIdisValid()	#Behavior will be wipe the user exists error if id is invalid
													#Which is ok because not valid ID's should never exist 
		if( not existStatus and idValid):
			self.verified = True
			self.save()
			return 1#UserCreated!
		#else:
		#	return ErrorMsg	#UsernotCreated
		return 0
	#TODO implement
	def deleteEntry(self):
		pass
	
	#TODO Setup SMTP
	#TODO Setup secret code for user validation
	def verifyEmail(self):
		pass
		#send_mail(	'Verify email for Marketapp!',
		#			'1234567secretcode',
		#			'validate@fake.com',
		#			[self.email],
		#			fail_silently=False
		#		)
		
	#Verifies ID hasnt already been registered
	def checkUserExists(self):
		ErrorMsg = ""
		try:
			userModel.objects.get(umbc_id = self.umbc_id)
		except ObjectDoesNotExist:			
			return False #User doesnt exist 
		except:
			return True
		#Otherwise useralready exsists
		return True

	def checkIdisValid(self):
		ErrorMsg = ""
		s = str(self.umbc_id)
		s = s.upper()	
		if(None == re.match(p,s)):
			ErrorMsg += "The umbcID provided was not valid. "
			return False
		else:
			return True

	def checkPassword(self):
		try:
			if( userModel.objects.get(umbc_id = self.umbc_id).password == self.password):
				return True
			else:
				return False
		except:
			pass

	#this is like java's toString
	def __str__(self):
		return "Name: " + self.name + ' Password: ' + self.password  + \
				' Email: ' + self.email + ' UmbcID: ' + self.umbc_id + \
				' Verified: ' + str(self.verified)


###############################################################
class productModel(models.Model):
	title = models.CharField(max_length=64)
	goodorservice = models.BooleanField() # true for a good
	description = models.CharField(max_length=255)
	price = models.FloatField(max_length=64)
	owner = models.CharField(max_length=7)
	#picture = models.ImageField(upload_to=None)

	def createEntry(self):
		self.clean()
		self.save()
		return
	def getAll(self):
		return productModel.objects.all()

	#this is like java's toString
	def __str__(self):
		return 'Title: ' + str(self.title) + \
				' Good or Service: ' + str(self.goodorservice) + \
				' Price: ' + str(self.price) + \
				' Owner: ' + str(self.owner)

###############################################################
class userSession(models.Model):
	umbc_id = models.CharField(max_length=7, primary_key=True)
	token = models.CharField(max_length=64)
	created = models.DateTimeField(auto_now_add=True)

	def createEntry(self):
		self.clean()
		ErrorMsg = ''
		try:
			w = userSession.objects.get(umbc_id = self.umbc_id)
		except ObjectDoesNotExist as detail:
			ErrorMsg += str(detail)
			self.save()
			return 1
		except:
			ErrorMsg += "Different Error occured."
			return ErrorMsg
		#delete old entry overwrite with fresher session
		w.delete()
		self.save()
		return 1

	#Returns true for being logged in
	def checkTime(self):
		try:
			w = userSession.objects.get(umbc_id = self.umbc_id)
		except:
			return False
		if timezone.now() < w.created + timedelta(days=1):
			return True
		return False

	def checkLogin(self):
		try:
			w = userSession.objects.get(umbc_id = self.umbc_id)
		except ObjectDoesNotExist as detail:
			return "User is not signed in."
		except ValueError as detail:
			return "A Value error occured. %s" % detail			
		except:
			return "A different error occured."
		if (str(w.token) == str(self.token) and self.checkTime()):
			return 1
		return 0

	def logout(self):
		u = userSession().objects.get(pk=self.umbc_id)
		u.delete()

	def __str__(self):
		return "UmbcId: " + self.umbc_id + ' Token: ' + self.token + ' Time created: ' + str(self.created)
	
###############################################################
class adminSession(models.Model):
	email = models.CharField(max_length=64, primary_key=True)
	token = models.CharField(max_length=64)
	created = models.DateTimeField(auto_now_add=True)

	def createEntry(self):
		self.clean()
		try:
			w = adminSession.objects.get(email = self.email)
		except ObjectDoesNotExist as detail:
			ErrorMsg += str(detail)
			self.save()
			return 1
		except:
			ErrorMsg += "Different Error occured."
			return ErrorMsg
		#delete old entry overwrite with fresher session
		w.delete()
		self.save()
		return 1

	def checkTime(self):
		try:
			w = adminSession().objects.get(email = self.umbc_id)
		except:
			return False
		if timezone.now() < self.created + timedelta(minutes=15):
			return True
		return False

	def checkLogin(self):
		try:
			w = adminSession.objects.get(email= self.email)
		except ObjectDoesNotExist as detail:
			return "User is not signed in."
		except ValueError as detail:
			return "A Value error occured. %s" % detail			
		except:
			return "A different error occured."
		if (str(w.token) == str(self.token) and self.checkTime()):
			return 1
		return 0

	def __str__(self):
		return "Email: " + self.email + ' Token: ' + self.token + ' Time created: ' + str(self.created)




