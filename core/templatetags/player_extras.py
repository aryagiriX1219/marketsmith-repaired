from django import template

register = template.Library()

@register.filter
def get_player_by_id(players, player_id):
    """
    Given a queryset or list of Player objects and a player_id, return the Player object with that id.
    Usage: {% with player=players|get_player_by_id:some_id %}
    """
    for p in players:
        if p.id == player_id:
            return p
    return None
