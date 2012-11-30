__author__ = 'pmeier'

from account import signals

def test_login(sender, **kwargs):
    print sender
    print kwargs

signals.user_login_attempt.connect(test_login)
