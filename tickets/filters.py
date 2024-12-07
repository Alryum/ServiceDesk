from django_filters import rest_framework as filters
from .models import Ticket


class TicketFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Ticket.STATUS_CHOICES)

    created_at_min = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_max = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Ticket
        fields = ['status', 'created_at_min', 'created_at_max']
