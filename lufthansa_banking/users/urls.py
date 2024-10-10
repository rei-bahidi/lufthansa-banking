from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns 
from .views import UserListView, UserView

urlpatterns = [
    # path('customers/', UserListView.as_view(), name='user-create'),  
    path('customers/list/', UserListView.as_view(), name='user-list'),
    path('customers/delete/<int:user_id>/', UserView.as_view(), name='user-delete'), 
    path('customers/detail/<int:user_id>/', UserView.as_view(), name='user-detail'), 
    # path('bankers/list/', BankerListView.as_view()),
    # path('bankers/<int:user_id>/', BankerView.as_view(), name='banker-detail'),
    # path('accounts/', include('django.contrib.auth.urls')),  
]

urlpatterns = format_suffix_patterns(urlpatterns)
