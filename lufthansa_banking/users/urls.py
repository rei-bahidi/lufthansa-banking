from django.urls import path
from .views import Users

urlpatterns = [
    path('list/', Users.as_view()),  # Link the function-based view to a URL
]