from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_homopage(client):
    assert True