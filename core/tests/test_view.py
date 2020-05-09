"""
Test for core module api added here
"""
import json

from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import EventType, Event, UserInterest, UserProfile


class RestAPITest(APITestCase):
    """
    Test cases are added in this class
    """

    def setUp(cls):
        """
        Data set up for the unit test
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
        cls.user = User.objects.get(id=cls.user_id)

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=500,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

    def test_subscriber_reminder_post_api_with_valid_data(self):
        """
        Unit test for notify post api with valid data
        """
        # Setup
        json_data = {
            "event_id": self.event.id,
            "message": "test message",
            "type": "reminder",
            "testing": True
        }

        # Run
        response = self.client.post("/core/notify-subscriber/", json.dumps(json_data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_for_get_user_api(self):
        """
        Unit test for user get api
        """
        # Run
        response = self.client.get("/core/user/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_user_api_with_wrong_token(self):
        """
        Unit test for user get api with wrong token
        """
        # Run
        response = self.client.get("/core/user/",
                                   HTTP_AUTHORIZATION="Bearer {}".format("wrong-token"),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 401)

    def test_for_get_user_details_api_with_invalid_user_id(self):
        """
        Unit test for user get api with invalid user id
        """
        user_interest = UserInterest(event_type=self.event_type, user=self.user)
        user_interest.save()

        # Run
        response = self.client.get("/core/user/207/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 400)

    def test_for_get_user_details_api_with_valid_user_id(self):
        """
        Unit test for user get api with valid user id
        """
        user_interest = UserInterest(event_type=self.event_type, user=self.user)
        user_interest.save()

        # Run
        response = self.client.get(f"/core/user/{self.user_id}/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_patch_user_api_without_parameter(self):
        """
        Unit test for user patch api with any parameter
        """
        user_interest = UserInterest(event_type=self.event_type, user=self.user)
        user_interest.save()

        # Run
        response = self.client.patch(f"/core/user/{self.user_id}/",
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                     content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_patch_user_api_with_parameter(self):
        """
        Unit test for user patch api with parameter
        """
        user_interest = UserInterest(event_type=self.event_type, user=self.user)
        user_interest.save()

        data = {
            "field_name": "test",
            "interest": [self.event_type.id]
        }

        # Run
        response = self.client.patch(f"/core/user/{self.user_id}/", json.dumps(data),
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                     content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_event_summary_for_all_event(self):
        """
        Unit test for event summary get api for all events
        """
        # Run
        response = self.client.get("/core/event-summary/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_event_summary_for_all_event_with_wrong_token(self):
        """
        Unit test for event summary get api with wrong token
        """
        # Run
        response = self.client.get("/core/event-summary/",
                                   HTTP_AUTHORIZATION="Bearer {}".format("wrong_token"),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 401)

    def test_api_for_sending_email_to_friend_with_invalid_event_id(self):
        """
        Unit test for sending email to friend with invalid event id
        """
        data = {
            "email_id": "user21@gmail.com",
            "event_id": 300,
            "message": "Testing",
            "testing": True
        }
        response = self.client.post("/core/share-with-friend/", json.dumps(data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")
        # check
        self.assertEqual(response.status_code, 400)

    def test_api_for_sending_email_to_friend_with_valid_event_id(self):
        """
        Unit test for sending email to friend with valid event id
        """
        data = {
            "email_id": "user21@gmail.com",
            "event_id": self.event.id,
            "message": "Testing",
            "testing": True
        }
        response = self.client.post("/core/share-with-friend/", json.dumps(data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_event_summary_for_completed_event(self):
        """
        Unit test for event summary get api for completed events
        """
        # Run
        response = self.client.get("/core/event-summary/?event_status=completed",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_event_summary_for_upcoming_event(self):
        """
        Unit test for event summary get api for upcoming events
        """
        # Run
        response = self.client.get("/core/event-summary/?event_status=upcoming",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_for_get_event_summary_for_cancelled_event(self):
        """
        Unit test for event summary get api for cancelled events
        """
        # Run
        response = self.client.get("/core/event-summary/?event_status=cancelled",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")
        # check
        self.assertEqual(response.status_code, 200)

    def test_subscriber_update_post_api_with_valid_data(self):
        """
        Unit test for notify post api with valid data
        """
        # Setup
        json_data = {
            "event_id": self.event.id,
            "message": "test message",
            "type": "send_updates",
            "testing": True
        }

        # Run
        response = self.client.post("/core/notify-subscriber/", json.dumps(json_data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
