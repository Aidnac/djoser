from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from djet import assertions, restframework, utils
from rest_framework import status
import djoser.views

from .common import create_user


class UserViewTest(restframework.APIViewTestCase,
                   assertions.EmailAssertionsMixin,
                   assertions.StatusCodeAssertionsMixin):
    view_class = djoser.views.UserView

    def test_get_should_return_user(self):
        user = create_user()
        request = self.factory.get(user=user)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(
            [get_user_model().USERNAME_FIELD, get_user_model()._meta.pk.name] + get_user_model().REQUIRED_FIELDS
        ))

    def test_put_should_update_user(self):
        user = create_user()
        data = {
            'email': 'ringo@beatles.com',
        }
        request = self.factory.put(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        user = utils.refresh(user)
        self.assertEqual(data['email'], user.email)

    @override_settings(DJOSER=dict(settings.DJOSER, **{'SEND_ACTIVATION_EMAIL': True}))
    def test_put_should_update_user_email_and_send_activation_email(self):
        user = create_user()
        data = {
            'email': 'ringo@beatles.com',
        }
        request = self.factory.put(user=user, data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[data['email']])

        user = get_user_model().objects.get(username='john')
        self.assertFalse(user.is_active)
