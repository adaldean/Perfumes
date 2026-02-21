from django import template
from django.contrib.admin.models import LogEntry

register = template.Library()

@register.simple_tag
def get_admin_log(limit=10, for_user=None):
    if for_user:
        return LogEntry.objects.filter(user=for_user).select_related('content_type', 'user')[:limit]
    return LogEntry.objects.select_related('content_type', 'user')[:limit]
