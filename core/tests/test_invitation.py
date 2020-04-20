"""
Event test case created here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import Role
from core.models import EventType, Event


class InvitationTestCase(APITestCase):
    """
    Test cases for the methods started from here
    """

    def setUp(cls):
        """
        Data setup for Unit test case
        :return:
        """
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

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=499,
                          no_of_tickets=250,
                          images="https://www.google.com/images",
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

        cls.end_point = "/core/invite/"

    def test_invitation_api_with_wrong_method(self):
        """
        Testing the api with wrong method name
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_invitation_api_with_wrong_token(self):
        """
        providing wrong token and testing the invitation api
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format('token')
        )
        self.assertEquals(response.status_code, 401)

    def test_invitation_get_api(self):
        """
         Test the get api of invitation
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_event(self):
        """
         Test the get api invitation with specific event id
        """
        response = self.client.get(
            self.end_point, {"event_id": 10}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_user(self):
        """
        Test the get api invitation with specific user id
        """
        response = self.client.get(
            self.end_point, {"user_id": 9}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_invalid_parameters(self):
        """
        Test the get api invitation for invalid parameter
        """
        response = self.client.get(
            self.end_point, {"event_id": 1, "user_id": 1},
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data['data']['invitee_list']), 0)

    def test_invitation_post_api_with_invalid_event_id(self):
        """
        Test the post api invitation with wrong data
        """
        data = {"event": 1000,
                "discount_percentage": 10,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_invitation_post_api_with_valid_details(self):
        """
        Test the post api invitation for valid data
        """
        data = {
            "event": self.event.id,
            "discount_percentage": 10,
            "invitee_list": ["email@gmail.com", "email1@gmail.com"],
            "testing": True
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_event_id_and_users(self):
        """
        Test the post api invitation for same user and event id
        """
        data = {"event": self.event.id,
                "discount_percentage": 10,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": self.event.id,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_event_id_not_users(self):
        """
        Test the post api invitation for same event id
        """
        data = {"event": self.event.id,
                "discount_percentage": 10,
                "invitee_list": ["email1@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": self.event.id,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertNotEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_user_not_event(self):
        """
        Test the post api invitation for same user
        """
        data = {"event": self.event.id,
                "discount_percentage": 10,
                "invitee_list": ["email1@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        prev_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {"event": self.event.id,
                "discount_percentage": 11,
                "invitee_list": ["email@gmail.com"],
                "testing": True
                }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertNotEquals(prev_id, response.data['data']['invitee_list'][0].get('invitation_id'))
        self.assertEquals(response.status_code, 200)

    def test_invitation_delete_api_with_valid_invitation_id(self):
        """
        Tset of delete api with valid id
        :return: response : 500
        """
        data = {
            "invitation_ids": [1, 2],
            "event_id": self.event.id
        }
        response = self.client.delete(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, 200)

    def test_invitation_delete_api_with_invalid_invitation_id(self):
        """
        Test for delete api with invalid id
        :return:
        """
        data = {
            "invitation_ids": [1, 2],
            "event_id": 23
        }
        response = self.client.delete(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, 400)
