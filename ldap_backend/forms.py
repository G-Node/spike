from django_ldapbackend import LDAPBackend, getLDAPGroup
from django.contrib.auth.models import Group
from django.conf import settings
from django import forms

LDAPGROUP = getattr(settings, 'AUTH_LDAP_GROUP_NAME', 'ldap_users')

class PasswordChangeForm(forms.Form):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """

    old_password = forms.CharField(label=("Old password"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        g = self.user.groups.all()
        checkGroup = getLDAPGroup(LDAPGROUP)
        self.l = LDAPBackend()
        try:
            ldapGroup = Group.objects.get(name=LDAPGROUP)
            if(ldapGroup in g):
                self.ldapuser = True
            else:
                self.ldapuser = False
        except:
            self.ldapuser = False


    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if(self.ldapuser == False):
            if not self.user.check_password(old_password):
                raise forms.ValidationError(("Your old password was entered incorrectly. Please enter it again."))
            return old_password
        else:
            if not self.l.checkPassword(self.user.username,old_password):
                raise forms.ValidationError(("Your old LDAP password was entered incorrectly. Please enter it again."))
            return old_password
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if(self.ldapuser == False):
            if commit:
                self.user.save()
                return self.user
        else:
            change = self.l.changePassword(self.user.username, self.cleaned_data['old_password'], self.cleaned_data['new_password1'])
            if(change == True):
                return self.user
            else:
                raise 'LDAP Error: consult your server'
                

PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

