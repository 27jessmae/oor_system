from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to the form field."""
    return field.as_widget(attrs={
        "class": css_class
    })

@register.filter(name='add_placeholder')
def add_placeholder(field, placeholder_text):
    """Add a placeholder to the form field."""
    return field.as_widget(attrs={
        "placeholder": placeholder_text
    })

@register.filter(name='add_attrs')
def add_attrs(field, attrs):
    """Add multiple attributes to the form field.
    
    Usage: {{ field|add_attrs:"placeholder:Enter text,class:form-control" }}
    """
    attrs_dict = {}
    attrs_list = attrs.split(',')
    
    for attr in attrs_list:
        if ':' in attr:
            key, value = attr.split(':', 1)
            attrs_dict[key.strip()] = value.strip()
    
    return field.as_widget(attrs=attrs_dict)
