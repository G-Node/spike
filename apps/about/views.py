##---IMPORTS

from django.views.generic import TemplateView

##---CLASSES

class HomepageView(TemplateView):
    template_name = 'homepage.html'

class ImprintView(TemplateView):
    template_name = 'about/imprint.html'


class TeamView(TemplateView):
    template_name = 'about/team.html'

##---MAIN

if __name__ == '__main__':
    pass
