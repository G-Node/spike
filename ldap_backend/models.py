from django.contrib.auth.models import User, Group
from django.db import models
from django.conf import settings
import django.dispatch
import ldap
import ldap.modlist as modlist
from emailconfirmation.models import EmailAddress

import logging

""" Signals, to make magic easier """
new_ldap_user = django.dispatch.Signal(providing_args=['user','email'])
auth_ldap_user = django.dispatch.Signal(providing_args=['user'])

""" Create/edit/manage an LDAP group - should be moved (inline, away?) """
def getLDAPGroup(ldapGroup):
    groupName = ldapGroup
    try:
        g = Group.objects.get(name=groupName)
    except:
        g = Group(name=groupName)
        g.save()
    return g

""" The backend """
class LDAPBackend:
    """ Set Defaults and Connect - use the config file"""
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def __init__(self):
        """ Set blank username and password as we are not managing them yet """
        self.username = None
        self.password = None

        """ Carry over the information we need, then start """
        self.base_username = getattr(settings, 'AUTH_LDAP_BASE_USER', 'admin')
        self.base_password = getattr(settings, 'AUTH_LDAP_BASE_PASS', 'secret')
        self.ldap_address = getattr(settings, 'AUTH_LDAP_SERVER', '127.0.0.1')
        self.django_group = getattr(settings, 'AUTH_LDAP_GROUP_NAME', 'ldap_users')
        self.base_dn = getattr(settings, 'AUTH_LDAP_BASE_DN', 'dc=example,dc=com')
        self.domain_name = getattr(settings, 'AUTH_LDAP_FIELD_DOMAIN', 'example.com')
        self.username_field = getattr(settings, 'AUTH_LDAP_FIELD_USERNAME', 'uid')
        self.auth_field = getattr(settings, 'AUTH_LDAP_FIELD_USERAUTH', 'uid')
        self.auth_group = getattr(settings, 'AUTH_LDAP_FIELD_AUTHUNIT', 'People')
        self.oldpw = getattr(settings, 'AUTH_LDAP_OLDPW', False)
        self.mailDirectory = getattr(settings, 'AUTH_LDAP_WITHDRAW_EMAIL', True)
        VERSION = getattr(settings, 'AUTH_LDAP_VERSION', 3)
        if(VERSION == 2):
            self.protocol_version = ldap.VERSION2
        elif(VERSION == 3):
            self.protocol_version = ldap.VERSION3
        ldapGroup = getLDAPGroup(self.django_group)


    """ Two different connection types are used, and passed on the fly, then destroyed on
        use to minimise administrative use.  This gives two levels of authentication,
        and two binds in some instances.  Notably simple_bind is used at the moment
        because there is no other method available. """

    """ For user connections. """
    def connection(self):
        try:
            l = ldap.open(self.ldap_address)
            l.protocol_version = self.protocol_version
            l.simple_bind_s(self.username,self.password)
            return l
        except ldap.INVALID_CREDENTIALS, e:
            return None

    """ For super user (admin) actions """
    def sudo(self):
        try:
            l = ldap.open(self.ldap_address)
            l.protocol_version = self.protocol_version
            l.simple_bind(self.base_username,self.base_password)
            return l
        except ldap.INVALID_CREDENTIALS, e:
            return None

    """ Use sudo to pull run a filter, return results.  Default is 'dn' if not set. """
    def getUser(self, username=None, find=['dn']):
        try:
            su = self.sudo()
            auth_filter = "(%s=%s)" % (self.username_field,username)
            type, data = su.result(su.search(self.base_dn, ldap.SCOPE_SUBTREE, auth_filter, find), 0)
            su.unbind_s()
            return data
        except:
            return None

    """ Like a lot of others, except we're using an inbuilt functions for separation. 
        This is also required to force case sensitivity (read: if we use the 'root' or 'admin'
        user to pull the username, then force an auth through another method to ensure you
        are the correct user, we have a record of the case used.  This means we can ignore
        the case elsewhere and Django will block duplication of user objects based on
        case insensitivity, even though LDAP's uid doesn't care.  Elsewhere this script
        utilises self.username_field for auth. """
    def authenticate(self, username=None, password=None, create=True):
        find = ['dn',self.username_field]
        if(self.mailDirectory == True): find.append('mail')
        data = self.getUser(username, find)
        if (len(data) != 1):
            return None

        """ set the username/password by dn (so it's compatible no matter what),
            the test the connection with the user/pass.  If they have access,
            set the username field we're carrying (e.g. mail, uid, etc.),
            and try to setup a new user or return an existing one """
        self.username = data[0][0]
        self.password = password
        username = data[0][1][self.username_field][0]

        """ Set the e-mail if the directory holds it, otherwise fake it. """
        # currently works wrong!! TODO
        if(self.mailDirectory == True and 'mail' in list(data[0][1].keys())):
            email = data[0][1]['mail'][0]
        else:
            email = "%s@%s" % (username, self.domain_name)

	#LOG_FILENAME = '/home/sobolev/media/logs/test.txt'
	#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
        #logging.debug('%s', data)

        connection = self.connection()
        if connection is None:
            return None
        else:
            try:
                user = User.objects.get(username__exact=username)
                user.email = email
                user.save()
                if not EmailAddress.objects.filter(user=user, email=email, verified=True, primary=True):
                    EmailAddress(user=user, email=email, verified=True, primary=True).save()
            except Exception, e:
                if(create == True):
                    user = User.objects.create_user(username, email)
                    new_ldap_user.send(sender=self, user=user, email=email)
                    user.is_staff = False
                    user.groups.add(Group.objects.get(name=self.django_group))
                    user.save()
                    EmailAddress(user=user, email=email, verified=True, primary=True).save()
            auth_ldap_user.send(sender=self, user=user)
            connection.unbind_s()
            return user

    """ We are using the models storage, so this shall remain unchanged """
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist, e:
            return None

    def checkPassword(self, username=None, password=None):
        data = self.getUser(username)
        self.username = data[0][0]
        self.password = password
        c = self.connection()
        if(c is None):
            return False
        c.unbind_s()
        return True

    """ Change Password! """
    def changePassword(self, username=None, oldpassword=None, newpassword=None):
        """ TODO: Use getUser to get the user ... use user to login,
            if it works, change password, filter by oldpw """
        try:
            data = self.getUser(username)
            self.username = data[0][0]
            self.password = oldpassword
            c = self.connection()
            if(c is None):
                return False
            if(self.oldpw == False): self.password = None
            # another way to modify password. if passwd_s() doesn't work
            #old = {'userPassword':self.password}
            #new = {'userPassword':newpassword}
            #ldif = modlist.modifyModlist(old,new)
            #c.modify_s(dn,ldif)
            c.passwd_s(self.username, self.password, newpassword)
            c.unbind_s()
            return True
        except ldap.LDAPError, e:
            return e
        except ldap.INVALID_CREDENTIALS, e:
            return e

    """ Reset Password! """
    def resetPassword(self, username=None, newpassword=None):
        """ TODO: Use getUser to get the user ... use user to login,
            if it works, change password, filter by oldpw """
        try:
            data = self.getUser(username)
            usr_to_change = data[0][0]
            self.username = getattr(settings, 'AUTH_LDAP_BASE_USER')
            self.password = getattr(settings, 'AUTH_LDAP_BASE_PASS')
            c = self.connection()
            if(c is None):
                return False
            if(self.oldpw == False): self.password = None
            # another way to modify password. if passwd_s() doesn't work
            #old = {'userPassword':self.password}
            #new = {'userPassword':newpassword}
            #ldif = modlist.modifyModlist(old,new)
            #c.modify_s(dn,ldif)
            c.passwd_s(usr_to_change, None, newpassword)
            c.unbind_s()
            return True
        except ldap.LDAPError, e:
            return e
        except ldap.INVALID_CREDENTIALS, e:
            return e


    """ currently not used """
    def addUser(self, username=None, oldpassword=None, newpassword=None):

	dn=getattr(settings, 'AUTH_LDAP_FIELD_USERNAME', 'uid') + "=" + username + ",ou="
	dn+=getattr(settings, 'AUTH_LDAP_FIELD_AUTHUNIT', 'People') + ","
	dn+=getattr(settings, 'AUTH_LDAP_BASE_DN', 'o=g-node.org,o=g-node')

	attrs = {}
	attrs['objectclass'] = ['top','organizationalRole','simpleSecurityObject']
	attrs['cn'] = username
	attrs['sn'] = username
	attrs['uid'] = username
	attrs['userPassword'] = password
	attrs['gidNumber'] = '2000'
	attrs['uidNumber'] = '2014'
	attrs['homeDirectory'] = '/home/' + username
	try:
            c = self.connection(self.base_username, self.base_password)
            if(c is None):
                return False
	    ldif = modlist.addModlist(attrs)
	    c.add_s(dn,ldif)
	    c.unbind_s()
        except ldap.LDAPError, e:
            return False
        except ldap.INVALID_CREDENTIALS, e:
            return False

