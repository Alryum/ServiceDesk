from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ticket, Message
from .serializers import TicketSerializer, CreateTicketSerializer
from .tasks import send_auto_reply
from .filters import TicketFilter


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TicketFilter
    ordering_fields = ['created_at', 'status']
    ordering = ['created_at']

    def create(self, request, *args, **kwargs):
        serializer = CreateTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        send_auto_reply.delay(ticket.id, 'Ваше сообщение принято в обработку')
        return Response({'detail': 'Тикет создан, автоответ отправлен.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == 'closed':
            return Response({'detail': 'Тикет уже закрыт.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = 'closed'
        ticket.save()

        send_auto_reply.delay(ticket.id, 'Ваше обращение закрыто. Спасибо, что обратились к нам!')
        return Response({'detail': 'Тикет закрыт и уведомление отправлено.'})

    @action(detail=True, methods=['post'], url_path='assign', url_name='assign')
    def assign_operator(self, request, pk=None):
        ticket = self.get_object()
        operator = request.user

        if not operator.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if ticket.status == 'closed':
            return Response({'detail': 'Нельзя назначить оператора для закрытого тикета.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.operator = operator
        ticket.status = 'in_progress'
        ticket.save()

        return Response({'detail': 'Тикет назначен оператору.'})

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        ticket = self.get_object()

        if not ticket.operator:
            return Response({'detail': 'Тикет не назначен оператору.'}, status=status.HTTP_400_BAD_REQUEST)

        if ticket.status == 'closed':
            return Response({'detail': 'Нельзя ответить на закрытый тикет.'}, status=status.HTTP_400_BAD_REQUEST)

        content = request.data.get('content')
        if not content:
            return Response({'detail': 'Сообщение не может быть пустым.'}, status=status.HTTP_400_BAD_REQUEST)

        Message.objects.create(
            ticket=ticket,
            sender='operator',
            content=content
        )
        send_auto_reply.delay(ticket.id, content)

        return Response({'detail': 'Ответ отправлен пользователю.'})
