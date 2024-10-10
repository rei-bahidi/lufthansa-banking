from django.urls import path, include 
from .views import UserListView, UserView, BankerListView, BankerView

urlpatterns = [
    path('customers/', UserView.as_view(), name='user-create'),  
    path('customers/list', UserListView.as_view(), name='user-list'), 
    path('customers/<int:user_id>', UserView.as_view(), name='user-detail'), 
    path('bankers/list', BankerListView.as_view()),
    path('bankers/<int:user_id>', BankerView.as_view(), name='banker-detail'),
    # path('accounts/', include('django.contrib.auth.urls')),  
]