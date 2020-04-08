import json
from rest_framework.test import APITestCase


# Create your tests here.


class EventAPITest(APITestCase):
    fixtures = ["default.json"]

    def setUp(cls):
        data = dict(email="user2@gmail.com", password="Password")
        cls.user = cls.client.post('/authentication/login', json.dumps(data), content_type='application/json')
        cls.token = cls.user.data['data']['access']
        cls.ENDPOINT = "/core/event/"

    def test_event_api_with_wrong_method(self):
        response = self.client.post(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)
