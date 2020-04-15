"""
Test for core module api added here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import EventType, Event


class RestAPITest(APITestCase):
    """
    Test cases are created in this class
    """

    def setUp(cls):
        """
        Data set up for the unit test
        :return:
        """
        role = Role(role="organizer")
        role.save()
        content = {
            "email": "usertest@mail.com",
            "name": "usertest@mail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }

        cls.client.post('/authentication/registration', json.dumps(content),
                        content_type='application/json')

        data = dict(email="usertest@mail.com", password="user123")
        login_response = cls.client.post('/authentication/login', json.dumps(data),
                                         content_type='application/json')
        cls.user_id = login_response.data['data']['user']['user_id']
        cls.token = login_response.data['data']['access']
        cls.user = User.objects.get(id=cls.user_id)

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=499,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=2,
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

    def test_subscriber_notify_post_api_with_valid_data(self):
        """
        Unit test for notify post api
        :return:
        """
        # Setup
        json_data = {
            "event_id": self.event.id,
            "message": "test message",
            "type": "reminder"
        }

        # Run
        response = self.client.post("/core/notify-subscriber/", json.dumps(json_data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_for_get_user_api(self):
        """
        Get api of user
        :return:
        """
        # Run
        response = self.client.get("/core/user/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_user_api_with_wrong_token(self):
        """
        Get api of user
        :return:
        """
        # Run
        response = self.client.get("/core/user/",
                                   HTTP_AUTHORIZATION="Bearer {}".format("wrong-token"),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 401)
