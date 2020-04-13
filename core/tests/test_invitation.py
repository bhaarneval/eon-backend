"""
Event test case created here
"""
import json
from rest_framework.test import APITestCase


class InvitationTestCase(APITestCase):
    """
    test cases for the methods started from here
    """
    fixtures = ['default.json']

    def setUp(cls):
        data = dict(email="user2@gmail.com", password="Password")
        cls.user = cls.client.post('/authentication/login',
                                   json.dumps(data), content_type='application/json')
        cls.token = cls.user.data['data']['access']
        cls.ENDPOINT = "/core/invite/"

    def test_invitation_api_with_wrong_method(self):
        """
        testing the api with wrong method name
        """
        response = self.client.put(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_invitation_api_with_wrong_token(self):
        """
        providing wrong token and testing the invitation api
        """
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format('token')
        )
        self.assertEquals(response.status_code, 401)

    def test_invitation_get_api(self):
        """
         test the get api of invitation
        """
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_event(self):
        """
         test the get api invitation with specific event id
        """
        response = self.client.get(
            self.ENDPOINT, {"event_id": 10}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_user(self):
        """
        test the get api invitation with specific user id
        """
        response = self.client.get(
            self.ENDPOINT, {"user_id": 9}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_invalid_parameters(self):
        """
        test the get api invitation for invalid parameter
        """
        response = self.client.get(
            self.ENDPOINT, {"event_id": 1, "user_id": 1},
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data['data']['invitee_list']), 0)

    def test_invitation_post_api_with_invalid_event_id(self):
        """
        test the post api invitation with wrong data
        """
        data = {"event": 1000,
                "discount_percentage": 10,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_invitation_post_api_with_valid_details(self):
        """
        test the post api invitation for valid data
        """
        data = {"event": 9,
                "discount_percentage": 10,
                "invitee_list": ["email@gmail.com", "email1@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_event_id_and_users(self):
        """
        test the post api invitation for same user and event id
        """
        data = {"event": 9,
                "discount_percentage": 10,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": 9,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_event_id_not_users(self):
        """
        test the post api invitation for same event id
        """
        data = {"event": 9,
                "discount_percentage": 10,
                "invitee_list": ["email1@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": 9,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertNotEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_user_not_event(self):
        """
        test the post api invitation for same user
        """
        data = {"event": 9,
                "discount_percentage": 10,
                "invitee_list": ["email1@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": 9,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertNotEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)
