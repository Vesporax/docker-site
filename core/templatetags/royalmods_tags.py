from django import template

register = template.Library()

STATUS_FR = {
    'pending': 'En attente',
    'approved': 'Approuvé',
    'rejected': 'Rejeté',
}


@register.filter
def status_fr(value):
    """Traduit les statuts de mod en français."""
    return STATUS_FR.get(value, value)