"""
Notification module test cases are added here
"""
import json

from django.test import TestCase

from authentication.models import User, Role
from core.models import Event, EventType, Notification


# Create your tests here.

class NotificationTestCase(TestCase):
    """
    Notification methods test cases are added in this class
    """

    def setUp(cls):
        role = Role(role="subscriber")
        role.save()
        content = {
            "email": "usertest@gmail.com",
            "name": "user test",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
            "organization": "Eventhigh"
        }

        response = cls.client.post('/authentication/registration', json.dumps(content),
                                   content_type='application/json')

        cls.user_id = response.data['data']['user']['user_id']
        cls.token = response.data['data']['access']
        cls.user = User.objects.get(id=cls.user_id)

        event_type = EventType(type="test")
        event_type.save()

        cls.event = Event(name="test_event", type=event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=500,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

    def test_notification_api_patch_for_valid_data(self):
        """
        Unit test for notification patch api with valid data
        """

        # Setup
        json_content = {"notification_ids": [1]}
        notification = Notification(user=self.user, event=self.event,
                                    message="test message", has_read=False)
        notification.save()

        # Run
        response = self.client.patch("/core/notification/", data=json_content,
                                     content_type="application/json",
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token))

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_notification_api_patch_for_empty_list_of_notification_id(self):
        """
        Unit test for notification patch api for empty notification id
        """

        # Setup
        json_content = {"notification_ids": []}

        # Run
        response = self.client.patch("/core/notification/", data=json_content,
                                     content_type="application/json",
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token))

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_for_notification_get_when_no_unread_notification_for_that_user(self):
        """
        Unit test for notification get api for no unread notification
        """

        # Setup
        notification = Notification(user=self.user, event=self.event,
                                    message="test message", has_read=True)
        notification.save()

        # Run
        response = self.client.get("/core/notification/", content_type="application/json",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'], [])

    def test_for_notification_get_data_when_unread_notification(self):
        """
        Unit test for notification get api for unread notification
        """

        # Setup
        notification = Notification(user=self.user, event=self.event,
                                    message="test message", has_read=False)
        notification.save()

        # Run
        response = self.client.get("/core/notification/", content_type="application/json",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token))

        # Assert
        self.assertEqual(response.data['data'][0]['message'], notification.message)
        self.assertEqual(response.data['data'][0]['id'], notification.id)
