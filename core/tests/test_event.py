"""
Event related test cases are added here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import Role
from core.models import Event, EventType


class EventAPITest(APITestCase):
    """
    Event methods test cases are added in this class
    """

    def setUp(cls):
        role = Role(role="organizer")
        role.save()
        content = {
            "email": "user12@gmail.com",
            "name": "user12@gmail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }

        url1 = reverse('registration')
        cls.client.post(url1, json.dumps(content),
                        content_type='application/json')

        data = dict(email="user12@gmail.com", password="user123")
        login_response = cls.client.post('/authentication/login', json.dumps(data),
                                         content_type='application/json')
        cls.user_id = login_response.data['data']['user']['user_id']
        cls.token = login_response.data['data']['access']

    def test_event_post(self):
        """
        Unit test for Event post Api
        :return:
        """
        # Setup

        event_type = EventType(type="Annual function")
        event_type.save()

        json_content = {
            "name": "Diwali",
            "event_type": event_type.id,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38:00",
            "location": "mumbai",
            "images": "https://www.google.com/images",
            "subscription_fee": 499,
            "no_of_tickets": 200,
            "event_created_by": self.user_id
        }

        # Run
        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.data['name'], json_content['name'])
        self.assertEqual(response.data['description'], json_content['description'])
        self.assertEqual(response.data['date'], json_content['date'])
        self.assertEqual(response.data['location'], json_content['location'])
        self.assertEqual(response.data['images'], json_content['images'])
        self.assertEqual(response.data['subscription_fee'], json_content['subscription_fee'])
        self.assertEqual(response.data['event_created_by'], self.user_id)

    def test_event_post_with_empty_body(self):
        """
        Unit test for Event post Api
        :return:
        """
        # Setup

        event_type = EventType(type="Annual function")
        event_type.save()

        json_content = {

        }

        # Run

        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        # Check

        self.assertEqual(response.status_code, 400)

    def test_event_post_with_invalid_event_type_id(self):
        """
        Unit test for Event post Api without required information
        :return:
        """
        # Setup

        json_content = {
            "name": "Diwali",
            "event_type": 1000,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38:00",
            "location": "mumbai",
            "images": "https://www.google.com/images",
            "subscription_fee": 499,
            "no_of_tickets": 200,
            "user_created_by": self.user_id
        }

        # Run

        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_event_get_without_parameter(self):
        """
        Test for event get api withot passing parameter
        """
        # Setup
        event_type = EventType(type="Annual function")
        event_type.save()

        event = Event(name="test_event", type=event_type, description="New Event",
                      date="2020-04-02",
                      time="12:38:00", location="karnal", subscription_fee=499, no_of_tickets=250,
                      images="https://www.google.com/images", sold_tickets=2,
                      external_links="google.com",
                      event_created_by_id=self.user_id)
        event.save()

        # Run
        response = self.client.get("/core/event/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_with_parameter_event_id(self):
        """
        Test for event get with event id
        """
        # Setup
        event_type = EventType(type="Annual function")
        event_type.save()

        event = Event(name="test_event", type=event_type, description="New Event",
                      date="2020-04-02",
                      time="12:38:00", location="karnal", subscription_fee=499, no_of_tickets=250,
                      images="https://www.google.com/images", sold_tickets=2,
                      external_links="google.com",
                      event_created_by_id=self.user_id)
        event.save()
        event_id = event.id

        # Run
        response = self.client.get("/core/event/?event_id={id}".format(id=event_id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)
