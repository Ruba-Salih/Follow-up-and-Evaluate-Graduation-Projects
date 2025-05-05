from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def dict_get(dict_obj, key):
    try:
        return dict_obj.get(key)
    except Exception:
        return None
    
@register.filter
def is_uploaded_by_participant(file, participants):
    """Return True if file.uploaded_by is among participants (MeetingParticipant.member)"""
    return any(file.uploaded_by == participant.user for participant in participants)