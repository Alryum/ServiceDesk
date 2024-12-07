import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models import Ticket

# == fixtures


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_operator():
    return User.objects.create_user(username='operator', password='testpassword')


@pytest.fixture
def ticket():
    return Ticket.objects.create(subject='Test Ticket', user_email='user@example.com')

# == create tests


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


# == close tests

@pytest.mark.django_db
def test_close_ticket_success(api_client, ticket, test_operator):
    ticket.operator = test_operator
    ticket.save()
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-close', args=[ticket.id])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Тикет закрыт и уведомление отправлено.'
    ticket.refresh_from_db()
    assert ticket.status == 'closed'


@pytest.mark.django_db
def test_close_ticket_already_closed(api_client, ticket, test_operator):
    ticket.operator = test_operator
    ticket.status = 'closed'
    ticket.save()
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-close', args=[ticket.id])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Тикет уже закрыт.'


@pytest.mark.django_db
def test_close_ticket_not_found(api_client, test_operator):
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-close', args=[999])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND