from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q, IntegerField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation
)
from .serializers import (
    PersonSerializer, AliasSerializer, MigrationInfoSerializer,
    RelationshipSerializer, PhotoSerializer, PersonInPhotoSerializer,
    MemoryFragmentSerializer, ConflictVersionSerializer,
    FamilyConfirmationSerializer, StatsSerializer, PersonSimpleSerializer,
    PhotoSimpleSerializer
)
from .filters import PhotoFilter, PersonFilter


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PersonFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            relationship_count=Count('relationships_from', distinct=True) + Count('relationships_to', distinct=True),
            photo_count=Count('photos', distinct=True),
            memory_count=Count('memories', distinct=True)
        )

    @action(detail=False, methods=['get'])
    def simple(self, request):
        qs = Person.objects.all()
        serializer = PersonSimpleSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_alias(self, request, pk=None):
        person = self.get_object()
        serializer = AliasSerializer(data={**request.data, 'person': person.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_migration(self, request, pk=None):
        person = self.get_object()
        serializer = MigrationInfoSerializer(data={**request.data, 'person': person.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    filterset_fields = ['from_person', 'to_person', 'relation_type']


class AliasViewSet(viewsets.ModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
    filterset_fields = ['person']


class MigrationInfoViewSet(viewsets.ModelViewSet):
    queryset = MigrationInfo.objects.all()
    serializer_class = MigrationInfoSerializer
    filterset_fields = ['person']


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PhotoFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            person_count=Count('people_in_photo', distinct=True)
        )

    @action(detail=False, methods=['get'])
    def simple(self, request):
        qs = Photo.objects.all()[:100]
        serializer = PhotoSimpleSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_person(self, request, pk=None):
        photo = self.get_object()
        serializer = PersonInPhotoSerializer(data={**request.data, 'photo': photo.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def people(self, request, pk=None):
        photo = self.get_object()
        people = PersonInPhoto.objects.filter(photo=photo)
        serializer = PersonInPhotoSerializer(people, many=True)
        return Response(serializer.data)


class PersonInPhotoViewSet(viewsets.ModelViewSet):
    queryset = PersonInPhoto.objects.all()
    serializer_class = PersonInPhotoSerializer
    filterset_fields = ['photo', 'person']


class MemoryFragmentViewSet(viewsets.ModelViewSet):
    queryset = MemoryFragment.objects.all()
    serializer_class = MemoryFragmentSerializer
    filterset_fields = ['status', 'author']

    @action(detail=True, methods=['post'])
    def link_photo(self, request, pk=None):
        memory = self.get_object()
        photo_id = request.data.get('photo_id')
        if photo_id:
            try:
                photo = Photo.objects.get(id=photo_id)
                memory.related_photos.add(photo)
                return Response({'status': 'linked'})
            except Photo.DoesNotExist:
                return Response({'error': 'Photo not found'}, status=404)
        return Response({'error': 'photo_id required'}, status=400)

    @action(detail=True, methods=['post'])
    def link_person(self, request, pk=None):
        memory = self.get_object()
        person_id = request.data.get('person_id')
        if person_id:
            try:
                person = Person.objects.get(id=person_id)
                memory.related_people.add(person)
                return Response({'status': 'linked'})
            except Person.DoesNotExist:
                return Response({'error': 'Person not found'}, status=404)
        return Response({'error': 'person_id required'}, status=400)


class ConflictVersionViewSet(viewsets.ModelViewSet):
    queryset = ConflictVersion.objects.all()
    serializer_class = ConflictVersionSerializer
    filterset_fields = ['status', 'conflict_field', 'related_person', 'related_photo']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        conflict = self.get_object()
        version = request.data.get('version')
        resolved_by = request.data.get('resolved_by', '')
        if version in ['A', 'B']:
            conflict.status = 'resolved'
            conflict.resolved_version = version
            conflict.resolved_by = resolved_by
            from django.utils import timezone
            conflict.resolved_at = timezone.now()
            conflict.save()
            return Response({'status': 'resolved', 'version': version})
        return Response({'error': 'version must be A or B'}, status=400)


class FamilyConfirmationViewSet(viewsets.ModelViewSet):
    queryset = FamilyConfirmation.objects.all()
    serializer_class = FamilyConfirmationSerializer
    filterset_fields = ['status', 'confirm_type']

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        conf = self.get_object()
        voter = request.data.get('voter', '匿名家属')
        vote_type = request.data.get('vote')  # 'approve' or 'reject'
        if voter in conf.voters:
            return Response({'error': '已投过票'}, status=400)
        conf.voters.append(voter)
        if vote_type == 'approve':
            conf.vote_approve += 1
        elif vote_type == 'reject':
            conf.vote_reject += 1
        else:
            return Response({'error': 'vote must be approve or reject'}, status=400)
        total = conf.vote_approve + conf.vote_reject
        if total >= 3:
            if conf.vote_approve > conf.vote_reject:
                conf.status = 'approved'
            elif conf.vote_reject > conf.vote_approve:
                conf.status = 'rejected'
            else:
                conf.status = 'tied'
        conf.save()
        return Response({'status': 'voted', 'approve': conf.vote_approve, 'reject': conf.vote_reject})


class StatsView(APIView):
    def get(self, request):
        total_photos = Photo.objects.count()
        total_persons = Person.objects.count()
        pending_persons = Person.objects.filter(status='pending').count()
        total_memories = MemoryFragment.objects.count()
        open_conflicts = ConflictVersion.objects.filter(status='open').count()
        pending_confirmations = FamilyConfirmation.objects.filter(status='pending').count()

        era_list = ['1920s', '1930s', '1940s', '1950s', '1960s', '1970s',
                    '1980s', '1990s', '2000s', '2010s', '2020s', 'unknown']
        era_coverage = []
        for era in era_list:
            count = Photo.objects.filter(era=era).count()
            era_obj = Photo._meta.get_field('era').choices
            label = dict(era_obj).get(era, era)
            era_coverage.append({'era': era, 'label': label, 'count': count})

        top_persons = list(
            Person.objects.annotate(
                count=Count('photos', distinct=True) + Count('memories', distinct=True)
            ).order_by('-count').values('id', 'name', 'count')[:10]
        )

        archived = Photo.objects.filter(status='archived').count()
        annotating = Photo.objects.filter(status='annotating').count()
        completed = Photo.objects.filter(status='completed').count()
        draft_mem = MemoryFragment.objects.filter(status='draft').count()
        submitted_mem = MemoryFragment.objects.filter(status='submitted').count()
        published_mem = MemoryFragment.objects.filter(status='published').count()
        total_pip = PersonInPhoto.objects.count()
        confirmed_pip = PersonInPhoto.objects.filter(person__isnull=False).count()

        annotation_completion = {
            'photos': {'archived': archived, 'annotating': annotating, 'completed': completed, 'total': total_photos},
            'persons_in_photos': {'confirmed': confirmed_pip, 'unconfirmed': total_pip - confirmed_pip, 'total': total_pip},
            'memories': {'draft': draft_mem, 'submitted': submitted_mem, 'published': published_mem, 'total': total_memories},
        }

        data = {
            'total_photos': total_photos,
            'total_persons': total_persons,
            'pending_persons': pending_persons,
            'total_memories': total_memories,
            'open_conflicts': open_conflicts,
            'pending_confirmations': pending_confirmations,
            'era_coverage': era_coverage,
            'top_persons': top_persons,
            'annotation_completion': annotation_completion,
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)
