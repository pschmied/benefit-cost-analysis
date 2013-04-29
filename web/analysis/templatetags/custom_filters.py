from django import template
import re
regex = re.compile(r'^(-?\d+)(\d{3})')


register = template.Library()

def commify(num, separator=','):
    """commify(num, separator) -> string

    Return a string representing the number num with separator inserted
    for every power of 1000.   Separator defaults to a comma.
    E.g., commify(1234567) -> '1,234,567'
    """
    num = '%.0f' %(num)  # just in case we were passed a numeric value
    more_to_do = 1
    while more_to_do:
        (num, more_to_do) = regex.subn(r'\1%s\2' % separator,num)
    return num
commify.is_safe = True

register.filter(commify)