##---IMPORTS

from captcha.fields import CaptchaField
from django import forms
from account.forms import SignupForm

##---FORMS

class CaptchaMixin(forms.Form):
    captcha = CaptchaField()


class CaptchaSignupForm(SignupForm, CaptchaMixin):
    pass

##---MAIN

if __name__ == '__main__':
    pass
