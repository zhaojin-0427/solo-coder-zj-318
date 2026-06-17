from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonViewSet, RelationshipViewSet, AliasViewSet, MigrationInfoViewSet,
    PhotoViewSet, PersonInPhotoViewSet, MemoryFragmentViewSet,
    ConflictVersionViewSet, FamilyConfirmationViewSet, StatsView
)

router = DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'relationships', RelationshipViewSet)
router.register(r'aliases', AliasViewSet)
router.register(r'migrations', MigrationInfoViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'person-in-photo', PersonInPhotoViewSet)
router.register(r'memories', MemoryFragmentViewSet)
router.register(r'conflicts', ConflictVersionViewSet)
router.register(r'confirmations', FamilyConfirmationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', StatsView.as_view(), name='stats'),
]
