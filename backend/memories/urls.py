from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonViewSet, RelationshipViewSet, AliasViewSet, MigrationInfoViewSet,
    PhotoViewSet, PersonInPhotoViewSet, MemoryFragmentViewSet,
    ConflictVersionViewSet, FamilyConfirmationViewSet, StatsView,
    CluesView, ClueDetailView, ClaimClueView, ClueStatsView
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
    path('clues/', CluesView.as_view(), name='clues'),
    path('clues/stats/', ClueStatsView.as_view(), name='clue-stats'),
    path('clues/<str:clue_key>/', ClueDetailView.as_view(), name='clue-detail'),
    path('clues/claim/', ClaimClueView.as_view(), name='claim-clue'),
]
