from django import template

register = template.Library()

@register.filter
def rupees(value):
    """
    Format value as Indian Rupees
    Usage: {{ product.price|rupees }}
    Output: ₹1,234.56
    """
    try:
        amount = float(value)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"

@register.filter
def inr(value):
    """Short alias for rupees filter"""
    try:
        amount = float(value)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"

@register.simple_tag
def currency_symbol():
    """Returns currency symbol"""
    return '₹'