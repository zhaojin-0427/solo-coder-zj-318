import hashlib
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q, IntegerField, Min, Max
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation
)
from .serializers import (
    PersonSerializer, AliasSerializer, MigrationInfoSerializer,
    RelationshipSerializer, PhotoSerializer, PersonInPhotoSerializer,
    MemoryFragmentSerializer, ConflictVersionSerializer,
    FamilyConfirmationSerializer, StatsSerializer, PersonSimpleSerializer,
    PhotoSimpleSerializer, ClueSerializer, ClaimClueSerializer,
    ClaimResultSerializer
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


def _normalize_name(name):
    if not name:
        return ''
    name = name.strip()
    name = name.replace('（', '(').replace('）', ')')
    if '(' in name:
        name = name.split('(')[0].strip()
    return name


def _get_clue_key(name):
    normalized = _normalize_name(name)
    if not normalized:
        return None
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def _aggregate_clues(pip_qs):
    unconfirmed_pips = pip_qs.filter(
        person__isnull=True,
        person_name_override__isnull=False
    ).exclude(person_name_override='')

    clues_dict = {}
    for pip in unconfirmed_pips:
        clue_name = _normalize_name(pip.person_name_override)
        if not clue_name:
            continue
        clue_key = _get_clue_key(clue_name)
        if clue_key not in clues_dict:
            clues_dict[clue_key] = {
                'clue_name': clue_name,
                'clue_key': clue_key,
                'count': 0,
                'items': [],
                'first_seen': pip.created_at,
                'last_seen': pip.created_at,
                'position_notes': set(),
                'old_titles': set(),
            }
        clues_dict[clue_key]['count'] += 1
        clues_dict[clue_key]['items'].append(pip)
        if pip.created_at < clues_dict[clue_key]['first_seen']:
            clues_dict[clue_key]['first_seen'] = pip.created_at
        if pip.created_at > clues_dict[clue_key]['last_seen']:
            clues_dict[clue_key]['last_seen'] = pip.created_at
        if pip.position_note:
            clues_dict[clue_key]['position_notes'].add(pip.position_note)
        if pip.old_title:
            clues_dict[clue_key]['old_titles'].add(pip.old_title)

    for key in clues_dict:
        clues_dict[key]['position_notes'] = list(clues_dict[key]['position_notes'])
        clues_dict[key]['old_titles'] = list(clues_dict[key]['old_titles'])

    return list(clues_dict.values())


class CluesView(APIView):
    def get(self, request):
        search = request.query_params.get('search', '')
        sort_by = request.query_params.get('sort_by', 'count')
        sort_order = request.query_params.get('sort_order', 'desc')

        pip_qs = PersonInPhoto.objects.select_related('photo')

        if search:
            pip_qs = pip_qs.filter(
                Q(person_name_override__icontains=search) |
                Q(position_note__icontains=search) |
                Q(old_title__icontains=search) |
                Q(photo__title__icontains=search)
            )

        clues = _aggregate_clues(pip_qs)

        if sort_by == 'count':
            clues.sort(key=lambda x: x['count'], reverse=(sort_order == 'desc'))
        elif sort_by == 'name':
            clues.sort(key=lambda x: x['clue_name'], reverse=(sort_order == 'desc'))
        elif sort_by == 'last_seen':
            clues.sort(key=lambda x: x['last_seen'], reverse=(sort_order == 'desc'))

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        paginated = clues[start:end]

        serializer = ClueSerializer(paginated, many=True)
        return Response({
            'count': len(clues),
            'next': None if end >= len(clues) else f'?page={page + 1}',
            'previous': None if page <= 1 else f'?page={page - 1}',
            'results': serializer.data
        })


class ClueDetailView(APIView):
    def get(self, request, clue_key):
        pip_qs = PersonInPhoto.objects.select_related('photo')
        all_clues = _aggregate_clues(pip_qs)
        clue = next((c for c in all_clues if c['clue_key'] == clue_key), None)
        if not clue:
            return Response({'error': '线索不存在'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClueSerializer(clue)
        return Response(serializer.data)


class ClaimClueView(APIView):
    def post(self, request):
        serializer = ClaimClueSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        mode = data['mode']
        claimed_by = data.get('claimed_by', '家属')
        add_as_alias = data.get('add_as_alias', True)

        clue_keys = []
        if data.get('clue_key'):
            clue_keys.append(data['clue_key'])
        if data.get('clue_keys'):
            clue_keys.extend(data['clue_keys'])

        person = None
        created_person = False

        if mode == 'existing':
            try:
                person = Person.objects.get(id=data['person_id'])
            except Person.DoesNotExist:
                return Response({'error': '人物不存在'}, status=status.HTTP_404_NOT_FOUND)
        else:
            person_data = data['person_data']
            name = person_data.get('name', '')
            if not name:
                return Response({'error': '新建人物必须提供姓名'}, status=status.HTTP_400_BAD_REQUEST)

            existing = Person.objects.filter(name=name).first()
            if existing:
                person = existing
            else:
                person = Person.objects.create(
                    name=name,
                    gender=person_data.get('gender', 'U'),
                    birth_year=person_data.get('birth_year'),
                    death_year=person_data.get('death_year'),
                    birth_place=person_data.get('birth_place', ''),
                    description=person_data.get('description', ''),
                    status='pending',
                    created_by=claimed_by
                )
                created_person = True

        pip_qs = PersonInPhoto.objects.select_related('photo')
        all_clues = _aggregate_clues(pip_qs)

        target_pips = []
        clue_names_for_alias = []
        for ck in clue_keys:
            clue = next((c for c in all_clues if c['clue_key'] == ck), None)
            if clue:
                target_pips.extend(clue['items'])
                clue_names_for_alias.append(clue['clue_name'])

        if not target_pips:
            return Response(
                {'error': '未找到待认领的线索', 'success': False},
                status=status.HTTP_404_NOT_FOUND
            )

        updated_photo_ids = []
        claimed_count = 0

        for pip in target_pips:
            if pip.person_id == person.id:
                continue
            pip.person = person
            pip.save()
            claimed_count += 1
            if pip.photo_id not in updated_photo_ids:
                updated_photo_ids.append(pip.photo_id)

        if add_as_alias and mode == 'existing':
            for alias_name in clue_names_for_alias:
                if alias_name and alias_name != person.name:
                    existing_alias = Alias.objects.filter(
                        person=person, alias_name=alias_name
                    ).first()
                    if not existing_alias:
                        Alias.objects.create(
                            person=person,
                            alias_name=alias_name,
                            usage_context='线索认领自动添加',
                            added_by=claimed_by
                        )

        for photo_id in updated_photo_ids:
            try:
                photo = Photo.objects.get(id=photo_id)
                unconfirmed_count = PersonInPhoto.objects.filter(
                    photo=photo, person__isnull=True
                ).exclude(person_name_override='').count()
                if unconfirmed_count == 0:
                    if photo.status == 'annotating':
                        photo.status = 'completed'
                        photo.save()
                else:
                    if photo.status == 'archived':
                        photo.status = 'annotating'
                        photo.save()
            except Photo.DoesNotExist:
                pass

        result = {
            'success': True,
            'person_id': person.id,
            'person_name': person.name,
            'claimed_count': claimed_count,
            'updated_photos': updated_photo_ids,
            'message': f'成功认领 {claimed_count} 条线索，关联到人物「{person.name}」',
            'created_person': created_person
        }
        return Response(result)


class ClueStatsView(APIView):
    def get(self, request):
        pip_qs = PersonInPhoto.objects.all()
        unconfirmed_pips = pip_qs.filter(
            person__isnull=True
        ).exclude(person_name_override='')
        unconfirmed_total = unconfirmed_pips.count()

        clues = _aggregate_clues(pip_qs)
        total_clues = len(clues)

        photo_ids_with_clues = unconfirmed_pips.values_list('photo_id', flat=True).distinct()
        photos_with_clues = len(photo_ids_with_clues)

        multi_photo_clues = sum(1 for c in clues if c['count'] > 1)
        single_photo_clues = sum(1 for c in clues if c['count'] == 1)

        top_clues = sorted(clues, key=lambda x: x['count'], reverse=True)[:10]
        top_clues_simple = [
            {'clue_name': c['clue_name'], 'clue_key': c['clue_key'], 'count': c['count']}
            for c in top_clues
        ]

        return Response({
            'total_clues': total_clues,
            'unconfirmed_annotations': unconfirmed_total,
            'photos_with_clues': photos_with_clues,
            'multi_photo_clues': multi_photo_clues,
            'single_photo_clues': single_photo_clues,
            'top_clues': top_clues_simple,
        })


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

        try:
            pip_qs = PersonInPhoto.objects.all()
            clues = _aggregate_clues(pip_qs)
            total_clues = len(clues)
            unconfirmed_total = total_pip - confirmed_pip
            multi_photo_clues = sum(1 for c in clues if c['count'] > 1)

            clue_stats = {
                'total_clues': total_clues,
                'unconfirmed_annotations': unconfirmed_total,
                'multi_photo_clues': multi_photo_clues,
                'single_photo_clues': total_clues - multi_photo_clues,
            }
        except Exception as e:
            clue_stats = {
                'total_clues': 0,
                'unconfirmed_annotations': 0,
                'multi_photo_clues': 0,
                'single_photo_clues': 0,
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
            'clue_stats': clue_stats,
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)
