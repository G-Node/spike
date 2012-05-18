from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

#from blog.models import Post
#from photos.models import Image
#from bookmarks.models import BookmarkInstance
# from tribes.models import Tribe
# from tribes.models import Topic as TribeTopic


from tagging.models import Tag, TaggedItem

from experiments.models import Experiment
from datasets.models import RDataset
from datafiles.models import Datafile
from wiki.models import Article as WikiArticle

@login_required
def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
   
    #alltags = TaggedItem.objects.get_by_model(Post, tag).filter(status=2)
    #phototags = TaggedItem.objects.get_by_model(Image, tag)
    #bookmarktags = TaggedItem.objects.get_by_model(BookmarkInstance, tag)
    # tribe_tags = TaggedItem.objects.get_by_model(Tribe, tag).filter(deleted=False)
    # tribe_topic_tags = TaggedItem.objects.get_by_model(TribeTopic, tag).filter(tribe__deleted=False)

    wiki_article_tags = TaggedItem.objects.get_by_model(WikiArticle, tag)

    experiment_tags = TaggedItem.objects.get_by_model(Experiment, tag).filter(current_state=10)
    experiment_tags = filter(lambda x: x.is_accessible(request.user), experiment_tags)

    dataset_tags = TaggedItem.objects.get_by_model(RDataset, tag).filter(current_state=10)
    dataset_tags = filter(lambda x: x.is_accessible(request.user), dataset_tags)

    datafile_tags = TaggedItem.objects.get_by_model(Datafile, tag).filter(current_state=10)
    datafile_tags = filter(lambda x: x.is_accessible(request.user), datafile_tags)

    return render_to_response(template_name, {
        'tag': tag,
        'experiment_tags': experiment_tags,
        'dataset_tags': dataset_tags,
        'datafile_tags': datafile_tags,
	'wiki_article_tags': wiki_article_tags,
    }, context_instance=RequestContext(request))
