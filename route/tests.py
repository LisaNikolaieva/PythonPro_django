from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test import Client
from route.models import Event
from unittest.mock import patch
from route.views import route_add_event


# Create your tests here.


class TestEvent(TestCase):

    def test_anonimus_user(self):
        client = Client()
        response = client.get('/route/1/add_event')
        self.assertEqual(401, response.status_code)

        response_client_post = client.post('/route/1/add_event')
        self.assertEqual(401, response_client_post.status_code)

    def setUp(self):
        self.factory = RequestFactory()

        class userMock():
            def has_perm(self, *args, **kwargs):
                return True

        self.user = userMock()

    def test_with_user(self):
        request = self.factory.post('/route/1/add_event', {'start_date': "2031-10-01",
                                                          'price': 100})
        request.user = self.user
        route_id = 1
        response = route_add_event(request, route_id)
        self.assertEqual(200, response.status_code)
        itms = list(Event.objects.all().filter(id_route=1))
        self.assertEqual(1, len(itms))
