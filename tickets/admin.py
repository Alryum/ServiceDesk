from django.contrib import admin
from .models import Ticket, Message, IncomingEmail


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fk_name = 'ticket'
    fields = ['sender', 'content', 'sent_at']
    readonly_fields = ['sender', 'content', 'sent_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'user_email', 'status', 'operator', 'created_at']
    search_fields = ['subject', 'user_email']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'sender', 'sent_at']
    search_fields = ['sender', 'content']
    readonly_fields = ['ticket', 'sender', 'content', 'sent_at']


@admin.register(IncomingEmail)
class IncomingEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'subject', 'received_at']
    search_fields = ['sender', 'subject']
    readonly_fields = ['sender', 'subject', 'body', 'received_at']
