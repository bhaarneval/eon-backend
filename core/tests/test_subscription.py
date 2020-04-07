import json
from rest_framework.test import APITestCase


# Create your tests here.


class SubscriptionAPITest(APITestCase):
    fixtures = ["default.json"]

    def setUp(cls):
        data = dict(email="user2@gmail.com", password="Password")
        cls.user = cls.client.post('/authentication/login', json.dumps(data), content_type='application/json')
        cls.token = cls.user.data['data']['access']
        cls.ENDPOINT = "/core/subscription/"

    def test_subscription_api_with_wrong_method(self):
        response = self.client.put(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_subscription_api_with_wrong_token(self):
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format("wrong token")
        )
        self.assertEquals(response.status_code, 401)

    def test_subscription_get_api(self):
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_particular_event(self):
        response = self.client.get(
            self.ENDPOINT, {"event_id": 3}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_subscription_get_api_with_invalid_event(self):
        response = self.client.get(
            self.ENDPOINT, {"event_id": 400}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
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
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.data['message'], "Required Fields are not present")
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_free_event(self):
        """ payment_id is a not required
        """
        data = {
            "event_id": 12,
            "user_id": 28,
            "no_of_tickets": 4
        }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 201)

    def test_subscription_api_with_paid_event(self):
        """ payment_id is required field"""
        data = {
            "event_id": 3,
            "user_id": 28,
            "no_of_tickets": 4,
            "payment_id": 27
        }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
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
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_subscription_api_with_no_of_tickets_greater_than_tickets_left(self):
        """ payment_id is required field"""
        data = {
            "event_id": 3,
            "user_id": 28,
            "no_of_tickets": 1000,
        }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

