from django.test import TestCase

import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_homepage(client):
    assert True