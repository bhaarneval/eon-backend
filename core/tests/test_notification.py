from django.test import TestCase

from authentication.models import User
from core.models import Event, EventType, Notification


# Create your tests here.


class NotificationTestCase(TestCase):

    def test_notification_api_patch_for_valid_data(self):
        """
          Test for updated notification status has_read false to true

        """

        # Setup
        user = User.objects.create_user(email="usertest@mail.com", password="password")
        user_id = User.objects.only('id').get(email='usertest@mail.com').id

        event_type = EventType(type="test")
        event_type.save()

        json_content = {"notification_id": [1]}

        event = Event(name="test_event", type=event_type, description="New Event", date="2020-04-02",
                      time="12:38:00", location="karnal", subscription_fee=499, no_of_tickets=250,
                      images="https://www.google.com/images", sold_tickets=2, external_links="google.com",
                      event_created_by_id=user_id)
        event.save()

        notification = Notification(user=user, event=event, message="test message", has_read=False)
        notification.save()

        expected_response = {'message': 'Unread notification updated successfully'}

        # Run
        response = self.client.patch("/core/notification/", data=json_content, content_type="application/json")

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, expected_response)

    def test_notification_api_patch_for_invalid_data(self):
        """
          Test for updated notification status has_read false to true

        """

        # Setup

        json_content = {"notification_id": []}

        expected_response = {'message': "Notification Id list can not be Null"}

        # Run
        response = self.client.patch("/core/notification/", data=json_content, content_type="application/json")

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_response)

    def test_for_Notification_get(self):
        """
          Test for notification when there is no unread notification for a user

        """

        # Setup

        json_content = {
            "user_id": 1
        }

        # Run
        response = self.client.get("/core/notification/", json_content, content_type="application/json")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'], [])

    def test_for_Notification_get(self):
        """
          Test for notification when there is unread notification for a user

        """

        # Setup
        user = User.objects.create_user(email="usertest@mail.com", password="password")
        user_id = User.objects.only('id').get(email='usertest@mail.com').id

        event_type = EventType(type="test")
        event_type.save()

        json_content = {"notification_id": [1]}

        event = Event(name="test_event", type=event_type, description="New Event", date="2020-04-02",
                      time="12:38:00", location="karnal", subscription_fee=499, no_of_tickets=250,
                      images="https://www.google.com/images", sold_tickets=2, external_links="google.com",
                      event_created_by_id=user_id)
        event.save()

        notification = Notification(user=user, event=event, message="test message", has_read=False)
        notification.save()

        json_content = {
            "user_id": user_id
        }

        # Run
        response = self.client.get("/core/notification/", json_content, content_type="application/json")

        # Assert
        self.assertEqual(response.data['data'][0]['message'], notification.message)
        self.assertEqual(response.data['data'][0]['notification_id'], notification.id)
