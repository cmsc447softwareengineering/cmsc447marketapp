from django import forms

class SignUpForm(forms.Form):
	name = forms.CharField(label='your name', max_length=64)
	password = forms.CharField(label='password',widget=forms.PasswordInput(), max_length=64)
	repassword = forms.CharField(label='retypepassword',widget=forms.PasswordInput(), max_length=64)
	email = forms.CharField(label='email', max_length=64)
	umbcid = forms.CharField(label='umbcid', max_length=7)

class LoginForm(forms.Form):
	umbcid = forms.CharField(label='umbcid', max_length=7)
	password = forms.CharField(label='password',widget=forms.PasswordInput(), max_length=64)

class addGoodForm(forms.Form):
	title = forms.CharField(label='Title', max_length=64)
	goodorservice = forms.BooleanField(required=False) # true for a good
	description = forms.CharField(label='description', max_length=255)
	price = forms.FloatField(label='price')
	#owner = forms.CharField(label='', max_length=7)
