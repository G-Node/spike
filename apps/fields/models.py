from django import forms
from django.forms.util import ValidationError, ErrorList, flatatt
from django.forms.widgets import Select, SelectMultiple, HiddenInput, MultipleHiddenInput
from django.db import models
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.utils.html import escape, conditional_escape
from django.contrib.auth.models import User

from itertools import chain
import settings
from neo_api.meta import meta_unit_types

class UnitField(models.CharField):
    """
    This field is going to store a unit of any measure.
    """
    __metaclass__ = models.SubfieldBase
    _unit_type = None

    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(UnitField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super(UnitField, self).validate(value, model_instance)
        if self._unit_type and (not value.lower() in meta_unit_types[self._unit_type]):
            raise forms.ValidationError("Unit provided is not supported: %s. \
The following units are supported: %s." % (value, meta_unit_types))

class TimeUnitField(UnitField):
    """
    This field should store time units.
    """
    def __init__(self, *args, **kwargs):
        super(TimeUnitField, self).__init__(*args, **kwargs)
        self._unit_type = 'time'
    
class SignalUnitField(UnitField):
    """
    This field stores signal units.
    """
    def __init__(self, *args, **kwargs):
        super(SignalUnitField, self).__init__(*args, **kwargs)
        self._unit_type = 'signal'

class SamplingUnitField(UnitField):
    """
    This field stores sampling rate units.
    """
    def __init__(self, *args, **kwargs):
        super(SamplingUnitField, self).__init__(*args, **kwargs)
        self._unit_type = 'sampling'


class AutoSelectMultiple(SelectMultiple):
    """ A widget which uses jQuery autocomplete to search and select across 
    multiple values. """
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [(u'<input type="text" id="lookup_%s" />' % name)]
        output.append(u'''<script type="text/javascript">
            $(function() {
                var availableTags = %(tags)s;
                var tag_list = [];
                for (i=0; i<availableTags.length; i++) {
                    var option = new Object();
                    option.value = availableTags[i][0];
                    option.label = availableTags[i][1];
                    tag_list[i] = option;
                };
    	        $("#lookup_%(name)s").autocomplete({
                    source: tag_list,
                    select: function( event, ui ) {
                        $('#select_%(name)s option[value=' + ui.item.value + ']').attr('selected','selected');
                        var b1 = !($('#list_%(name)s li[id=' + ui.item.value + ']').length > 0)
                        if (!($('#list_%(name)s li[id=' + ui.item.value + ']').length > 0)) {
                            $('#list_%(name)s').append('<li id="' + ui.item.value + '"><div class="object_repr">' + ui.item.label + '</div><div class="delete_from_m2m"><a style="cursor:pointer" onClick="autocompleteRemoveItem(' + ui.item.value + ')"><img src="%(static_url)spinax/images/img/icon_deletelink.gif" /></a></div></li>');
                        };
                        $('#lookup_%(name)s').val('');
                        $('#lookup_%(name)s').focus();
                        return false;
                    }
    	        });
            });
            </script>''' % {
                'tags': [[int(option[0]), str(option[1])] for option in chain(self.choices)],
                'name': name,
                'static_url': settings.STATIC_URL})
        output.append(u'''<script type="text/javascript">
            //$('.delete_from_m2m').click(function() {
            function autocompleteRemoveItem (rm_pk) {
                //var rm_pk = $(this).parent().attr("id")
                $('#list_%(name)s li[id=' + rm_pk + ']').remove();
                $('#select_%(name)s option[value=' + rm_pk + ']').removeAttr('selected');
            };
            function autocompleteRemoveAll() {
                $('#select_%(name)s :selected').removeAttr('selected');
                $('#list_%(name)s li').remove();
            }
            </script>''' % {'name': name})
        output.append(u'<select id="select_%s" multiple="multiple" style="display:none;"%s>' % (name, flatatt(final_attrs)))
        options = self.render_options(choices, value)
        if options: 
            output.append(options)
        output.append('</select>')
        output.append('<div class="autocomplete_label">Selected:</div>')
        """ This renders a list of selected options as a <ul><li></li></ul> """
        output.append(u'<div class="autocomplete"><ul id="list_%s">' % name)
        selected = self.render_selected(choices, value)
        if selected:
            output.append(selected)
        output.append('</ul></div>')
        return mark_safe(u'\n'.join(output))

    def render_selected(self, choices, selected_choices):
        choice_ids = [str(c) for c in selected_choices]
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        ch = [c for c in self.choices]
        for option_value, option_label in chain(self.choices, choices):
            if str(option_value) in choice_ids:
                if isinstance(option_label, (list, tuple)):
                    output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                    for option in option_label:
                        output.append(self.render_item(selected_choices, *option))
                    output.append(u'</optgroup>')
                else:
                    output.append(self.render_item(selected_choices, option_value, option_label))
        return u'\n'.join(output)

    def render_item(self, selected_choices, option_value, option_label):
        output = []
        option_value = force_unicode(option_value)
        output.append(u'<li id="%s"><div class="object_repr">%s</div>' % (escape(option_value),
            conditional_escape(force_unicode(option_label))))
        output.append(u'''<div class='delete_from_m2m'>
            <a style='cursor:pointer' onClick='autocompleteRemoveItem(%s)'>
                <img src='%spinax/images/img/icon_deletelink.gif' />
            </a>
            </div></li>''' % (escape(option_value), settings.STATIC_URL))
        return u'\n'.join(output)


# A ModelMultipleChoiceField with "Clear" helptext.
# Require a javascript code to be inserted to perform clear of selection.
	
class MMCFClearField(forms.ModelChoiceField):
    """A MultipleChoiceField whose choices are a model QuerySet."""
    widget = AutoSelectMultiple #SelectMultiple
    hidden_widget = MultipleHiddenInput
    default_error_messages = {
        'list': _(u'Enter a list of values.'),
        'invalid_choice': _(u'Select a valid choice. %s is not one of the'
                            u' available choices.'),
        'invalid_pk_value': _(u'"%s" is not a valid value for a primary key.')
    }

    def __init__(self, queryset, cache_choices=False, required=False,
                 widget=None, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        super(MMCFClearField, self).__init__(queryset, None,
            cache_choices, required, widget, label, initial, help_text,
            *args, **kwargs)
        # this string makes the only difference from 'ModelMultipleChoiceField'
        self.help_text = self.help_text + 'Select people by typing a few letters in the box above. To remove all people from sharing push <span id="clear_selection"><b onClick="autocompleteRemoveAll()">remove all</b></span>.'

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
        for pk in value:
            try:
                self.queryset.filter(pk=pk)
            except ValueError:
                raise ValidationError(self.error_messages['invalid_pk_value'] % pk)
        qs = self.queryset.filter(pk__in=value)
        pks = set([force_unicode(o.pk) for o in qs])
        for val in value:
            if force_unicode(val) not in pks:
                raise ValidationError(self.error_messages['invalid_choice'] % val)
        return qs





# THE FOLLOWING IS LEGACY PLEASE DELETE
"""

class ManyToManySearchInput(SelectMultiple):
    class Media:
		css = {
			'all': ('%s/css/jquery.autocomplete.css' % settings.STATIC_URL,)
		}
		js = (
			'%s/js/jquery.js' % settings.STATIC_URL,
			'%s/js/jquery.autocomplete.js' % settings.STATIC_URL,
			'%s/js/autocomplete/AutocompleteObjectLookups.js' % settings.STATIC_URL,
            '%s/js/jquery.bgiframe.min.js' % settings.STATIC_URL,
            '%s/js/jquery.ajaxQueue.js' % settings.STATIC_URL,
		)

    def label_for_value(self, value=None):
        return ''

    def __init__(self, rel, search_fields, attrs=None):
        self.rel = rel
        self.search_fields = search_fields
        super(ManyToManySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        ul=""
        select=''
        ToModel=self.rel
        if not value:value=[]
        for val in value:
            obj=ToModel.objects.get(pk=val)
            ul+="<li id='%(pk)s'><div class='object_repr'>%(repr)s</div><div class='delete_from_m2m'><a style='cursor:pointer'><img src='%(static_url)spinax/images/img/icon_deletelink.gif' /></a></div></li>"%{'static_url': settings.STATIC_URL,
                        'repr':obj.__unicode__(), 
                        'pk':str(obj.pk)}
            select+='<option id="%(pk)s" value="%(pk)s" selected="selected">%(repr)s</option>'%{'static_url': settings.STATIC_URL,
                        'repr':obj.__unicode__(), 
                        'pk':str(obj.pk)}
        return mark_safe(u'''<style type="text/css" media="screen">
                #lookup_%(name)s {
                    padding-right:16px;
                    width:150px;
                    background: url(
                        %(static_url)spinax/images/img/selector-search.gif
                    ) no-repeat right;
                }
                #del_%(name)s {
                    display: none;
                }
                #list_%(name)s{
                margin-left:5px;
                list-style-type:none
                padding:0;
                margin:0;
                margin-left:75px;
                
                }
                #list_%(name)s li{
                list-style-type:none;
                
                margin:0px;
                padding:0px;
                margin-top:5px;
                }
                .object_repr{
                                float:left;
                                padding-left:2px;
                                border:1px solid #CCCCCC;
                                width:200px;
                                color:#333333;
                                background-color:#EFEFEF;
                                }
                .delete_from_m2m{float:left}
            </style>

            <select multiple="multiple" name="%(name)s" id="id_%(name)s" style="display:none;">
                %(select)s
            </select>

            <input type="text" id="lookup_%(name)s" value="%(label)s" />
            <a href="../../../%(app_label)s/%(model_name)s/add/" class="add-another" id="add_id_%(name)s" onclick="return showAddAnotherPopup(this);"> 
                <img src="%(static_url)spinax/images/img/icon_addlink.gif" width="10" height="10" alt="Add user"/>
            </a>
            <br/>
            <br/>

            <ul id="list_%(name)s"><b>added objects:</b>
                %(ul)s
            </ul>
            <br/>
            <br/>

<script type="text/javascript">
            $(document).ready(function() {
            $('#id_%(name)s').parent().children().filter('.add-another:last').hide();

            //$('#add_id_%(name)s').hide();
            $('.delete_from_m2m').click(function(){
            var rm_li=$(this).parent();
            var rm_pk=$(rm_li).attr("id");
            $('ul#list_%(name)s li#'+rm_pk+':first').remove()
            $('#id_%(name)s #'+rm_pk+':first').remove()
            });
        });
            $('#lookup_%(name)s').keydown( function(){$('#busy_%(name)s').show();});
            
            $('#lookup_%(name)s')
            var event=$('#lookup_%(name)s').autocomplete('../search/', {
                extraParams: {
                    search_fields: '%(search_fields)s',
                    app_label: '%(app_label)s',
                    model_name: '%(model_name)s',
                }
            });
            event.result(function(event, data, formatted) {
                $('#busy_%(name)s').hide();
                if (data) {
                    var elem=$('#list_%(name)s li#'+data[1])
                    
                    if (!elem.attr("id")){
                    $('#list_%(name)s').html($('#list_%(name)s').html()+'<li id="'+data[1]+'"><div class="object_repr">'+data[0]+'</div><div class="delete_from_m2m"><a style="cursor:pointer"><img src="%(static_url)simg/admin/icon_deletelink.gif" /></a></div></li>');
                    $('#lookup_%(name)s').val('');
                    $('#id_%(name)s').html($('#id_%(name)s').html()+'<option id="'+data[1]+'" value="' +data[1] + '" selected="selected">' +data[0] +'</option>');
            $('.delete_from_m2m').click(function(){
            var rm_li=$(this).parent();
            var rm_pk=$(rm_li).attr("id");
            $('ul#list_%(name)s li#'+rm_pk+':first').remove()
            $('#id_%(name)s #'+rm_pk+':first').remove()
            });
                    }
                }
            });
            
</script>
        ''' % {
            'search_fields': ','.join(self.search_fields),
            'static_url': settings.STATIC_URL,
            'model_name': self.rel._meta.module_name,
            'app_label': self.rel._meta.app_label,
            'label': label,
            'name': name,
            'ul':ul, 
            'select':select, 
        })
"""


