from django.urls import path

from api.mock.views import (
    MockElementDetailView,
    MockElementListCreateView,
    MockElementsIndexView,
)

urlpatterns = [
    path('', MockElementsIndexView.as_view(), name='mock-index'),
    path('<slug:element>/', MockElementListCreateView.as_view(), name='mock-list-create'),
    path('<slug:element>/<int:obj_id>/', MockElementDetailView.as_view(), name='mock-detail'),
]
