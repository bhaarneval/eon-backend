"""
Test for feedback module api added here
"""
import json

from rest_framework.test import APITestCase

from authentication.models import Role, User
from core.models import Event, EventType, Question, UserProfile


class FeedbackQuestionsTestCase(APITestCase):
    """
    Test cases are created in this class
    """
    def setUp(cls):
        """
        Data setup for Feedback Question Unit test cases
        """
        role = Role(role="organizer")
        role.save()

        user = User.objects.create_user(email="user21@gmail.com", password="user123")
        role_obj = Role.objects.get(role="organizer")

        user_profile_obj = UserProfile.objects.create(
            user=user, name="user21@gmail.com", contact_number="9999911111",
            organization="organization", address="Bangalore",
            role=role_obj)
        user_profile_obj.save()
        data = dict(email="user21@gmail.com", password="user123")
        login_response = cls.client.post('/authentication/login', json.dumps(data),
                                         content_type='application/json')
        cls.user_id = login_response.data['data']['user']['user_id']
        cls.token = login_response.data['data']['access']
        cls.end_point = "/core/feedback-questions/"
        cls.question = Question(question="Demo question1 ?")
        cls.question.save()

    def test_feedback_questions_api_with_wrong_method_type(self):
        """
        Unit test for feedback question get api with wrong method
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_feedback_questions_api_with_wrong_token(self):
        """
        Unit test for feedback question get api with wrong token
        """
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format('token')
        )
        self.assertEquals(response.status_code, 401)

    def test_get_api_for_feedback_questions(self):
        """
        Unit test for feedback question get api with correct method and token
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 200)


class FeedbackTestCase(APITestCase):
    """
    Test cases are created in this class
    """

    def setUp(cls):
        """
        Data setup for Feedback Unit test cases
        """
        role = Role(role="organizer")
        role.save()
        role2 = Role(role="subscriber")
        role2.save()

        user = User.objects.create_user(email="user21@gmail.com", password="user123")
        role_obj = Role.objects.get(role="organizer")

        user_profile_obj = UserProfile.objects.create(
            user=user, name="user21@gmail.com", contact_number="9999911111",
            organization="organization", address="Bangalore",
            role=role_obj)
        user_profile_obj.save()

        content2 = {
            "email": "user20@gmail.com",
            "name": "user20@gmail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
            "organization": "Eventhigh"
        }

        cls.client.post('/authentication/registration', json.dumps(content2),
                        content_type='application/json')
        data = dict(email="user20@gmail.com", password="user123")
        login_response = cls.client.post('/authentication/login', json.dumps(data),
                                         content_type='application/json')
        cls.user_id = login_response.data['data']['user']['user_id']
        cls.token = login_response.data['data']['access']
        cls.end_point = "/core/feedback/"

        cls.event_type = EventType(type="test")
        cls.event_type.save()

        cls.event = Event(name="test_event", type=cls.event_type, description="New Event",
                          date="2020-04-02",
                          time="12:38:00", location="karnal", subscription_fee=499,
                          no_of_tickets=250,
                          images="https://www.google.com/images", sold_tickets=0,
                          external_links="google.com",
                          event_created_by_id=User.objects.filter()[0].id)
        cls.event.save()
        cls.question = Question(question="Demo question1 ?")
        cls.question.save()

    def test_feedback_api_with_wrong_method_type(self):
        """
        Unit test for feedback get api with wrong method
        """
        data = dict(email="user20@gmail.com", password="user123")
        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        token = login_response.data['data']['access']
        response = self.client.put(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(token)
        )
        self.assertEquals(response.status_code, 405)

    def test_feedback_api_with_wrong_token(self):
        """
        Unit test for feedback get api with wrong token
        """
        response = self.client.get(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format('token')
        )
        self.assertEquals(response.status_code, 401)

    def test_feedback_post_api_with_no_question_id(self):
        """
        Unit test for feedback post api with no question id
        """
        json_content = {
            "event_id": self.event.id,
            "feedback": [{
                "answer": {
                    "description": "abcd",
                    "image": "demo.jpeg"
                }
            }]
        }
        response = self.client.post(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            data=json.dumps(json_content),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 400)

    def test_feedback_post_api_with_wrong_question_id(self):
        """
        Unit test for feedback post api with wrong question id
        """
        json_content = {
            "event_id": self.event.id,
            "feedback": [{
                "id": 1000,
                "answer": {
                    "description": "abcd",
                    "image": "demo.jpeg"
                }
            }]
        }
        response = self.client.post(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            data=json.dumps(json_content),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 400)

    def test_feedback_post_api_with_correct_data(self):
        """
        Unit test for feedback post with correct data
        """

        json_content = {
            "event_id": self.event.id,
            "feedback": [{
                "id": self.question.id,
                "answer": {
                    "description": "abcd",
                    "image": "demo.jpeg"
                }
            }]
        }
        response = self.client.post(
            self.end_point, HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            data=json.dumps(json_content),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 200)

    def test_feedback_get_api_with_subscriber_login(self):
        """
        Unit test for feedback get api for subscriber
        """
        response = self.client.get(
            self.end_point + '?event_id={}'.format(self.event.id),
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 200)

    def test_feedback_get_api_with_organizer_login(self):
        """
        Unit test for feedback get api for organizer
        """
        data = dict(email="user21@gmail.com", password="user123")
        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        self.token = login_response.data['data']['access']
        response = self.client.get(
            self.end_point + '?event_id={}'.format(self.event.id),
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 200)

    def test_feedback_get_api_with_no_event_in_parameter(self):
        """
        Unit test for feedback get api with no event
        """
        response = self.client.get(
            self.end_point,
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 400)

    def test_feedback_get_api_with_wrong_event(self):
        """
        Unit test for feedback get api with wrong event id
        """
        response = self.client.get(
            self.end_point + '?event_id={}'.format(100),
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 400)

    def test_feedback_get_api_with_correct_event(self):
        """
        Unit test for feedback get api with correct event id
        """
        response = self.client.get(
            self.end_point + '?event_id={}'.format(self.event.id),
            HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 200)
