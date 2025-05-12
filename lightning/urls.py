from django.urls import path
from .views import (
    LightningList, LightningCreate, LightningDetail,
    LightningUpdate, LightningDelete
)

app_name = 'lightning'

urlpatterns = [
    path('', LightningList.as_view(), name='meetup-list'),
    path('create/', LightningCreate.as_view(), name='meetup-create'),
    path('<int:pk>/', LightningDetail.as_view(), name='meetup-detail'),
    path('<int:pk>/update/', LightningUpdate.as_view(), name='meetup-update'),
    path('<int:pk>/delete/', LightningDelete.as_view(), name='meetup-delete'),
]