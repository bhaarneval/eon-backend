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
    Test cases method start from here
    """

    def setUp(cls):
        """
            Data setup for the test cases here
        """
        role = Role(role="subscriber")
        role.save()
        content = {
            "email": "user12@gmail.com",
            "name": "user12@gmail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
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
                          external_links="google.com", event_created_by_id=cls.user_id)
        cls.event.save()

        cls.end_point = "/core/subscription/"

    def test_subscription_api_with_wrong_method(self):
        """
        Test subscription api with wrong method name
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_subscription_api_with_wrong_token(self):
        """
        Providing wrong token for subscription method
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format("wrong token")
        )
        self.assertEquals(response.status_code, 401)

    def test_subscription_get_api(self):
        """
        Test for get api of subscription
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_particular_event(self):
        """
        Test for subscription get api with event id
        """
        response = self.client.get(
            self.end_point, {"event_id": 3}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_invalid_event(self):
        """
        Providing invalid event id for subscription get api
        """
        response = self.client.get(
            self.end_point, {"event_id": 400}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.data['data']['total'], 0)
        self.assertEquals(response.status_code, 200)

    def test_subscription_api_without_passing_required_fields(self):
        """Required fields are
                    1. event_id
                    2. user_id,
                    3. no_of_tickets,
        """
        data = {"user_id": 28,
                "no_of_tickets": 4}
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.data['message'], "Request Parameters are invalid")
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_free_event(self):
        """
        Payment_id is a not required
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
        Payment_id is required field
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 4,
            "card_number": 5039303342356004,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 400,
            "discount_amount": 300
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_api_with_invalid_event_id(self):
        """
        Payment_id is required field
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
        Payment_id is required field
        """
        data = {
            "event_id": self.event.id,
            "user_id": self.user_id,
            "no_of_tickets": 1000,
            "card_number": 5039303342356004,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 400,
            "discount_amount": 300
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.data['message'], "Number of tickets are invalid")
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_wrong_length_of_card_number(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year
                    3. expiry_month
                    4. amount
                    5. discount_amount
        """
        data = {
            "event_id": 3,
            "user_id": 28,
            "no_of_tickets": 1,
            "card_number": 50393033423,
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 4000,
            "discount_amount": 300
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_passing_string_as_card_number(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year
                    3. expiry_month
                    4. amount
                    5. discount_amount
        """
        data = {
            "event_id": 3,
            "user_id": 28,
            "no_of_tickets": 10,
            "card_number": "INVALID CARD",
            "expiry_year": 2022,
            "expiry_month": 7,
            "amount": 4000,
            "discount_amount": 300
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_wrong_exiry_date(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year (greater or equal current year)
                    3. expiry_month (if year is same as current year
                       then month should be greater than current month)
                    4. amount
                    5. discount_amount
        """
        data = {
            "event_id": 3,
            "user_id": 28,
            "no_of_tickets": 10,
            "card_number": 5039303342356004,
            "expiry_year": 2020,
            "expiry_month": 1,
            "amount": 4000,
            "discount_amount": 300
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)
