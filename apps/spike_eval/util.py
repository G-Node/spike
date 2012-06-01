##---IMPORTS

from django.shortcuts import render_to_response
from django.template import RequestContext

##---CHOICES

ACCESS_CHOICES = [
    (10, 'PRIVATE'),
    (20, 'PUBLIC'),
]

FILETYPE_CHOICES = [
    (10, 'Rawdata File'),
    (20, 'Groundtruth File'),
    (30, 'Evaluation File'),
    (40, 'Supplementary File'),
]

TASK_STATE_CHOICES = [
    (10, 'Running'),
    (20, 'Success'),
    (30, 'Failure'),
]

##---DECORATORS

def render_to(template_name):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(
                template_name,
                output,
                context_instance=RequestContext(request))

        return wrapper

    return renderer

##---MAIN

if __name__ == '__main__':
    pass
