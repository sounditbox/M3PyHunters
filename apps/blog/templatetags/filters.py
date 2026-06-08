from datetime import datetime

from django import template

register = template.Library()


# Example 1: A filter that cuts off text after a certain length
@register.filter(name='truncate_eco')
def truncate_eco(value, max_length):
    """Truncates text strings and appends an ellipsis."""
    if len(str(value)) > int(max_length):
        return f"{str(value)[:int(max_length)]}..."
    return value


@register.simple_tag
def current_time(format_string):
    return datetime.now().strftime(format_string)
