from django import forms

class WebsiteForm(forms.Form):
    post = forms.CharField()