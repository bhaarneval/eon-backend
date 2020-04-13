"""
Test cases for wish list api method are added here
"""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import Event, EventType, WishList


class WishListAPITest(APITestCase):
    """
    Unit test for api methods are added in this class
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
                          images="https://www.google.com/images", sold_tickets=2,
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

    def test_wish_list_post_api_with_valid_event_id(self):
        """
        Unit test for Wish list post Api
        :return:
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
        Unit test for Wish list post Api
        :return:
        """
        # Setup

        json_content = {
            "event_id": 6
        }

        # Run
        response = self.client.post("/core/wishlist/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 400)

    def test_wish_list_delete_api_with_invalid_event_id(self):
        """
        Unit test for Wish list delete Api
        :return:
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
        Unit test for Wish list delete Api
        :return:
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
