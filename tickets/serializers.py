from rest_framework import serializers
from .models import Ticket, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'sent_at']

class TicketSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'user_email', 'created_at', 'updated_at', 'status', 'operator', 'messages']

class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['subject', 'user_email']
