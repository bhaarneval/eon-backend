"""
Test for subscriptions are here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

# Create your tests here.
from authentication.models import Role
from core.models import Event, EventType


class SubscriptionAPITest(APITestCase):
    """
    Subscription methods test cases are added in this class
    """

    def setUp(cls):
        """
        Data setup for the Subscription Unit test cases
        """
        role = Role(role="subscriber")
        role.save()
        content = {
            "email": "user12@gmail.com",
            "name": "user 12",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
            "organization": "Eventhigh"
        }

        url1 = reverse('registration')
        response = cls.client.post(url1, json.dumps(content),
                                   content_type='application/json')

        cls.user_id = response.data['data']['user']['user_id']
        cls.token = response.data['data']['access']

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=100,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com", event_created_by_id=cls.user_id)
        cls.event.save()
        cls.event_free = Event(name="test_event_free", type=cls.event_type, description="New Event",
                               date="2020-04-02", time="12:38:00", location="karnal",
                               subscription_fee=0, no_of_tickets=250, images="https://www.google.com/images",
                               sold_tickets=0, external_links="google.com", event_created_by_id=cls.user_id)
        cls.event_free.save()

        cls.end_point = "/core/subscription/"

    def test_subscription_api_with_wrong_method_type(self):
        """
        Unit test for subscription get api with wrong method
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_subscription_api_with_invalid_user_id(self):
        """
        Unit test for feedback post api with invalid user id
        """
        data = {"user_id": 28,
                "no_of_tickets": 4}
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_no_payment_details_for_paid_event(self):
        """
        Unit test for feedback post api with no payment details for paid event
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 4
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_paid_event(self):
        """
        Unit test for subscription post api with valid payment details for paid event
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 4,
            "card_number": 5039303342356004,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 400,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_api_with_invalid_event_id(self):
        """
        Unit test for subscription post api with invalid event id
        """
        data = {
            "event_id": 4000,
            "user_id": 28,
            "no_of_tickets": 4
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_no_of_tickets_greater_than_tickets_left(self):
        """
        Unit test for subscription post api with no of tickets more than tickets left
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 1000,
            "card_number": 5039303342356004,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 10000,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_wrong_length_of_card_number(self):
        """
        Unit test for subscription post api with wrong card no
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 1,
            "card_number": 50393033423,  # length is less the 16
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 100,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 500)

    def test_subscription_api_with_passing_string_as_card_number(self):
        """
        Unit test for subscription post api with invalid card number
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 10,
            "card_number": "INVALID CARD",
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 1000,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 500)

    def test_subscription_api_with_wrong_expiry_date(self):
        """
        Unit test for subscription post api with wrong expiry date
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 10,
            "card_number": 5039303342356004,
            "expiry_year": 2019,
            "expiry_month": 1,
            "amount": 1000,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 500)

    def test_subscription_api_with_reducing_subscribed_ticket(self):
        """
        Unit test for subscription post api
        """
        self.test_subscription_api_with_paid_event()
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": -2,
            "card_number": 5039303342356004,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": -400,
            "discount_amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_api_with_free_event(self):
        """
        Unit test for subscription post api for free event
        """
        data = {
            "event_id": self.event_free.id,
            "user_id": self.user_id,
            "no_of_tickets": 4,
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_delete_api(self):
        """
        Unit test for subscription delete api
        """
        self.test_subscription_api_with_free_event()
        response = self.client.delete(
            f"/core/subscription/{str(self.event_free.id)}/", HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)
