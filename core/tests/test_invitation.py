"""
Event test case created here
"""
import json

from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import EventType, Event, UserProfile, Invitation


class InvitationTestCase(APITestCase):
    """
    Invitation methods test cases are added in this class
    """

    def setUp(cls):
        """
        Data setup for Invitation Unit test cases
        """
        role = Role(role="organizer")
        role.save()

        user = User.objects.create_user(email="user12@gmail.com", password="user123")
        role_obj = Role.objects.get(role="organizer")

        user_profile_obj = UserProfile.objects.create(
            user=user, name="user12@gmail.com", contact_number="9999911111",
            organization="organization", address="Bangalore",
            role=role_obj)
        user_profile_obj.save()

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
        Unit test for invitation get api with wrong method
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_invitation_api_with_wrong_token(self):
        """
        Unit test for invitation get api with wrong token
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format('token')
        )
        self.assertEquals(response.status_code, 401)

    def test_invitation_get_api(self):
        """
        Unit test for invitation get api with valid token
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_after_creating_invitation(self):
        """
        Unit test for invitation get api with valid invitation content
        """
        Invitation.objects.create(event=self.event, discount_percentage=10, email="abcd@gmail.com")
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_event(self):
        """
        Unit test for invitation get api with event id
        """
        response = self.client.get(
            self.end_point, {"event_id": 10}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_user(self):
        """
        Unit test for invitation get api for particular user
        """
        response = self.client.get(
            self.end_point, {"user_id": 9}, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_get_api_with_particular_invalid_parameters(self):
        """
        Unit test for invitation get api for checking user and event specific data
        """
        response = self.client.get(
            self.end_point, {"event_id": 1, "user_id": 1},
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data['data']['invitee_list']), 0)

    def test_invitation_post_api_with_invalid_event_id(self):
        """
        Unit test for invitation post api with invalid event id
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
        Unit test for invitation post api with valid event id
        """
        data = {
            "event": self.event.id,
            "discount_percentage": 10,
            "invitee_list": ["email@gmail.com", "email1@gmail.com", "user12@gmail.com"],
            "testing": True
        }
        response = self.client.post(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)

    def test_invitation_post_api_for_same_event_id_and_users(self):
        """
        Unit test for invitation post api when user invited again
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
        Unit test for invitation post api with for different user
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
        Unit test for invitation post api for same user but different event
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
        Unit test case for invitation delete api with valid invitation id
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
        invitation_id = response.data['data']['invitee_list'][0].get('invitation_id')
        data = {
            "invitation_ids": [invitation_id],
            "event_id": self.event.id,
            "testing": True
        }
        response = self.client.delete(
            self.end_point, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )

        self.assertEquals(response.status_code, 200)

    def test_invitation_delete_api_with_invalid_invitation_id(self):
        """
        Unit test for invitation delete api with invalid invitation id
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
