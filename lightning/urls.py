from django.urls import path
from .views import (
    LightningList, LightningCreate, LightningDetail,
    LightningUpdate, LightningDelete, JoinLightning, LeaveLightning,
    LightningCategoryFilterView, LightningStatusFilterView
)

app_name = 'lightning'

urlpatterns = [
    path('', LightningList.as_view(), name='meetup-list'),
    path('create/', LightningCreate.as_view(), name='meetup-create'),
    path('<int:pk>/', LightningDetail.as_view(), name='meetup-detail'),
    path('category/', LightningCategoryFilterView.as_view(), name='lightning_category_filter'),
    path('status/', LightningStatusFilterView.as_view(), name='lightning_status_filter'),
    path('<int:pk>/update/', LightningUpdate.as_view(), name='meetup-update'),
    path('<int:pk>/delete/', LightningDelete.as_view(), name='meetup-delete'),
    path('<int:pk>/join/', JoinLightning.as_view(), name='lightning-join'),
    path('<int:pk>/leave/', LeaveLightning.as_view(), name='leave-lightning'),
]