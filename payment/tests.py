import json
from rest_framework.test import APITestCase

# Create your tests here.


class PaymentAPITest(APITestCase):
    fixtures = ["default.json"]

    def setUp(cls):
        data = dict(email="user2@gmail.com", password="Password")
        cls.user = cls.client.post('/authentication/login', json.dumps(data), content_type='application/json')
        cls.token = cls.user.data['data']['access']
        cls.ENDPOINT = "/payment/"

    def test_payment_api_with_wrong_method(self):
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format(self.token)
        )
        self.assertEquals(response.status_code, 405)

    def test_payment_api_with_wrong_token(self):
        response = self.client.get(
            self.ENDPOINT, HTTP_AUTHORIZATION="Bearer {}".format("wrong token")
        )
        self.assertEquals(response.status_code, 401)

    def test_payment_api_without_passing_required_fields(self):
        """Required fields are
                    1. card_number
                    2. expiry_year
                    3. expiry_month
                    4. amount
                    5. discount_amount
        """
        data = {"card_number": 5039303342356004,
                "expiry_year": 2022,
                "expiry_month": 7}
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_wrong_length_of_card_number(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year
                    3. expiry_month
                    4. amount
                    5. discount_amount
        """
        data = {
                "card_number": 50393033423,
                "expiry_year": 2022,
                "expiry_month": 7,
                "amount": 4000,
                "discount_amount": 300
            }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_passing_string_as_card_number(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year
                    3. expiry_month
                    4. amount
                    5. discount_amount
        """
        data = {
                "card_number": "INVALID CARD",
                "expiry_year": 2022,
                "expiry_month": 7,
                "amount": 4000,
                "discount_amount": 300
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_wrong_exiry_date(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year (greater or equal current year)
                    3. expiry_month (if year is same as current year then month should be greater than current month)
                    4. amount
                    5. discount_amount
        """
        data = {
                "card_number": "INVALID CARD",
                "expiry_year": 2020,
                "expiry_month": 1,
                "amount": 4000,
                "discount_amount": 300
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 400)

    def test_payment_api_with_valid_input_fields(self):
        """Required fields are
                    1. card_number (length=16)
                    2. expiry_year (greater or equal current year)
                    3. expiry_month (if year is same as current year then month should be greater than current month)
                    4. amount
                    5. discount_amount
        """
        data = {
                "card_number": 5039303342356004,
                "expiry_year": 2020,
                "expiry_month": 8,
                "amount": 4000,
                "discount_amount": 300
                }
        response = self.client.post(
            self.ENDPOINT, json.dumps(data), HTTP_AUTHORIZATION="Bearer {}".format(self.token),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, 200)
