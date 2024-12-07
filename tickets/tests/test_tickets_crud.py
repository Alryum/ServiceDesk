import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models import Ticket


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_ticket_success(api_client):
    URL = reverse('ticket-list')
    data = {
        'subject': 'Проблема с авторизацией',
        'user_email': 'user@example.com',
    }

    response = api_client.post(URL, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['detail'] == 'Тикет создан, автоответ отправлен.'

    ticket = Ticket.objects.get(subject='Проблема с авторизацией')
    assert ticket.user_email == 'user@example.com'
    assert ticket.status == 'new'


@pytest.mark.django_db
def test_create_ticket_failure(api_client):
    """Ошибка при отсутствии обязательных полей"""
    URL = reverse('ticket-list')
    data = {}
    response = api_client.post(URL, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'subject' in response.data
    assert 'user_email' in response.data
