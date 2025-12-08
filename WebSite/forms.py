from django import forms
from django.core.mail import send_mail

class contactForms(forms.Form):

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    countrycode = forms.CharField(max_length=10)
    