from django import template
import time

register = template.Library()

@register.filter
def format_seconds(seconds):
    if not seconds:
        return '0m'
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m {secs}s"
