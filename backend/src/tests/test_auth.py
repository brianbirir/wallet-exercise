import unittest
import json
from unittest.mock import patch

from src.main import create_app, db, jwt


class AuthTest(unittest.TestCase):
    def setUp(self):
        app = create_app(config_name="testing")
        app.app_context().push()
        app.testing = True
        self.app = app.test_client(())
        db.create_all()

    def mock_jwt_required(self):
        return

    def test_register_user(self):
        request_data = {
            "first_name": "test name one",
            "last_name": "test name two",
            "username": "fake@example.com",
            "password": "1234567891",
            "telephone": "122222222",
            "role_id": 1,
            "is_disabled": False,
        }

        headers = {"Content-Type": "application/json"}

        auth_registration_response = self.app.post(
            "api/v1/auth/register-user", data=json.dumps(request_data), headers=headers
        )
        response_data = json.loads(auth_registration_response.get_data())
        print(json.loads(auth_registration_response.get_data()))
        self.assertEqual(auth_registration_response.status_code, 200)
        self.assertIn("message", response_data.keys())
        self.assertIn("access_token", response_data.keys())
        self.assertIn("refresh_token", response_data.keys())

    @patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        side_effect=mock_jwt_required,
    )
    def test_invalid_token(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\
            .eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ\
                .SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        headers = {"Authorization": "Bearer " + token}
        param = f"?user_id=1"
        get_user_response = self.app.get(f"api/v1/user{param}")
        self.assertEqual(get_user_response.status_code, 422)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # def test_get_user_details(self):
    #
    #     request_data = {
    #         "first_name": "Brian",
    #         "last_name": "Birir",
    #         "username": "brianbirir@gmail.com",
    #         "password": "1234567891",
    #         "telephone": "0720807242",
    #         "role_id": 1,
    #     }
    #     # login user
    #     login_response = requests.post(
    #         "http://127.0.0.1:5000/api/v1/auth/login",
    #         data=request_data,
    #     )
    #     token = login_response.json()["auth_token"]
    #     headers = {"Authorization": "Bearer " + token}
    #
    #     # get user details
    #     user_response = requests.get("http://127.0.0.1:5000/api/user", headers=headers)
    #     self.assert200(user_response)

    # def test_invalid_token(self):
    #     token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\
    #         .eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ\
    #             .SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    #     headers = {'Authorization': 'Bearer ' + token}
    #     user_response = requests.get(
    #         'http://127.0.0.1:5000/api/user',
    #         headers=headers
    #     )
    #     self.assert403(user_response)
    #
    # def test_expired_token(self):
    #     token = ''
    #     headers = {'Authorization': 'Bearer ' + token}
    #     user_response = requests.get(
    #         'http://127.0.0.1:5000/api/user',
    #         headers=headers
    #     )
    #     self.assert403(user_response)

    if __name__ == "__main__":
        unittest.main()
