##---IMPORTS

from captcha.fields import ReCaptchaField as CaptchaField
from django import forms
from pinax.apps.account.forms import SignupForm

##---FORMS

class CaptchaMixin(forms.Form):
    captcha = CaptchaField()


class CaptchaSignupForm(SignupForm, CaptchaMixin):
    pass

##---MAIN

if __name__ == '__main__':
    pass
