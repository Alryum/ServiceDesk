from celery import shared_task
from .models import IncomingEmail, Ticket, Message

@shared_task
def process_incoming_emails():
    """Обработка входящих писем"""
    emails = IncomingEmail.objects.all()

    for email in emails:
        ticket = Ticket.objects.create(
            subject=email.subject,
            user_email=email.sender,
        )
        Message.objects.create(
            ticket=ticket,
            sender='user',
            content=email.body,
        )
        Message.objects.create(
            ticket=ticket,
            sender='system',
            content='Ваше обращение зарегистрировано и находится в работе.',
        )
        email.delete()

@shared_task
def send_auto_reply(ticket_id:int, message: str):
    """Отправка автоответа пользователю"""
    # Эмуляция автоответа
    ticket = Ticket.objects.get(id=ticket_id)
    Message.objects.create(
        ticket=ticket,
        sender='system',
        content=message,
    )
