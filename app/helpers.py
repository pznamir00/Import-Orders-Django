from .models import Log

def create_log(order, event, deadline=None):
    return Log.objects.create(
        order=order,
        event=event,
        deadline=deadline
    )