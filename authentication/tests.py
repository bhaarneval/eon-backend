"""
Write test cases for authentication module here
"""

import json

from django.test import TestCase

from authentication.models import Role, VerificationCode


class AuthenticationTestCase(TestCase):
    """
    Authentication methods test cases are added in this class
    """

    def setUp(cls):
        """
        Data setup for Authentication Unit test cases
        """
        Role.objects.create(role='subscriber')
        Role.objects.create(role="organizer")
        content = {
            "email": "user123@mail.com",
            "name": "user_test",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "subscriber",
            "organization": "Eventhigh"
        }
        cls.register = cls.client.post('/authentication/registration', json.dumps(content),
                                       content_type='application/json')

    def test_register_user_with_complete_details(self):
        """
        Unit test for register user with complete details
        """
        self.assertEqual(self.register.status_code, 201)

    def test_register_user_without_password(self):
        """
        Unit test for register user without password
        """

        # Setup
        content = {
            "email": "user123@mail.com",
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

    def test_register_user_with_role_as_organizer(self):
        """
        Unit test for register user with role as organizer
        """

        # Setup
        content = {
            "email": "user1@mail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh",
            "testing": True
        }

        # Run
        register = self.client.post('/authentication/registration', json.dumps(content),
                                    content_type='application/json')

        # Check
        self.assertEqual(register.status_code, 201)

    def test_user_login_with_valid_credentials(self):
        """
        Unit test for login with valid credential
        """

        register_user_id = self.register.data['data']['user']['user_id']

        data = dict(email='user123@mail.com', password="user123")

        # Run

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        login_user_id = login_response.data['data']['user']['user_id']

        # Check
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_user_id, register_user_id)

    def test_user_login_with_invalid_credentials(self):
        """
        Unit test for login with wrong credential
        """

        # Setup

        data = dict(email='user123@mail.com', password="user1234")

        # Run

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')

        # Check
        self.assertEqual(login_response.status_code, 400)

    def test_for_change_user_password_with_valid_credentials(self):
        """
        Unit test for change password for existing user with valid credential
        """

        pay_load = {'email': 'user123@mail.com', 'old_password': 'user123', 'new_password': 'user1234'}
        data = dict(email='user123@mail.com', password="user123")

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
        Unit test for change password for existing user with wrong password
        """
        # Setup
        pay_load = {'email': 'user123@mail.com', 'old_password': 'user1', 'new_password': 'user1234'}
        data = dict(email='user123@mail.com', password="user123")

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
        Unit test to check reset password api with invalid code
        """
        data = dict(email='user123@mail.com', code="code")
        verification_code = VerificationCode(email="user123@mail.com", code=1234)
        verification_code.save()

        # Run
        reset_response = self.client.post('/authentication/reset-password', json.dumps(data),
                                          content_type='application/json')
        # Check
        self.assertEqual(reset_response.status_code, 400)

    def test_reset_password_with_valid_code(self):
        """
        Unit test to check reset password api with valid code
        """
        verification_code = VerificationCode(email='user123@mail.com', code='1234')
        verification_code.save()

        data = dict(email='user123@mail.com', code="1234")

        # Run
        reset_response = self.client.post('/authentication/reset-password', json.dumps(data),
                                          content_type='application/json')
        # Check

        self.assertEqual(reset_response.status_code, 200)

    def test_for_send_forget_password_mail_for_wrong_user(self):
        """
        Unit test to check send forget password mail api with wrong user
        """

        # setup
        data = dict(email='user@mail.com', testing=True)

        # Run
        code_response = self.client.post('/authentication/generate-code', json.dumps(data),
                                         content_type='application/json')

        # Check
        self.assertEqual(code_response.status_code, 400)

    def test_for_change_user_password_with_same_old_and_new_password(self):
        """
        Unit test for change password for existing user with same old and new password
        """

        pay_load = {'email': 'user123@mail.com', 'old_password': 'user123', 'new_password': 'user123'}
        data = dict(email='user123@mail.com', password="user123")

        login_response = self.client.post('/authentication/login', json.dumps(data),
                                          content_type='application/json')
        token = login_response.data['data']['access']
        # Run

        response = self.client.post('/authentication/change-password', json.dumps(pay_load),
                                    HTTP_AUTHORIZATION="Bearer {}".format(token),
                                    content_type='application/json')

        # check
        self.assertEqual(response.status_code, 400)

    def test_for_old_password_when_sending_multiple_request(self):
        """
         Unit test for old verification code with send multiple request
        """
        verification_code = VerificationCode(email='user123@mail.com', code='0000')
        verification_code.save()

        data = dict(email='user123@mail.com', testing=True)

        # Run
        self.client.post('/authentication/generate-code', json.dumps(data),
                         content_type='application/json')
        rest_data = dict(email='user123@mail.com', code="0000")
        reset_response = self.client.post('/authentication/reset-password', json.dumps(rest_data),
                                          content_type='application/json')

        self.assertEqual(reset_response.status_code, 400)
