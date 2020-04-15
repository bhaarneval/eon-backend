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
        """
        Data setup for Unit test case
        :return:
        """
        role = Role(role="organiser")
        role.save()
        content = {
            "email": "user12@gmail.com",
            "name": "user12@gmail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organiser",
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

    def test_event_post(self):
        """
        Unit test for Event post Api
        :return:
        """
        # Setup

        json_content = {
            "name": "Diwali",
            "event_type": self.event_type.id,
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
        self.assertEqual(response.data['subscription_fee'], json_content['subscription_fee'])
        self.assertEqual(response.data['event_created_by'], self.user_id)

    def test_event_post_without_parameter(self):
        """
        Unit test for Event post Api
        :return:
        """
        # Setup
        json_content = {}

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
        Get api test case without parameter
        :return:
        """

        # Run
        response = self.client.get("/core/event/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_with_parameter_event_id(self):
        """
        Get api test case with valid event id as a parameter
        :return:
        """
        # Setup
        event_id = self.event.id

        # Run
        response = self.client.get("/core/event/?event_id={id}".format(id=event_id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_type_get_api_with_valid_data(self):
        """
        Get Api for event test cases with valid data
        :return:
        """
        # Run
        response = self.client.get("/core/event-type",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_delete_api_with_valid_data(self):
        """
        Delete Api for event with valid data event id
        """
        # Setup
        event_id = self.event.id

        # Run
        response = self.client.delete("/core/event/{event_id}/".format(event_id=event_id),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_delete_api_with_invalid_even_id(self):
        """
        Test case for delete api event with wrong event id
        :return:
        """
        # Setup
        event_id = 5

        # Run
        response = self.client.delete("/core/event/{event_id}/".format(event_id=event_id),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 400)

    def test_event_patch_api_updating_something_went_wrong(self):
        """
        Test for patch api of event with  valid event id
        :return:
        """
        # Setup
        event_id = self.event.id

        data = {
            "name": "Holi",
            "event_type": self.event_type.id,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38",
            "location": "Giridih",
            "subscription_fee": 499,
            "no_of_tickets": 200,
        }

        # Run
        response = self.client.patch("/core/event/{event_id}/".format(event_id=event_id),
                                     json.dumps(data),
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                     content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_retrieve_api_with_invalid_event_id(self):
        """
        Test for retrieve api of event with invalid user id
        :return:
        """

        # Run
        response = self.client.get("/core/event/12/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 400)

    def test_event_retrieve_api_with_valid_event_id(self):
        """
            Test for retrieve api of event with invalid event id
            :return:
            """

        # Run
        response = self.client.get("/core/event/{id}/".format(id=self.event.id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_for_pre_signed_url_get_api_with_invalid_data(self):
        """
        Test for pre signed url get api without event id
        :return:
        """
        # Run
        response = self.client.get("/core/presigned-url/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_for_pre_signed_url_get_api_with_invalid_event_id(self):
        """
               Test for pre signed url get api with invalid event id
               :return:
               """
        # Run
        response = self.client.get("/core/presigned-url/1/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_for_pre_signed_url_get_api_with_valid_event_id(self):
        """
                     Test for pre signed url get api with valid event id
                     :return:
        """

        # Run
        response = self.client.get("/core/presigned-url/", {'event_id': self.event.id},
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)
