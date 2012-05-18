from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

register = template.Library()


def metadata_tree(value, autoescape=None):
    """
    Recursively takes a self-nested list and returns an HTML unordered list --
    WITHOUT opening and closing <ul> tags.

    The list is assumed to be in the proper format. For example, if ``var``
    contains: ``[[1,'States'], [[3,'Kansas'], [[2,'Lawrence'], [12,'Topeka']], [8,'Illinois']]]``,
    then ``{{ var|unordered_list }}`` would return::

        <li id="1"><a href="#"><ins>&nbsp;</ins>States</a>
        <ul>
                <li id="3"><a href="#"><ins>&nbsp;</ins>Kansas</a>
                <ul>
                        <li id="2"><a href="#"><ins>&nbsp;</ins>Lawrence</a></li>
                        <li id="12"><a href="#"><ins>&nbsp;</ins>Topeka</a></li>
                </ul>
                </li>
                <li id="8"><a href="#"><ins>&nbsp;</ins>Illinois</a></li>
        </ul>
        </li>
    """
    if autoescape:
        from django.utils.html import conditional_escape
        escaper = conditional_escape
    else:
        escaper = lambda x: x
    def convert_old_style_list(list_):
        """
        Converts old style lists to the new easier to understand format.

        The old list format looked like:
            ['Item 1', [['Item 1.1', []], ['Item 1.2', []]]

        And it is converted to:
            ['Item 1', ['Item 1.1', 'Item 1.2]]
        """
        if not isinstance(list_, (tuple, list)) or len(list_) != 2:
            return list_, False
        first_item, second_item = list_
        if second_item == []:
            return [first_item], True
        old_style_list = True
        new_second_item = []
        for sublist in second_item:
            item, old_style_list = convert_old_style_list(sublist)
            if not old_style_list:
                break
            new_second_item.extend(item)
        if old_style_list:
            second_item = new_second_item
        return [first_item, second_item], old_style_list
    def _helper(list_, tabs=1):
        indent = u'\t' * tabs
        output = []
        flag = 0
        flag2 = 0

        if not isinstance(list_[0], (list, tuple)):
            output.append('%s<li id="%s"><a href="#"><ins>&nbsp;</ins>%s</a>' % (indent, list_[0], escaper(force_unicode(list_[1]))))
            flag2 = 1
            flag = 1
            i = 2
        else:
            i = 0
        list_length = len(list_)
        if flag2 and list_length > 2:
            output.append('<ul>')
        while i < list_length:
            flag2 = 2
            item = list_[i]
            sublist = ''
            sublist_item = None
            if len(item) > 2:
                sublist_item = item
            #if isinstance(title, (list, tuple)):
            #    #if not ((len(title) == 2) and not isinstance(title[0], (list, tuple)) and not isinstance(title[1], (list, tuple))):
            #    sublist_item = title
            #    title = ''
            #elif i < list_length - 1:
            #    next_item = list_[i+1]
            #    if next_item and isinstance(next_item, (list, tuple)):
            #        # The next item is a sub-list.
            #        sublist_item = next_item
            #        # We've processed the next item now too.
            #        i += 1
            if sublist_item:
                sublist = _helper(sublist_item, tabs+1)
                sublist = '\n%s\n%s' % (sublist, indent)
                output.append(sublist)
                flag = 0
            else:
                output.append('%s<li id="%s"><a href="#"><ins>&nbsp;</ins>%s</a></li>' % (indent, item[0], escaper(force_unicode(item[1]))))
                flag = 0
            i += 1
        if flag:
            output.append('</li>')
        if flag2 and list_length > 2: 
            output.append('%s</ul>%s</li>' % (indent, indent))
        return '\n'.join(output)
    value, converted = convert_old_style_list(value)
    a = 0
    o = []
    o.append('\n<ul>\n')
    while a < len(value):
        o.append(_helper(value[a]))
        a += 1
    o.append('\n</ul>\n')
    return mark_safe('\n'.join(o))

register.filter(metadata_tree)
