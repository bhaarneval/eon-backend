"""
Event related test cases are added here
"""
import json

from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import Event, EventType, UserProfile


class EventAPITest(APITestCase):
    """
    Event methods test cases are added in this class
    """

    def setUp(cls):
        """
        Data setup for Event Unit test cases
        """

        role = Role(role="organizer")
        role.save()
        role2 = Role(role="subscriber")
        role2.save()

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
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com",
                          event_created_by_id=cls.user_id)
        cls.event.save()

        subscriber_data = {
            "email": "user20@gmail.com",
            "name": "user20@gmail.com",
            "password": "user1234",
            "contact": "9999911112",
            "address": "Rishikesh",
            "role": "subscriber",
            "organization": "Rockers"
        }
        data2 = dict(email="user20@gmail.com", password="user1234")
        cls.client.post('/authentication/registration', json.dumps(subscriber_data), content_type='application/json')
        login_response2 = cls.client.post('/authentication/login', json.dumps(data2),
                                          content_type='application/json')
        cls.user_id2 = login_response2.data['data']['user']['user_id']
        cls.token2 = login_response2.data['data']['access']

    def test_event_post(self):
        """
        Unit test for event creation api by the same organizer
        """
        # Setup

        json_content = {
            "name": "Diwali",
            "event_type": self.event_type.id,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38:00",
            "location": "mumbai",
            "images": "https://www.google.com/images",
            "subscription_fee": 499,
            "no_of_tickets": 200,
            "event_created_by": self.user_id
        }

        # Run
        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], json_content['name'])
        self.assertEqual(response.data['description'], json_content['description'])
        self.assertEqual(response.data['date'], json_content['date'])
        self.assertEqual(response.data['location'], json_content['location'])
        self.assertEqual(response.data['subscription_fee'], json_content['subscription_fee'])
        self.assertEqual(response.data['event_created_by'], self.user_id)

    def test_event_post_with_invalid_event_type_id(self):
        """
        Unit test for event post api with invalid event id
        """
        # Setup

        json_content = {
            "name": "Diwali",
            "event_type": 1000,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38:00",
            "location": "mumbai",
            "images": "https://www.google.com/images",
            "subscription_fee": 499,
            "no_of_tickets": 200,
            "event_created_by": self.user_id
        }

        # Run

        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_event_get_without_parameter(self):
        """
        Unit test for event get api without any parameter
        """

        # Run
        response = self.client.get("/core/event/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_with_parameter_event_id(self):
        """
        Unit test cases for event get api for particular event
        """
        # Setup
        event_id = self.event.id

        # Run
        response = self.client.get("/core/event/?event_id={id}".format(id=event_id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_type_get_api_with_valid_data(self):
        """
        Unit test for event type get api
        """
        # Run
        response = self.client.get("/core/event-type",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_delete_api_with_valid_data(self):
        """
        Unit test for event delete api with valid event id
        """
        # Setup
        event_id = self.event.id
        json_content = {
            "message": "TESTING",
            "testing": True
        }

        # Run
        response = self.client.delete("/core/event/{event_id}/".format(event_id=event_id),
                                      data=json.dumps(json_content),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_delete_api_with_invalid_event_id(self):
        """
        Unit test for event delete api with invalid event id
        """
        # Setup
        event_id = 5

        # Run
        response = self.client.delete("/core/event/{event_id}/".format(event_id=event_id),
                                      HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                      content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 400)

    def test_event_patch_api_with_valid_event_id(self):
        """
        Unit test for event update api with valid event id
        """
        # Setup
        event_id = self.event.id

        data = {
            "name": "Holi",
            "event_type": self.event_type.id,
            "date": "2020-04-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38",
            "location": "Giridih",
            "subscription_fee": 499,
            "no_of_tickets": 200,
            "testing": True
        }

        # Run
        response = self.client.patch("/core/event/{event_id}/".format(event_id=event_id),
                                     json.dumps(data),
                                     HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                     content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_retrieve_api_with_invalid_event_id(self):
        """
        Unit test for event get api with invalid event id
        """

        # Run
        response = self.client.get("/core/event/100/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 400)

    def test_event_retrieve_api_with_valid_event_id(self):
        """
        Unit test for event get api with valid event id
        """

        # Run
        response = self.client.get("/core/event/{id}/".format(id=self.event.id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_for_pre_signed_url_get_api_without_event_id(self):
        """
        Unit test for pre signed url get api without event id
        """
        # Run
        response = self.client.get("/core/presigned-url/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_for_pre_signed_url_get_api_with_invalid_event_id(self):
        """
        Unit test for pre signed url get api with invalid event id
        """
        # Run
        response = self.client.get("/core/presigned-url/", {'event_id': 100},
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_for_pre_signed_url_get_api_with_valid_event_id(self):
        """
        Unit test for pre signed url get api with valid event id
        """

        # Run
        response = self.client.get("/core/presigned-url/", {'event_id': self.event.id},
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_wish_listed_parameter(self):
        """
        Unit test for event get api for wish listed events
        """

        # Run
        response = self.client.get("/core/event/?is_wishlisted=True",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_subscription_type_free_parameter(self):
        """
        Unit test for event get api for free events
        """

        # Run
        response = self.client.get("/core/event/?subscription_type=free",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_subscription_type_paid_parameter(self):
        """
        Unit test for event get api for paid events
        """

        # Run
        response = self.client.get("/core/event/?subscription_type=paid",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_subscription_type_and_event_status_parameter(self):
        """
        Unit test for event get api for paid and upcoming events
        """

        # Run
        response = self.client.get("/core/event/?subscription_type=paid&event_status=upcoming",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_subscriber_login(self):
        """
        Unit test for event get api for subscriber
        """
        # Run
        response = self.client.get("/core/event/",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token2),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_get_api_for_particular_event_subscriber_login(self):
        """
        Unit test case for event with valid event id for subscriber
        """
        # Run
        response = self.client.get("/core/event/{}/".format(self.event.id),
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token2),
                                   content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_cancelled_event(self):
        """
        Unit test for event get api for cancelled events
        """

        # Run
        response = self.client.get("/core/event/?event_status=cancelled",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_completed_event(self):
        """
        Unit test for event get api for completed events
        """

        # Run
        response = self.client.get("/core/event/?event_status=completed",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_all_event(self):
        """
        Unit test for event get api for all events
        """

        # Run
        response = self.client.get("/core/event/?event_status=all",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        # Check
        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_text_search(self):
        """
        Unit test for event get api for search location or name
        """

        response = self.client.get("/core/event/?search=test",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_event_type(self):
        """
        Unit test for event get api for event type
        """

        response = self.client.get("/core/event/?event_type=1",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_event_created_by(self):
        """
        Unit test for event get api for event created by
        """

        response = self.client.get("/core/event/?event_created_by=True",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_event_get_api_for_date_range(self):
        """
        Unit test for event get api for event date range
        """

        response = self.client.get("/core/event/?start_date=2020-04-01&end_date=2020-05-01",
                                   HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_event_creation_by_passing_different_user_id(self):
        """
        Unit test for event post api with passing different user id
        """
        # Setup

        json_content = {
            "name": "NEW",
            "event_type": self.event_type.id,
            "date": "2020-05-09",
            "description": "New Event",
            "external_links": "google.com",
            "time": "12:38:00",
            "location": "Bangalore",
            "images": "https://www.google.com/images",
            "subscription_fee": 500,
            "no_of_tickets": 200,
            "event_created_by": 5
        }

        # Run
        response = self.client.post("/core/event/", data=json.dumps(json_content),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        #  Check
        self.assertEqual(response.status_code, 400)

    def test_pre_signed_url_post_api(self):
        """
        Unit test for pre signed url post api
        """
        data = {
            "path_name": "abc.png"
        }
        response = self.client.post("/core/presigned-url/", json.dumps(data),
                                    HTTP_AUTHORIZATION="Bearer {}".format(self.token),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
