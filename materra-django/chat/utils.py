from . import constants
from .models import ConversationMember
from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response

User = get_user_model()


"""
This decorator (for now) only works on functions in ViewSets
where the conversation_id argument is passed
"""
def has_conversation_access(requires_admin: bool = False):
    def wrapper(func):
        def wrapped(viewset_obj, request, *args, **kwargs):
            conversation_id = kwargs.get('conversation_id')
            key = constants.CONVERSATION_ACCESS_KEY.format(request.user.id, conversation_id)
            has_access = cache.get(key)
            if has_access is None:
                try:
                    member = ConversationMember.objects.get(
                            conversation_id=conversation_id, 
                            user_id=request.user.id
                        )
                    has_access = (not requires_admin) or member.is_admin
                except ConversationMember.DoesNotExist:
                    has_access = False
                cache.set(key, has_access)

            if not has_access:
                return Response({}, status=status.HTTP_403_FORBIDDEN)
            return func(viewset_obj, request, *args, **kwargs)

        return wrapped
    return wrapper

def get_available_staff():
    return User.objects.filter(is_staff=True).first()

