from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer

class TicketView(ViewSet): 
    """Honey Rae API Ticket View"""

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = TicketSerializer(new_ticket)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request): 
        """Handle GET requests to get all tickets"""

        service_tickets = []
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == 'done':
                    service_tickets = service_tickets.filter(date_completed__isnull=False)
        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None): 
        """Handle GET requests to get a single ticket"""

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        """Handle PUT requests for Service Tickets"""

        ticket = ServiceTicket.objects.get(pk=pk)

        assigned_employee = Employee.objects.get(pk=request.data['employee'])
        ticket.employee = assigned_employee

        ticket.save()
        return Response(None, status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests for service tickets """
        ticket = ServiceTicket.objects.get(pk=pk)
        ticket.delete()

        return Response(None, status.HTTP_204_NO_CONTENT)

    

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