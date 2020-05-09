"""
Test cases for wish list api method are added here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import Event, EventType, WishList, UserProfile


class WishListAPITest(APITestCase):
    """
    Wish list methods test cases are added in this class
    """

    def setUp(cls):
        """
        Data setup for the Wish list Unit test cases
        """
        role = Role(role="subscriber")
        role.save()
        role1 = Role(role="organizer")
        role1.save()
        content = {
            "email": "user12@gmail.com",
            "name": "user 12",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
            "organization": "Eventhigh"
        }

        organizer = User.objects.create_user(email="user21@gmail.com", password="user123")
        role_obj = Role.objects.get(role="organizer")

        org_profile_obj = UserProfile.objects.create(
            user=organizer, name="user12@gmail.com", contact_number="9999911111",
            organization="organization", address="Bangalore",
            role=role_obj)
        org_profile_obj.save()

        data = dict(email="user21@gmail.com", password="user123")

        login_response = cls.client.post('/authentication/login', json.dumps(data),
                                         content_type='application/json')
        cls.org_id = login_response.data['data']['user']['user_id']
        cls.org_token = login_response.data['data']['access']

        url = reverse('registration')
        response = cls.client.post(url, json.dumps(content),
                                   content_type='application/json')

        cls.user_id = response.data['data']['user']['user_id']
        cls.token = response.data['data']['access']

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=500,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com",
                          event_created_by_id=cls.org_id)
        cls.event.save()

    def test_wish_list_post_api_without_event_id(self):
        """
        Unit test for wish list post api without event_id
        """
        # Setup

        json_content = {
            # "event_id": self.event.id
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 400)

    def test_wish_list_post_api_with_valid_event_id(self):
        """
        Unit test for wish list post api with valid event id
        """
        # Setup

        json_content = {
            "event_id": self.event.id
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 200)

    def test_wish_list_post_api_with_invalid_event_id(self):
        """
        Unit test for wish list post api with invalid event id
        """
        # Setup

        json_content = {
            "event_id": 100
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 400)

    def test_wish_list_delete_api_with_invalid_event_id(self):
        """
        Unit test for wish list delete api with invalid event id
        """
        # Setup

        event_id = 6

        # Run
        response = self.client.delete("/core/wishlist/{id}/".format(id=event_id),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 400)

    def test_wish_list_delete_api_with_valid_event_id(self):
        """
        Unit test for wish list delete api with valid event id
        """
        user = User.objects.get(id=self.user_id)
        wish = WishList(event=self.event, user=user)
        wish.save()

        # Run
        response = self.client.delete("/core/wishlist/{id}/".format(id=self.event.id),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 200)

    def test_wish_list_post_api_for_duplicate_active_entry(self):
        """
        Unit test for wish list post api for duplicate active entry
        """
        # Setup

        user = User.objects.get(id=self.user_id)
        wish = WishList(event=self.event, user=user)
        wish.save()

        json_content = {
            "event_id": self.event.id
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 200)

    def test_wish_list_post_api_for_duplicate_inactive_entry(self):
        """
        Unit test for wish list post api for duplicate inactive entry
        """
        # Setup

        user = User.objects.get(id=self.user_id)
        wish = WishList(event=self.event, user=user, is_active=False)
        wish.save()

        json_content = {
            "event_id": self.event.id
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 200)

    def test_wish_list_post_api_with_event_creator_id(self):
        """
        Unit test for wish list post api with event creator id
        """
        # Setup
        json_content = {
            "event_id": self.event.id
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.org_token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 403)
