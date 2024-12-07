from datetime import datetime
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from tickets.models import Message, Ticket

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

# == get tests


@pytest.mark.django_db
def test_filter_by_status(api_client):
    Ticket.objects.create(subject='Test 1', user_email='user1@test.com', status='new')
    Ticket.objects.create(subject='Test 2', user_email='user2@test.com', status='closed')

    url = reverse('ticket-list') + '?status=new'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['status'] == 'new'


@pytest.mark.django_db
def test_sorting_by_created_at(api_client):
    Ticket.objects.create(subject='Test 2', user_email='user2@test.com')
    Ticket.objects.create(subject='Test 1', user_email='user1@test.com')
    Ticket.objects.create(subject='Test 3', user_email='user3@test.com')

    url = reverse('ticket-list') + '?ordering=-created_at'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['subject'] == 'Test 3'
    assert response.data[1]['subject'] == 'Test 1'
    assert response.data[2]['subject'] == 'Test 2'


@pytest.mark.django_db
def test_filter_by_date_range(api_client):
    ticket = Ticket.objects.create(subject='Test 1', user_email='user1@test.com')
    ticket.created_at = datetime(2023, 12, 1, 10, 0, 0)
    ticket.save()
    ticket = Ticket.objects.create(
        subject='Test 2', user_email='user2@test.com', created_at='2023-12-03T10:00:00Z')
    ticket.created_at = datetime(2023, 12, 3, 10, 0, 0)
    ticket.save()

    url = reverse('ticket-list') + \
        '?created_at_min=2023-12-01T00:00:00Z&created_at_max=2023-12-02T23:59:59Z'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['subject'] == 'Test 1'

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


# == assign_operator tests


@pytest.mark.django_db
def test_assign_operator_success(api_client, ticket, test_operator):
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-assign', args=[ticket.id])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Тикет назначен оператору.'

    ticket.refresh_from_db()
    assert ticket.operator == test_operator


@pytest.mark.django_db
def test_assign_operator_ticket_not_found(api_client, test_operator):
    """Попытка назначения оператора на несуществующий тикет"""
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-assign', args=[999])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_assign_operator_unauthorized(api_client, ticket):
    url = reverse('ticket-assign', args=[ticket.id])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# == reply tests


@pytest.mark.django_db
def test_reply_success(api_client, ticket, test_operator):
    api_client.force_authenticate(user=test_operator)
    ticket.operator = test_operator
    ticket.save()
    url = reverse('ticket-reply', args=[ticket.id])
    response = api_client.post(url, data={'content': 'Привет, я - принц из Нигерии, такое дело...'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Ответ отправлен пользователю.'

    assert Message.objects.filter(ticket=ticket, sender='operator',
                                  content='Привет, я - принц из Нигерии, такое дело...').exists()


@pytest.mark.django_db
def test_reply_without_operator(api_client, ticket):
    """Попытка ответа на тикет без назначенного оператора"""
    ticket.operator = None
    ticket.save()
    url = reverse('ticket-reply', args=[ticket.id])
    response = api_client.post(url, data={'content': 'Арбуз больше не ягода.'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Тикет не назначен оператору.'


@pytest.mark.django_db
def test_reply_ticket_not_found(api_client, test_operator):
    api_client.force_authenticate(user=test_operator)
    url = reverse('ticket-reply', args=[999])
    response = api_client.post(url, data={'content': 'Динозавры живут на обратной стороне луны.'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
