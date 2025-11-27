from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_cart_count(context):
    request = context.get('request')
    if not request:
        return 0
    cart = request.session.get("cart", {})
    rewards_cart = request.session.get("rewards_cart", {})
    return sum(cart.values()) + sum(rewards_cart.values())
