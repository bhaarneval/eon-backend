"""
Write test cases for authentication module here
"""

import json

from django.test import TestCase

from authentication.models import Role


class AuthenticationTestCase(TestCase):
    """
    Authentication Test Case Started from Here
    """

    def setUp(cls):
        Role.objects.create(role='organizer')
        content = {
            "email": "user@mail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }
        cls.register = cls.client.post('/authentication/registration', json.dumps(content),
                                       content_type='application/json')

    def test_register_user_with_complete_details(self):
        """
         Test: unit test for register a user with complete information
               mocked the user detail and call the register api.

        """
        self.assertEqual(self.register.status_code, 201)

    def test_register_user_without_password(self):
        """
         Test: unit test for register a user with incomplete information
               mocked the user detail and call the register api.

        """

        # Setup
        content = {
            "email": "user@mail.com",
            # "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }

        # Run
        register = self.client.post('/authentication/registration', json.dumps(content),
                                    content_type='application/json')

        # Check
        self.assertEqual(register.status_code, 400)
        self.assertEqual(register.data['message'],
                         'Incomplete or Incorrect Credentials are provided for registration')

    def test_user_login_with_valid_credentials(self):
        """
        TEST: Unit test for user login with valid credential,
              Mocked the user detail and call the login api
              Getting the response status = 200 and user_id
        """

        data = dict(email='user@mail.com', password="user123")
        register_user_id = self.register.data['data']['user']['user_id']

        # Run

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        login_user_id = login_response.data['data']['user']['user_id']

        # Check
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_user_id, register_user_id)

    def test_user_login_with_invalid_credentials(self):
        """
        TEST: Unit test for user login with valid credential,
              Mocked the user detail and call the login api
              Getting the response status = 200 and user_id
        """

        # Setup

        data = dict(email='user@mail.com', password="user1234")

        # Run

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')

        # Check
        self.assertEqual(login_response.status_code, 400)

    def test_for_change_user_password_with_valid_credentials(self):
        """
        Unit Test for change password for existing user

        """

        pay_load = {'email': 'user@mail.com', 'old_password': 'user123', 'new_password': 'user1234'}
        data = dict(email='user@mail.com', password="user123")

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        token = login_response.data['data']['access']
        # Run

        response = self.client.post('/authentication/change-password', json.dumps(pay_load),
                                    HTTP_AUTHORIZATION="Bearer {}".format(token),
                                    content_type='application/json')

        # check
        self.assertEqual(response.status_code, 200)

    def test_for_change_user_password_with_wrong_password(self):
        """
        Unit Test for change password for existing user

        """
        # Setup
        pay_load = {'email': 'user@mail.com', 'old_password': 'user1', 'new_password': 'user1234'}
        data = dict(email='user@mail.com', password="user123")

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        token = login_response.data['data']['access']

        # Run
        response = self.client.post('/authentication/change-password', json.dumps(pay_load),
                                    HTTP_AUTHORIZATION="Bearer {}".format(token),
                                    content_type='application/json')

        # check
        self.assertEqual(response.status_code, 400)

    def test_reset_password_with_invalid_code(self):
        """
        Unit test to check reset_password API with invalid code
        :return:
        """
        data = dict(email='user@mail.com', password="user1234", code="code")

        # Run
        reset_response = self.client.post('/authentication/reset-password', json.dumps(data),
                                          content_type='application/json')
        # Check

        self.assertEqual(reset_response.status_code, 400)

    def test_reset_password_with_valid_code(self):
        """
        Unit test to check reset_password API with valid code
        :return:
        """
        verification_code = VerificationCode(email='user@mail.com', code='1234')
        verification_code.save()

        data = dict(email='user@mail.com', password="user1234", code="1234")

        # Run
        reset_response = self.client.post('/authentication/reset-password', json.dumps(data),
                                          content_type='application/json')
        # Check

        self.assertEqual(reset_response.status_code, 200)

    def test_for_send_forget_password_mail_for_wrong_user(self):
        """
            Unit test to check send_forget_password_mail API with wrong user
            :return:
        """

        # setup
        data = dict(email='user123@mail.com', password="user1234", code="1234")

        # Run
        reset_response = self.client.post('/authentication/generate-code', json.dumps(data),
                                          content_type='application/json')

        # Check
        self.assertEqual(reset_response.status_code, 400)

    def test_for_send_forget_password_mail_api_for_valid_user(self):
        """
            Unit test for sending email verification code
            :return: status: 500
            trying to send email but fail
        """

        # setup
        data = dict(email='user@mail.com', password="user1234", code="1234")

        # Run
        reset_response = self.client.post('/authentication/generate-code', json.dumps(data),
                                          content_type='application/json')

        # Check
        self.assertEqual(reset_response.status_code, 500)
