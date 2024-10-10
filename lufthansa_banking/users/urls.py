from django.urls import path, include 
from .views import UserListView, UserView, BankerListView, BankerView

urlpatterns = [
    path('customers/list', UserListView.as_view()),  # Link the function-based view to a URL
    path('customers/<int:user_id>', UserView.as_view(), name='user-detail'),  # Link the class-based view to a URL for detail view
    path('bankers/list', BankerListView.as_view()),
    path('bankers/<int:user_id>', BankerView.as_view(), name='banker-detail'),
    # path('accounts/', include('django.contrib.auth.urls')),  
]