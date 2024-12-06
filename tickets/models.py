from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    subject = models.CharField(max_length=255)
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    operator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='tickets')

    def __str__(self):
        return f'Обращение {self.id} - {self.subject}'

class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=255)  # "user" или "operator"
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Сообщение от {self.sender}: {self.sent_at}'
