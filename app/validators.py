from rest_framework import serializers
from .choices import Status



class CheckStageValidator:
    requires_context = True
    """
    Check if executor provides deadline parameter
    when wants to update stage.
    Additionally stage must be increasing exactly 1 point
    """
    def __call__(self, value, serializer_field):
        instance = serializer_field.instance
        if 'stage' in value:
            if 'deadline' not in value:
                raise serializers.ValidationError({
                    'stage': 'If you want to change stage, you must pass a deadline parameter for new stage'
                })
            try:
                if int(instance.stage) + 1 != int(value['stage']):
                    raise serializers.ValidationError({
                        'stage': 'Wrong value. You must pass value ' + str(int(instance.stage) + 1) + ' for this stage'
                    })
            except TypeError as e:
                raise serializers.ValidationError({
                    'stage': 'You can\'t pass stage before status is \'Processing\' ' + str(e)
                })



class CheckStatusValidator:
    requires_context = True
    """
    Check if executor attempts assign appropriate value for currently status
    """
    def __call__(self, value, serializer_field):
        instance = serializer_field.instance
        if 'status' in value:
            if instance.status == Status.NEW:
                if 'deadline' not in value:
                    raise serializers.ValidationError({
                        'status': 'For update field status to \'Processing\' you must pass deadline parameter for set stage automatically'
                    })                  
                if value['status'] != Status.PROCESSING:
                    raise serializers.ValidationError({
                        'status': 'Wrong value. You must pass 2 for this status'
                    })
            elif instance.status == Status.PROCESSING and value['status'] not in [
                Status.PAYMENT_AWAIT, 
                Status.APPROVAL_AWAIT, 
                Status.FINISHED
            ]:
                raise serializers.ValidationError({
                    'status': 'Wrong value. You must pass 3, 4 or 6 for this status'
                })