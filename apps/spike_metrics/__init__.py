"""package for the default metrics"""

##---IMPORTS

import pkgutil, os, new

__all__ = []
ALL = []

##---FUNCTIONS

def get_admin():
    """admin generator"""

    for loader, name, is_pkg in pkgutil.iter_modules(path=[os.path.dirname(__file__)]):
        pass
    return pkgutil.iter_modules(path=[os.path.dirname(__file__)])

##---TIDY-UP

del new

##---MAIN

if __name__ == '__main__':
    pass
