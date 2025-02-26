from .views_app import (
    index, 
    room,
    ConversationViewset,
    EnquiryViewset
)
from .views_auth import (
    signin,
    signout,
    signup
)

from django.urls import path

app_name = 'chat'

urlpatterns = [
    path('', index, name='index'), 
    path('login', signin, name='login'),
    path('logout', signout, name='logout'),
    path('signup', signup, name='signup'),
    path('chat', room, name='room'),

    path('api/chat/get-messages/<str:conversation_id>', ConversationViewset.as_view({'get': 'get_messages'}), name='get-messages'),
    path('api/chat/create-room', ConversationViewset.as_view({'post': 'create_conversation'}), name='create-room'),
    path('api/chat/get-conversations/', ConversationViewset.as_view({'get': 'get_conversations'}), name='get-conversations'),
    path('api/chat/get-members/<str:conversation_id>', ConversationViewset.as_view({'get': 'get_members'}), name='get-members'),
    path('api/chat/upload-file/<str:conversation_id>', ConversationViewset.as_view({'post': 'upload_file'}), name='upload-file'),
    path('api/chat/archive-conversation/<str:conversation_id>', ConversationViewset.as_view({'get': 'archive_conversation'}), name='archive-conversation'),
    
    path('api/enquiry/create', EnquiryViewset.as_view({'post': 'create_enquiry'}), name='create-enquiry')
]
