from django import template

register = template.Library()

@register.filter
def calculate_difference(value1, value2):
    try:
        return float(value1) - float(value2)
    except (ValueError, TypeError):
        return 
    
    
@register.filter(name='get_category_total')
def get_category_total(category_totals, category_name):
    return category_totals.get(category_name, 0)

