"""Sievefilters tests."""

from __future__ import unicode_literals

import mock

from django.core.urlresolvers import reverse

from modoboa.admin import factories as admin_factories
from modoboa.core import models as core_models
from modoboa.lib.tests import ModoTestCase

from . import mocks


class SieveFiltersTestCase(ModoTestCase):
    """Check sieve filters."""

    @classmethod
    def setUpTestData(cls):
        """Create some users."""
        super(SieveFiltersTestCase, cls).setUpTestData()
        admin_factories.populate_database()
        cls.user = core_models.User.objects.get(username="user@test.com")

    def setUp(self):
        """Connect with a simpler user."""
        patcher = mock.patch("sievelib.managesieve.Client")
        self.mock_client = patcher.start()
        self.mock_client.return_value = mocks.ManagesieveClientMock()
        self.addCleanup(patcher.stop)

        patcher = mock.patch("imaplib.IMAP4")
        self.mock_client = patcher.start()
        self.mock_client.return_value = mocks.IMAP4Mock()
        self.addCleanup(patcher.stop)

        url = reverse("core:login")
        data = {
            "username": self.user.username, "password": "toto"
        }
        self.client.post(url, data)

    def test_index(self):
        """Test index view."""
        response = self.client.get(reverse("modoboa_sievefilters:index"))
        self.assertContains(response, "main_script (active)")

    def test_getfs(self):
        """Test getfs view."""
        response = self.ajax_get(
            reverse("modoboa_sievefilters:fs_get", args=["main_script"]))
        self.assertIn(
            "/sfilters/main_script/editfilter/test1/", response["content"])

    def test_toggle_filter_state(self):
        """Test toggle_filter_state view."""
        url = reverse("modoboa_sievefilters:filter_toggle_state",
                      args=["main_script", "test1"])
        response = self.ajax_get(url)
        self.assertEqual(response["color"], "red")
        response = self.ajax_get(url)
        self.assertEqual(response["color"], "green")

    def test_move_filter_up(self):
        """Test move_filter_up view."""
        url = reverse("modoboa_sievefilters:filter_move_up",
                      args=["main_script", "test2"])
        response = self.ajax_get(url)
        pos1 = response["content"].find(
            "/sfilters/main_script/editfilter/test2/")
        pos2 = response["content"].find(
            "/sfilters/main_script/editfilter/test1/")
        self.assertTrue(pos1 < pos2)

    def test_move_filter_down(self):
        """Test move_filter_down view."""
        url = reverse("modoboa_sievefilters:filter_move_down",
                      args=["main_script", "test1"])
        response = self.ajax_get(url)
        pos1 = response["content"].find(
            "/sfilters/main_script/editfilter/test2/")
        pos2 = response["content"].find(
            "/sfilters/main_script/editfilter/test1/")
        self.assertTrue(pos1 < pos2)

    def test_new_filter(self):
        """Test new_filter view."""
        url = reverse("modoboa_sievefilters:filter_add", args=["main_script"])
        response = self.client.get(url)
        self.assertContains(response, "New filter")

    def test_remove_filter(self):
        """Test removefilter view."""
        url = reverse(
            "modoboa_sievefilters:filter_delete",
            args=["second_script", "test1"])
        response = self.ajax_get(url)
        self.assertEqual(response, "Filter removed")

    def test_download_filters_set(self):
        """Test download_filters_set view."""
        url = reverse("modoboa_sievefilters:fs_download", args=["main_script"])
        response = self.client.get(url)
        self.assertEqual(response.content, mocks.SAMPLE_SIEVE_SCRIPT)

    def test_activate_filters_set(self):
        """Test activate_filters_set view."""
        url = reverse(
            "modoboa_sievefilters:fs_activate", args=["second_script"])
        response = self.ajax_get(url)
        self.assertEqual(response["respmsg"], "Filters set activated")

    def test_remove_filters_set(self):
        """Test remove_filters_set view."""
        url = reverse(
            "modoboa_sievefilters:fs_delete", args=["second_script"])
        response = self.ajax_get(url)
        self.assertEqual(response["respmsg"], "Filters set deleted")

    def test_new_filters_set(self):
        """Test new_filters_set view."""
        url = reverse("modoboa_sievefilters:fs_add")
        response = self.client.get(url)
        self.assertContains(response, "Create a new filters set")

        data = {"name": "new_script"}
        response = self.ajax_post(url, data)
        self.assertEqual(response["respmsg"], "Filters set created")

    def test_savefs(self):
        """Test savefs view."""
        url = reverse("modoboa_sievefilters:fs_save", args=["new_script"])
        data = {"scriptcontent": mocks.SAMPLE_SIEVE_SCRIPT}
        response = self.ajax_post(url, data)
        self.assertEqual(response["respmsg"], "Filters set saved")
