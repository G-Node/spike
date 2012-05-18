from django import forms
from spike_evaluation.evaldocs.models import Topic, Article, Section

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title', 'sort')

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'sort')

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ('title', 'sort', 'content')
