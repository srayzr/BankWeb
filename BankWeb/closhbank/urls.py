from django.urls import path
from .views import CreatePersonView, PersonDetailView, CreateAccountView, AccountDetailView

urlpatterns = [
    path('create_person/', CreatePersonView.as_view(), name='create_person'),
    path('person_detail/<int:person_id>/', PersonDetailView.as_view(), name='person_detail'),
    path('create_account/', CreateAccountView.as_view(), name='create_account'),
    path('account_detail/<int:account_id>/', AccountDetailView.as_view(), name='account_detail'),
]
