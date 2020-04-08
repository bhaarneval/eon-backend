import datetime
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import User
from core.models import Event, EventType


class EventAPITest(APITestCase):
    # fixtures = ["default.json"]

    # def test_event_post(self):
    #     content = {
    #         "name": "Diwali",
    #         "type": 1,
    #         "date": "2020-04-09",
    #
    #         "description": "New Event",
    #         "external_links": "google.com",
    #         "time": "12:38",
    #         "location": "Panipat",
    #         "images": "",
    #         "subscription_fee": 499,
    #         "no_of_tickets": 200,
    #     }
    #     response = self.client.post(
    #         "core/event/", json.dumps(content),
    #         content_type='application/json'
    #     )
    #     # print(url)
    #     print(response)

    def test_event_get(self):
        """
         Test: unit test for register a user with complete information
               mocked the user detail and call the register api.

        """

        # Setup
        data = dict(email="user@gmail.com", password="user123")
        content = {
            "email": "user@gmail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }

        url1 = reverse('registration')
        register = self.client.post(url1, json.dumps(content),
                                    content_type='application/json')

        print(register)

        # date_time = datetime.datetime.now()
        #
        # user = User.objects.create_user(email="user@gmail.com", password="user123")
        # user.is_active = True
        # user.save()
        #
        # url = reverse('login')
        # print(url)
        #
        # user_data = self.client.post(url, json.dumps(data),
        #                              content_type='application/json')
        # # token = user_data.data['data']['access']
        # print(user_data)
        # # print(token)
        #
        # event_type = EventType(type="Annual function")
        # event_type.save()
        #
        # user_id = User.objects.only('id').get(email='user@gmail.com').id
        # print(user_id)
        #
        # event = Event(name="test_event", type="Conference", description="New Event", date="2020-04-02",
        # time="12:38:00", location="karnal", subscription_fee=499, no_of_tickets=250,
        # images =https://www.google.com/images sold_tickets=2, external_links=google.com,
        # event_created_by_id=user_id) event.save()
        #
        # # Run
        # response = self.client.get("core/event/", HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        #                            content_type="application/json")

        # print(response)

        # Check
        # self.assertEqual(response['status'], 201)
        # self.assertEqual(response['message'], 'User created successfully')
