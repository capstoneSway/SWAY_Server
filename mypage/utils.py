from .models import Restriction

def get_active_restriction(user, restriction_type):
    restrictions = Restriction.objects.filter(
        user=user,
        restriction_type=restriction_type
    )
    for r in restrictions:
        if r.is_active():
            return r
    return None
