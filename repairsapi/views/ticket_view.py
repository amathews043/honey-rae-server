from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer

class TicketView(ViewSet): 
    """Honey Rae API Ticket View"""

    def list(self, request): 
        """Handle GET requests to get all tickets"""

        service_tickets = []
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None): 
        """Handle GET requests to get a single ticket"""

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)
    

class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Employee
        fields = ('id', 'user','specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Customer
        fields = ('id', 'user', 'address', 'full_name',)
    

class TicketSerializer(serializers.ModelSerializer):
    """JSON serializer for Service Tickets"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta: 
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed')
        depth = 1