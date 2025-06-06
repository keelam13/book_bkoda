from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        print(f"DEBUG: get_field filter: Field '{field_name}' not found in form.")
        return None # This None is what causes the CrispyError

@register.filter
def concat_strings(value1, value2):
    """Concatenates two values as strings."""
    return str(value1) + str(value2)