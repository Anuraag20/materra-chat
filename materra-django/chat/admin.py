from django.contrib import admin
from .models import Conversation
# Register your models here.

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('name', 'archived',)
    list_editable = ('archived',)
