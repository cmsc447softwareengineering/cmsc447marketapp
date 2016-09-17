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
