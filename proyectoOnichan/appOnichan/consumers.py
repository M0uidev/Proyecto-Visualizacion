import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from django.db.models import Sum, F
from django.core.serializers.json import DjangoJSONEncoder

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "dashboard_admin"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send initial data
        data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps(data, cls=DjangoJSONEncoder))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def dashboard_update(self, event):
        # Handler for group messages
        data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps(data, cls=DjangoJSONEncoder))

    @database_sync_to_async
    def get_dashboard_data(self):
        from .views import get_dashboard_context
        from django.http import HttpRequest, QueryDict
        
        # Mock request with query params from WebSocket scope
        request = HttpRequest()
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        request.GET = QueryDict(query_string)
        request.user = self.scope.get('user') # Add user to request
        
        # Reuse logic from views.py
        context, dashboard_data = get_dashboard_context(request)
        
        # Add period to data for frontend validation
        dashboard_data['period'] = context.get('period')
        
        return dashboard_data
