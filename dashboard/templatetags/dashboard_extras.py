# dashboard/templatetags/dashboard_extras.py
from django import template

register = template.Library()

@register.filter
def subtract_percentage(total_stroke, percentage):
    try:
        # Calculates stroke-dashoffset formula parameters smoothly
        return float(total_stroke) * (1 - (float(percentage) / 100.0))
    except (ValueError, TypeError):
        return total_stroke