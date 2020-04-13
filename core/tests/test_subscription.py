"""
test for subscriptions are here
"""
import json
from rest_framework.test import APITestCase


# Create your tests here.


class SubscriptionAPITest(APITestCase):
    """
    Test cases method start from here
    """
    fixtures = ["default.json"]

    def setUp(cls):
        """
        data setup for the test cases here
        """
        data = dict(email="user2@gmail.com", password="Password")
        cls.user = cls.client.post('/authentication/login',
                                   json.dumps(data), content_type='application/json')
        cls.token = cls.user.data['data']['access']
        cls.end_point = "/core/subscription/"

    def test_subscription_api_with_wrong_method(self):
        """
        test subscription api with wrong method name
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_subscription_api_with_wrong_token(self):
        """
        providing wrong token for subscription method
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format("wrong token")
        )
        self.assertEquals(response.status_code, 401)

    def test_subscription_get_api(self):
        """
        test for get api of subscription
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_particular_event(self):
        response = self.client.get(
            self.end_point, {"event_id": 3}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_invalid_event(self):
        """
        providing invalid event id for subscription get api
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
        """ payment_id is a not required
        """
        data = {
            "event_id": 12,
            "user_id": 28,
            "no_of_tickets": 4,
            "amount": 0
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_api_with_paid_event(self):
        """ payment_id is required field"""
        data = {
            "event_id": 3,
            "user_id": 28,
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
        """ payment_id is required field"""
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
        """ payment_id is required field"""
        data = {
            "event_id": 3,
            "user_id": 28,
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
