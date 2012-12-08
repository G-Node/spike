##---IMPORTS

from captcha import fields
from captcha.fields import ReCaptchaField

##---DECORATORS

def form_with_captcha(orig_form):
    if hasattr(orig_form, 'captcha'):
        raise ValueError('form already has a field captcha!')
    orig_form.__orig__init__ = orig_form.__init__

    def new_init(self, *args, **kwargs):
        self.__orig__init__(*args, **kwargs)
        self.fields['captcha'] = self.captcha

    orig_form.__init__ = new_init
    orig_form.captcha = ReCaptchaField(attrs={'theme': 'white'})
    return orig_form

##---MAIN

if __name__ == '__main__':
    pass
