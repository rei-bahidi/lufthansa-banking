from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns 
from .views import UserListView, UserView

urlpatterns = [
    path('customers/list/', UserListView.as_view(), name='user-list'),
    path('customers/detail/<int:user_id>/', UserView.as_view(), name='user-detail'), 
]

urlpatterns = format_suffix_patterns(urlpatterns)
