import json
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from authentication.models import Role, Status, User


class AuthenticationTestCase(TestCase):

    def _submit_request(self, view_name, method='POST', raw_json=None,
                        view_kwargs=None, getargs=None, header=None, reverse_url=False):
        """Submits a request to the client running inside the test engine.

        :param view_name: the reverse-lookup name for the view to submit the
        request against
        :param method: HTTP request method (e.g. 'POST', 'GET')
        :param raw_json: raw json string to submit to the view
        :param view_kwargs: any keyword arguments for reversing the view lookup
        to get the URL
        :param getargs: arguments to be appended to GET URLS
        (must be preformatted, e.g.: "foo=bar&baz=bat")
        :return: dictionary which is the deserialized JSON response
        """
        url = reverse(view_name, kwargs=view_kwargs)
        if method == 'POST':
            response = self.client.post(url, raw_json,
                                        content_type="application/json")
        elif method == 'PUT':
            response = self.client.put(url, raw_json,
                                       content_type="application/json")
        elif method == 'GET':
            if getargs is not None:
                url += '?%s' % getargs
            response = self.client.get(url, content_type="application/json")
        else:
            raise RuntimeError("unsupported method: %s" % method)

        result = json.loads(response.content)

        return result

    def test_register_user_with_complete_details(self):
        """
         Test: unit test for register a user with complete information
               mocked the user detail and call the register api.

        """

        # Setup
        Role.objects.create(role='organizer')
        Status.objects.create(status='active')
        content = {
            "email": "user@mail.com",
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": "Eventhigh"
        }

        # Run
        response = self._submit_request('registration', raw_json=content)

        # Check
        self.assertEqual(response['status'], 201)
        self.assertEqual(response['message'], 'User created successfully')

    def test_register_user_without_complete_details(self):
        """
         Test: unit test for register a user with incomplete information

        """

        # Setup
        Role.objects.create(role='organizer')
        Status.objects.create(status='active')
        content = {
            "password": "user123",
            "contact": "9999911111",
            "address": "Bangalore",
            "role": "organizer",
            "organization": None
        }
        expected_response = {"message": "Complete details are not provided", "status": 400}

        # Run
        response = self._submit_request('registration', raw_json=content)

        # Check
        self.assertEqual(response, expected_response)

    def test_user_login_with_valid_credentials(self):
        """
        TEST: Unit test for user login with valid credential,
              Mocked the user detail and call the login api
              Getting the response status = 200 and user_id
        """

        # Setup
        User.objects.create_user(email='email@mail.com', password='password')

        # Run
        response = self._submit_request('login', raw_json={"email": 'email@mail.com',
                                                           "password": 'password'})
        user_id = User.objects.only('id').get(email='email@mail.com').id

        # Check
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['data']['user_id'], user_id)

    def test_user_login_with_invalid_credentials(self):
        """
        TEST: Unit test for user login with invalid credential,
              Mocked the user detail and call the login api with wrong_password
             Getting the expected_response with status 400 and message "Given Credentials does not matches with any registered user"
        """
        # SetUp
        User.objects.create_user(email='email@mail.com', password='password')
        expected_response = {"message": "Given Credentials does not matches with any registered user", "status": 400}

        # Run
        response = self._submit_request('login', raw_json={"email": 'email@mail.com',
                                                           "password": 'wrong_password'})

        # Check
        self.assertEqual(response, expected_response)

    def test_for_change_user_password_with_valid_credentials(self):

        """
        Unit Test for change password for existing user

        """
        # Setup
        pay_load = {'email': 'email@mail.com', 'old_password': 'old_password', 'new_password': 'new_password'}
        User.objects.create_user(email='email@mail.com', password='old_password')
        expected_response = {'message': 'Password updated successfully', 'status': 200}

        # Run
        response = self._submit_request('change-password', raw_json=pay_load)

        # check
        self.assertEqual(response, expected_response)

    def test_for_change_user_password_with_invalid_credentials(self):

        """
        Unit Test for change password for existing user

        """
        # Setup
        pay_load = {'email': 'email@mail.com', 'old_password': 'old_password', 'new_password': 'new_password'}
        User.objects.create_user(email='email@mail.com', password='password')
        expected_response = {'message': 'Given Credentials does not matches with any registered user', 'status': 400}

        # Run
        response = self._submit_request('change-password', raw_json=pay_load)

        # check
        self.assertEqual(response, expected_response)

    def test_for_change_user_password_without_complete_information(self):

        """
        Unit Test for change password for existing user

        """
        # Setup
        pay_load = {'email': 'email@mail.com', 'old_password': None, 'new_password': 'new_password'}
        User.objects.create_user(email='email@mail.com', password='password')
        expected_response = {'message': 'No field can be left blank', 'status': 400}

        # Run
        response = self._submit_request('change-password', raw_json=pay_load)

        # check
        self.assertEqual(response, expected_response)

    def test_reset_password(self):
        """
        Unit test to check reset_password API
        :return:
        """
        old_password = "password"
        new_password = "new_password"
        # Setup
        User.objects.create_user(email='email@mail.com', password='password')

        # Run
        reset_response = self._submit_request('reset-password', raw_json={"email": 'email@mail.com', "password": new_password})
        self.assertEqual(reset_response['status'], 200)

        # login with changed password should be successful
        login_response_with_new_password = \
            self._submit_request('login', raw_json={"email": 'email@mail.com',"password": new_password})

        self.assertEqual(login_response_with_new_password['status'], 200)

        # login won't be successful with old password
        login_response_with_old_password = \
            self._submit_request('login', raw_json={"email": 'email@mail.com',"password": old_password})
        self.assertEqual(login_response_with_old_password['message'],
                         "Given Credentials does not matches with any registered user")
        self.assertEqual(login_response_with_old_password['status'], 400)



