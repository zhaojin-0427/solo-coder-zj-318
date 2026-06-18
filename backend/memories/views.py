import hashlib
import uuid
import re
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q, IntegerField, Min, Max, Sum
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation,
    CollectionTask, TaskSubmission, Contribution,
    StandardizedLocation, TimelineNode
)
from .serializers import (
    PersonSerializer, AliasSerializer, MigrationInfoSerializer,
    RelationshipSerializer, PhotoSerializer, PersonInPhotoSerializer,
    MemoryFragmentSerializer, ConflictVersionSerializer,
    FamilyConfirmationSerializer, StatsSerializer, PersonSimpleSerializer,
    PhotoSimpleSerializer, ClueSerializer, ClaimClueSerializer,
    ClaimResultSerializer, CollectionTaskSerializer, TaskSubmissionSerializer,
    ContributionSerializer, TaskStatsSerializer, TaskClaimSerializer,
    TaskSubmitSerializer, TaskReviewSerializer, GenerateTasksSerializer,
    ContributionRankingSerializer,
    StandardizedLocationSerializer, LocationSimpleSerializer, LocationParseSerializer,
    TimelineNodeSerializer, TimelineQuerySerializer, TimelineAggregateSerializer,
    SpaceArchiveQuerySerializer, NodeCreateTaskSerializer
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


def _create_contribution(contributor, ctype, **kwargs):
    points_map = {
        'task_submit': 10,
        'task_claim': 5,
        'task_approved': 30,
        'clue_claim': 20,
        'person_add': 25,
        'memory_add': 35,
        'photo_annotate': 15,
        'review_pass': 20,
        'vote_participate': 5,
    }
    Contribution.objects.create(
        contributor=contributor,
        contribution_type=ctype,
        points=points_map.get(ctype, 10),
        **kwargs
    )


def _check_for_conflict(task, submission_data):
    has_conflict = False
    conflict_desc = ''
    try:
        if task.task_type == 'old_name_supplement':
            alias_name = submission_data.get('alias_name', '')
            if task.related_person:
                exists = Alias.objects.filter(
                    person=task.related_person, alias_name=alias_name
                ).exists()
                if exists:
                    has_conflict = True
                    conflict_desc = f'别名「{alias_name}」已存在'
        elif task.task_type == 'identity_confirm':
            if task.related_photo and submission_data.get('person_id'):
                person_id = submission_data.get('person_id')
                pip_exists = PersonInPhoto.objects.filter(
                    photo=task.related_photo, person_id=person_id
                ).exists()
                if pip_exists:
                    has_conflict = True
                    conflict_desc = f'该人物已关联到此照片'
        elif task.task_type == 'migration_supplement':
            if task.related_person:
                from_place = submission_data.get('from_place', '')
                to_place = submission_data.get('to_place', '')
                exists = MigrationInfo.objects.filter(
                    person=task.related_person,
                    from_place=from_place,
                    to_place=to_place
                ).exists()
                if exists:
                    has_conflict = True
                    conflict_desc = f'迁居信息 {from_place}→{to_place} 已存在'
    except Exception:
        pass
    return has_conflict, conflict_desc


def _apply_submission_data(task, submission_data, submitter):
    try:
        if task.task_type == 'old_name_supplement' and task.related_person:
            Alias.objects.create(
                person=task.related_person,
                alias_name=submission_data.get('alias_name', ''),
                usage_context=submission_data.get('usage_context', ''),
                added_by=submitter
            )
        elif task.task_type == 'migration_supplement' and task.related_person:
            MigrationInfo.objects.create(
                person=task.related_person,
                from_place=submission_data.get('from_place', ''),
                to_place=submission_data.get('to_place', ''),
                move_year=submission_data.get('move_year'),
                reason=submission_data.get('reason', ''),
                added_by=submitter
            )
        elif task.task_type == 'identity_confirm' and task.related_photo:
            person_id = submission_data.get('person_id')
            if person_id:
                extra = task.extra_context or {}
                pip_id = extra.get('person_in_photo_id')
                if pip_id:
                    pip = PersonInPhoto.objects.filter(id=pip_id).first()
                    if pip:
                        pip.person_id = person_id
                        pip.added_by = submitter
                        pip.save()
                else:
                    PersonInPhoto.objects.create(
                        photo=task.related_photo,
                        person_id=person_id,
                        position_note=submission_data.get('position_note', ''),
                        added_by=submitter
                    )
        elif task.task_type == 'event_narration':
            if task.related_photo:
                task.related_photo.description = submission_data.get('description', task.related_photo.description)
                task.related_photo.save()
            elif task.related_memory:
                task.related_memory.content = submission_data.get('content', task.related_memory.content)
                task.related_memory.save()
        elif task.task_type == 'relation_verify' and task.related_person:
            to_person_id = submission_data.get('to_person_id')
            relation_type = submission_data.get('relation_type')
            if to_person_id and relation_type:
                Relationship.objects.create(
                    from_person=task.related_person,
                    to_person_id=to_person_id,
                    relation_type=relation_type,
                    relation_note=submission_data.get('relation_note', ''),
                    added_by=submitter
                )
        return True
    except Exception:
        return False


def _create_confirmation_for_submission(task, submission, conflict_desc):
    conf = FamilyConfirmation.objects.create(
        confirm_type='person' if task.source_type == 'person' else
                     'photo_info' if task.source_type == 'photo' else 'memory',
        related_person=task.related_person,
        related_photo=task.related_photo,
        related_memory=task.related_memory,
        title=f'{task.get_task_type_display()}信息确认：{task.title}',
        detail=f'提交人：{submission.submitter}\n提交内容：{submission.submission_text or str(submission.submission_data)}\n冲突说明：{conflict_desc}',
        proposer=submission.submitter,
        status='pending'
    )
    return conf


class CollectionTaskViewSet(viewsets.ModelViewSet):
    queryset = CollectionTask.objects.all()
    serializer_class = CollectionTaskSerializer
    filterset_fields = ['task_type', 'source_type', 'status', 'assign_type', 'assigned_to', 'claimed_by',
                        'related_photo', 'related_person', 'related_memory']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            submission_count=Count('submissions', distinct=True)
        )

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        claimant = request.query_params.get('claimed_by', '')
        status_filter = request.query_params.get('status', '')
        qs = self.get_queryset()
        if claimant:
            qs = qs.filter(
                Q(claimed_by=claimant) | Q(assigned_to=claimant)
            )
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['open', 'assigned']:
            return Response({'error': '该任务状态不允许认领'}, status=status.HTTP_400_BAD_REQUEST)
        if task.assign_type == 'specific' and task.assigned_to:
            claimant = request.data.get('claimed_by', '')
            if claimant and task.assigned_to != claimant:
                return Response({'error': f'此任务仅分派给「{task.assigned_to}」'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskClaimSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        task.claimed_by = serializer.validated_data['claimed_by']
        task.claimed_at = timezone.now()
        task.status = 'in_progress'
        task.save()
        _create_contribution(
            task.claimed_by, 'task_claim',
            related_task=task, description=f'认领任务：{task.title}'
        )
        return Response({'status': 'claimed', 'task': CollectionTaskSerializer(task).data})

    @action(detail=True, methods=['post'])
    def unclaim(self, request, pk=None):
        task = self.get_object()
        if task.status != 'in_progress':
            return Response({'error': '该任务状态不允许放弃认领'}, status=status.HTTP_400_BAD_REQUEST)
        task.claimed_by = ''
        task.claimed_at = None
        task.status = 'assigned' if task.assign_type == 'specific' and task.assigned_to else 'open'
        task.save()
        return Response({'status': 'unclaimed'})

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['in_progress', 'assigned']:
            return Response({'error': '该任务状态不允许提交'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        has_conflict, conflict_desc = _check_for_conflict(task, data['submission_data'])
        submission = TaskSubmission.objects.create(
            task=task,
            submitter=data['submitter'],
            submission_data=data['submission_data'],
            submission_text=data['submission_text'],
            has_conflict=has_conflict,
            conflict_description=conflict_desc,
            status='conflicted' if has_conflict else 'pending'
        )
        task.status = 'conflicted' if has_conflict else 'submitted'
        task.save()
        _create_contribution(
            data['submitter'], 'task_submit',
            related_task=task, related_person=task.related_person,
            related_photo=task.related_photo, related_memory=task.related_memory,
            description=f'提交任务补注：{task.title}'
        )
        if has_conflict:
            conf = _create_confirmation_for_submission(task, submission, conflict_desc)
            submission.related_confirmation = conf
            submission.save()
            try:
                cv = ConflictVersion.objects.create(
                    related_person=task.related_person,
                    related_photo=task.related_photo,
                    related_memory=task.related_memory,
                    conflict_field='other',
                    version_a=str(task.extra_context or '原有信息'),
                    version_a_author=task.created_by or '原数据',
                    version_b=str(data['submission_data']) + (data['submission_text'] or ''),
                    version_b_author=data['submitter'],
                    description=conflict_desc,
                    status='open'
                )
                submission.related_conflict = cv
                submission.save()
                conf.related_conflict = cv
                conf.save()
            except Exception:
                pass
        return Response({
            'status': 'submitted',
            'has_conflict': has_conflict,
            'submission': TaskSubmissionSerializer(submission).data
        })

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        task = self.get_object()
        if task.status not in ['submitted']:
            return Response({'error': '该任务状态不允许审核'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        last_submission = task.submissions.order_by('-created_at').first()
        if not last_submission:
            return Response({'error': '未找到提交记录'}, status=status.HTTP_400_BAD_REQUEST)

        if data['action'] == 'approve':
            success = _apply_submission_data(task, last_submission.submission_data, last_submission.submitter)
            if not success:
                return Response({'error': '应用提交数据失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            last_submission.status = 'approved'
            last_submission.reviewer = data['reviewer']
            last_submission.review_comment = data['comment']
            last_submission.reviewed_at = timezone.now()
            last_submission.save()
            task.status = 'completed'
            task.save()
            _create_contribution(
                last_submission.submitter, 'task_approved',
                related_task=task, related_person=task.related_person,
                description=f'任务补注审核通过：{task.title}'
            )
            _create_contribution(
                data['reviewer'], 'review_pass',
                related_task=task, description=f'审核通过任务：{task.title}'
            )
        elif data['action'] == 'reject':
            last_submission.status = 'rejected'
            last_submission.reviewer = data['reviewer']
            last_submission.review_comment = data['comment']
            last_submission.reviewed_at = timezone.now()
            last_submission.save()
            task.status = 'rejected'
            task.save()
        elif data['action'] == 'to_conflict':
            has_conflict = True
            conflict_desc = data['comment'] or '审核员判定存在信息冲突'
            last_submission.status = 'conflicted'
            last_submission.has_conflict = has_conflict
            last_submission.conflict_description = conflict_desc
            last_submission.reviewer = data['reviewer']
            last_submission.review_comment = data['comment']
            last_submission.reviewed_at = timezone.now()
            last_submission.save()
            task.status = 'conflicted'
            task.save()
            conf = _create_confirmation_for_submission(task, last_submission, conflict_desc)
            last_submission.related_confirmation = conf
            last_submission.save()

        return Response({
            'status': 'reviewed',
            'action': data['action'],
            'task': CollectionTaskSerializer(task).data,
            'submission': TaskSubmissionSerializer(last_submission).data
        })

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        task = self.get_object()
        subs = TaskSubmission.objects.filter(task=task).order_by('-created_at')
        serializer = TaskSubmissionSerializer(subs, many=True)
        return Response(serializer.data)


class TaskSubmissionViewSet(viewsets.ModelViewSet):
    queryset = TaskSubmission.objects.all()
    serializer_class = TaskSubmissionSerializer
    filterset_fields = ['status', 'submitter', 'task', 'has_conflict']


class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    filterset_fields = ['contributor', 'contribution_type']


class TaskStatsView(APIView):
    def get(self, request):
        contributor = request.query_params.get('contributor', '')
        total_tasks = CollectionTask.objects.count()
        open_tasks = CollectionTask.objects.filter(status='open').count()
        assigned_tasks = CollectionTask.objects.filter(status='assigned').count()
        in_progress_tasks = CollectionTask.objects.filter(status='in_progress').count()
        submitted_tasks = CollectionTask.objects.filter(status='submitted').count()
        completed_tasks = CollectionTask.objects.filter(status='completed').count()
        rejected_tasks = CollectionTask.objects.filter(status='rejected').count()
        conflicted_tasks = CollectionTask.objects.filter(status='conflicted').count()

        total_submissions = TaskSubmission.objects.count()
        approved_submissions = TaskSubmission.objects.filter(status='approved').count()
        conflicted_submissions = TaskSubmission.objects.filter(status='conflicted').count()

        closed_total = completed_tasks + rejected_tasks + conflicted_tasks
        completion_rate = round(completed_tasks / closed_total * 100, 1) if closed_total > 0 else 0.0
        conflict_rate = round(conflicted_submissions / total_submissions * 100, 1) if total_submissions > 0 else 0.0

        contributions_agg = list(
            Contribution.objects.values('contributor')
            .annotate(
                total_points=Sum('points'),
                task_count=Count('id', filter=Q(contribution_type__startswith='task_')),
                task_approved_count=Count('id', filter=Q(contribution_type='task_approved'))
            )
            .order_by('-total_points')[:10]
        )
        leaderboard = []
        for c in contributions_agg:
            types_detail = list(
                Contribution.objects.filter(contributor=c['contributor'])
                .values('contribution_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            leaderboard.append({
                **c,
                'contribution_detail': [
                    {'type': t['contribution_type'],
                     'type_display': dict(Contribution.TYPE_CHOICES).get(t['contribution_type'], t['contribution_type']),
                     'count': t['count']}
                    for t in types_detail
                ]
            })

        top_task_persons_qs = list(
            CollectionTask.objects.values('related_person__id', 'related_person__name')
            .filter(related_person__isnull=False)
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        top_task_persons = [
            {'person_id': t['related_person__id'], 'name': t['related_person__name'], 'task_count': t['count']}
            for t in top_task_persons_qs if t['related_person__name']
        ]

        task_type_qs = list(
            CollectionTask.objects.values('task_type')
            .annotate(count=Count('id'), completed=Count('id', filter=Q(status='completed')))
            .order_by('-count')
        )
        task_type_distribution = [
            {'type': t['task_type'],
             'type_display': dict(CollectionTask.TASK_TYPE_CHOICES).get(t['task_type'], t['task_type']),
             'count': t['count'], 'completed': t['completed']}
            for t in task_type_qs
        ]

        my_contribution = {}
        if contributor:
            contribs = Contribution.objects.filter(contributor=contributor)
            my_contribution = {
                'contributor': contributor,
                'total_points': contribs.aggregate(total=Sum('points'))['total'] or 0,
                'total_count': contribs.count(),
                'by_type': list(
                    contribs.values('contribution_type')
                    .annotate(count=Count('id'), points=Sum('points'))
                    .order_by('-points')
                ),
                'recent': list(contribs[:20].values(
                    'id', 'contribution_type', 'description', 'points', 'created_at'
                ))
            }

        data = {
            'total_tasks': total_tasks,
            'open_tasks': open_tasks + assigned_tasks,
            'assigned_tasks': assigned_tasks,
            'in_progress_tasks': in_progress_tasks,
            'submitted_tasks': submitted_tasks,
            'completed_tasks': completed_tasks,
            'rejected_tasks': rejected_tasks,
            'conflicted_tasks': conflicted_tasks,
            'completion_rate': completion_rate,
            'conflict_rate': conflict_rate,
            'total_submissions': total_submissions,
            'approved_submissions': approved_submissions,
            'contribution_leaderboard': leaderboard,
            'top_task_persons': top_task_persons,
            'task_type_distribution': task_type_distribution,
            'my_contribution': my_contribution,
        }
        return Response(data)


class GenerateTasksView(APIView):
    def post(self, request):
        serializer = GenerateTasksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        created_tasks = []
        source_type = data['source_type']
        task_types = data['task_types']

        def _build_task(tt, obj, st, extra=None):
            if task_types and tt not in task_types:
                return None
            obj_title = ''
            if hasattr(obj, 'title'):
                obj_title = obj.title
            elif hasattr(obj, 'name'):
                obj_title = obj.name

            title_map = {
                'identity_confirm': f'确认照片人物身份：{obj_title}',
                'old_name_supplement': f'补充旧称/别名：{obj_title}',
                'migration_supplement': f'补充迁居信息：{obj_title}',
                'event_narration': f'记录事件背景口述：{obj_title}',
                'relation_verify': f'校验亲属关系：{obj_title}',
            }
            desc_map = {
                'identity_confirm': '请确认照片中待标注人物的真实身份，与已有人物档案关联。',
                'old_name_supplement': '请补充该人物的乳名、旧时称呼、曾用名、别名等信息。',
                'migration_supplement': '请补充该人物的迁居历史，包括迁出地、迁入地、年份及原因。',
                'event_narration': '请根据老人口述记录照片或回忆背后的事件背景、故事细节。',
                'relation_verify': '请校验或补充该人物与其他家族成员的亲属关系。',
            }
            task = CollectionTask(
                task_type=tt,
                title=title_map.get(tt, obj_title),
                description=desc_map.get(tt, ''),
                source_type=st,
                extra_context=extra or {},
                assign_type=data['assign_type'],
                assigned_to=data.get('assigned_to', ''),
                created_by=data.get('created_by', '系统'),
                priority=10 if tt in ['identity_confirm', 'event_narration'] else 5
            )
            if st == 'photo':
                task.related_photo = obj
            elif st == 'person':
                task.related_person = obj
            elif st == 'memory':
                task.related_memory = obj
            if data['assign_type'] == 'specific' and data.get('assigned_to'):
                task.status = 'assigned'
            return task

        objs = []
        if source_type == 'photo':
            if data.get('source_id'):
                try:
                    objs = [(Photo.objects.get(id=data['source_id']), 'photo')]
                except Photo.DoesNotExist:
                    return Response({'error': '照片不存在'}, status=404)
            else:
                objs = [(p, 'photo') for p in Photo.objects.filter(status__in=['archived', 'annotating'])]
        elif source_type == 'person':
            if data.get('source_id'):
                try:
                    objs = [(Person.objects.get(id=data['source_id']), 'person')]
                except Person.DoesNotExist:
                    return Response({'error': '人物不存在'}, status=404)
            else:
                objs = [(p, 'person') for p in Person.objects.filter(status__in=['pending', 'confirmed'])]
        elif source_type == 'memory':
            if data.get('source_id'):
                try:
                    objs = [(MemoryFragment.objects.get(id=data['source_id']), 'memory')]
                except MemoryFragment.DoesNotExist:
                    return Response({'error': '回忆不存在'}, status=404)
            else:
                objs = [(m, 'memory') for m in MemoryFragment.objects.filter(status__in=['draft', 'submitted'])]
        elif source_type == 'all':
            objs = [(p, 'photo') for p in Photo.objects.filter(status__in=['archived', 'annotating'])] + \
                   [(p, 'person') for p in Person.objects.filter(status__in=['pending', 'confirmed'])] + \
                   [(m, 'memory') for m in MemoryFragment.objects.filter(status__in=['draft', 'submitted'])]

        for obj, st in objs:
            if st == 'photo':
                tts = ['identity_confirm', 'event_narration']
                if task_types:
                    tts = [t for t in tts if t in task_types]
                for tt in tts:
                    exists = CollectionTask.objects.filter(
                        source_type=st, related_photo=obj, task_type=tt,
                        status__in=['open', 'assigned', 'in_progress', 'submitted']
                    ).exists()
                    if exists:
                        continue
                    t = _build_task(tt, obj, st)
                    if t:
                        t.save()
                        created_tasks.append(t)
            elif st == 'person':
                tts = ['old_name_supplement', 'migration_supplement', 'relation_verify']
                if task_types:
                    tts = [t for t in tts if t in task_types]
                for tt in tts:
                    exists = CollectionTask.objects.filter(
                        source_type=st, related_person=obj, task_type=tt,
                        status__in=['open', 'assigned', 'in_progress', 'submitted']
                    ).exists()
                    if exists:
                        continue
                    t = _build_task(tt, obj, st)
                    if t:
                        t.save()
                        created_tasks.append(t)
            elif st == 'memory':
                tts = ['event_narration']
                if task_types:
                    tts = [t for t in tts if t in task_types]
                for tt in tts:
                    exists = CollectionTask.objects.filter(
                        source_type=st, related_memory=obj, task_type=tt,
                        status__in=['open', 'assigned', 'in_progress', 'submitted']
                    ).exists()
                    if exists:
                        continue
                    t = _build_task(tt, obj, st)
                    if t:
                        t.save()
                        created_tasks.append(t)

        return Response({
            'status': 'created',
            'count': len(created_tasks),
            'tasks': CollectionTaskSerializer(created_tasks, many=True).data
        })


class ContributionRankingView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        contribs = list(
            Contribution.objects.values('contributor')
            .annotate(
                total_points=Sum('points'),
                task_count=Count('id', filter=Q(contribution_type__startswith='task_')),
                task_approved_count=Count('id', filter=Q(contribution_type='task_approved')),
                clue_count=Count('id', filter=Q(contribution_type='clue_claim')),
                memory_count=Count('id', filter=Q(contribution_type='memory_add')),
            )
            .order_by('-total_points')[:limit]
        )
        return Response({
            'count': len(contribs),
            'results': contribs
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

        total_tasks = CollectionTask.objects.count()
        open_tasks = CollectionTask.objects.filter(status__in=['open', 'assigned']).count()
        in_progress_tasks = CollectionTask.objects.filter(status='in_progress').count()
        submitted_tasks = CollectionTask.objects.filter(status='submitted').count()
        completed_tasks = CollectionTask.objects.filter(status='completed').count()
        rejected_tasks = CollectionTask.objects.filter(status='rejected').count()
        conflicted_tasks = CollectionTask.objects.filter(status='conflicted').count()
        total_submissions = TaskSubmission.objects.count()
        approved_submissions = TaskSubmission.objects.filter(status='approved').count()
        closed_total = completed_tasks + rejected_tasks + conflicted_tasks
        completion_rate = round(completed_tasks / closed_total * 100, 1) if closed_total > 0 else 0.0
        conflict_total = total_submissions
        conflict_turned = TaskSubmission.objects.filter(status='conflicted').count()
        conflict_confirm_rate = round(conflict_turned / conflict_total * 100, 1) if conflict_total > 0 else 0.0

        top_task_persons_qs = list(
            CollectionTask.objects.values('related_person__id', 'related_person__name')
            .filter(related_person__isnull=False)
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        top_task_persons = [
            {'person_id': t['related_person__id'], 'name': t['related_person__name'], 'task_count': t['count']}
            for t in top_task_persons_qs if t['related_person__name']
        ]

        contrib_agg = list(
            Contribution.objects.values('contributor')
            .annotate(total_count=Count('id'), total_points=Sum('points'),
                      approved_count=Count('id', filter=Q(contribution_type='task_approved')))
            .order_by('-total_points')[:10]
        )

        task_stats = {
            'total_tasks': total_tasks,
            'open_tasks': open_tasks,
            'in_progress_tasks': in_progress_tasks,
            'submitted_tasks': submitted_tasks,
            'completed_tasks': completed_tasks,
            'rejected_tasks': rejected_tasks,
            'conflicted_tasks': conflicted_tasks,
            'total_submissions': total_submissions,
            'approved_submissions': approved_submissions,
            'completion_rate': completion_rate,
            'conflict_confirm_rate': conflict_confirm_rate,
            'top_task_persons': top_task_persons,
        }

        contribution_stats = {
            'total_contributions': Contribution.objects.count(),
            'total_contributors': Contribution.objects.values('contributor').distinct().count(),
            'total_points': Contribution.objects.aggregate(total=Sum('points'))['total'] or 0,
            'leaderboard': contrib_agg,
        }

        spacetime_stats = _get_spacetime_stats()

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
            'task_stats': task_stats,
            'contribution_stats': contribution_stats,
            'spacetime_stats': spacetime_stats,
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)


PROVINCE_CITY_MAP = {
    '北京': {'province': '北京市', 'city': '北京市'},
    '上海': {'province': '上海市', 'city': '上海市'},
    '天津': {'province': '天津市', 'city': '天津市'},
    '重庆': {'province': '重庆市', 'city': '重庆市'},
    '山东青岛': {'province': '山东省', 'city': '青岛市'},
    '山东济南': {'province': '山东省', 'city': '济南市'},
    '山东烟台': {'province': '山东省', 'city': '烟台市'},
    '山东潍坊': {'province': '山东省', 'city': '潍坊市'},
    '山东': {'province': '山东省', 'city': ''},
    '河北石家庄': {'province': '河北省', 'city': '石家庄市'},
    '河北保定': {'province': '河北省', 'city': '保定市'},
    '河北唐山': {'province': '河北省', 'city': '唐山市'},
    '河北': {'province': '河北省', 'city': ''},
    '河南郑州': {'province': '河南省', 'city': '郑州市'},
    '河南洛阳': {'province': '河南省', 'city': '洛阳市'},
    '河南开封': {'province': '河南省', 'city': '开封市'},
    '河南': {'province': '河南省', 'city': ''},
    '江苏南京': {'province': '江苏省', 'city': '南京市'},
    '江苏苏州': {'province': '江苏省', 'city': '苏州市'},
    '江苏无锡': {'province': '江苏省', 'city': '无锡市'},
    '江苏': {'province': '江苏省', 'city': ''},
    '浙江杭州': {'province': '浙江省', 'city': '杭州市'},
    '浙江宁波': {'province': '浙江省', 'city': '宁波市'},
    '浙江温州': {'province': '浙江省', 'city': '温州市'},
    '浙江': {'province': '浙江省', 'city': ''},
    '广东广州': {'province': '广东省', 'city': '广州市'},
    '广东深圳': {'province': '广东省', 'city': '深圳市'},
    '广东珠海': {'province': '广东省', 'city': '珠海市'},
    '广东': {'province': '广东省', 'city': ''},
    '四川成都': {'province': '四川省', 'city': '成都市'},
    '四川重庆': {'province': '重庆市', 'city': '重庆市'},
    '四川绵阳': {'province': '四川省', 'city': '绵阳市'},
    '四川': {'province': '四川省', 'city': ''},
    '湖南长沙': {'province': '湖南省', 'city': '长沙市'},
    '湖南岳阳': {'province': '湖南省', 'city': '岳阳市'},
    '湖南': {'province': '湖南省', 'city': ''},
    '湖北武汉': {'province': '湖北省', 'city': '武汉市'},
    '湖北宜昌': {'province': '湖北省', 'city': '宜昌市'},
    '湖北': {'province': '湖北省', 'city': ''},
    '陕西西安': {'province': '陕西省', 'city': '西安市'},
    '陕西咸阳': {'province': '陕西省', 'city': '咸阳市'},
    '陕西': {'province': '陕西省', 'city': ''},
    '山西太原': {'province': '山西省', 'city': '太原市'},
    '山西大同': {'province': '山西省', 'city': '大同市'},
    '山西': {'province': '山西省', 'city': ''},
    '辽宁沈阳': {'province': '辽宁省', 'city': '沈阳市'},
    '辽宁大连': {'province': '辽宁省', 'city': '大连市'},
    '辽宁': {'province': '辽宁省', 'city': ''},
    '吉林长春': {'province': '吉林省', 'city': '长春市'},
    '吉林': {'province': '吉林省', 'city': ''},
    '黑龙江哈尔滨': {'province': '黑龙江省', 'city': '哈尔滨市'},
    '黑龙江': {'province': '黑龙江省', 'city': ''},
    '安徽合肥': {'province': '安徽省', 'city': '合肥市'},
    '安徽芜湖': {'province': '安徽省', 'city': '芜湖市'},
    '安徽': {'province': '安徽省', 'city': ''},
    '福建福州': {'province': '福建省', 'city': '福州市'},
    '福建厦门': {'province': '福建省', 'city': '厦门市'},
    '福建': {'province': '福建省', 'city': ''},
    '江西南昌': {'province': '江西省', 'city': '南昌市'},
    '江西': {'province': '江西省', 'city': ''},
    '云南昆明': {'province': '云南省', 'city': '昆明市'},
    '云南大理': {'province': '云南省', 'city': '大理白族自治州'},
    '云南': {'province': '云南省', 'city': ''},
    '贵州贵阳': {'province': '贵州省', 'city': '贵阳市'},
    '贵州': {'province': '贵州省', 'city': ''},
    '广西南宁': {'province': '广西壮族自治区', 'city': '南宁市'},
    '广西桂林': {'province': '广西壮族自治区', 'city': '桂林市'},
    '广西': {'province': '广西壮族自治区', 'city': ''},
    '甘肃兰州': {'province': '甘肃省', 'city': '兰州市'},
    '甘肃': {'province': '甘肃省', 'city': ''},
    '内蒙古呼和浩特': {'province': '内蒙古自治区', 'city': '呼和浩特市'},
    '内蒙古包头': {'province': '内蒙古自治区', 'city': '包头市'},
    '内蒙古': {'province': '内蒙古自治区', 'city': ''},
    '新疆乌鲁木齐': {'province': '新疆维吾尔自治区', 'city': '乌鲁木齐市'},
    '新疆': {'province': '新疆维吾尔自治区', 'city': ''},
    '西藏拉萨': {'province': '西藏自治区', 'city': '拉萨市'},
    '西藏': {'province': '西藏自治区', 'city': ''},
    '宁夏银川': {'province': '宁夏回族自治区', 'city': '银川市'},
    '宁夏': {'province': '宁夏回族自治区', 'city': ''},
    '青海西宁': {'province': '青海省', 'city': '西宁市'},
    '青海': {'province': '青海省', 'city': ''},
    '海南海口': {'province': '海南省', 'city': '海口市'},
    '海南三亚': {'province': '海南省', 'city': '三亚市'},
    '海南': {'province': '海南省', 'city': ''},
    '香港': {'province': '香港特别行政区', 'city': '香港'},
    '澳门': {'province': '澳门特别行政区', 'city': '澳门'},
    '台湾台北': {'province': '台湾省', 'city': '台北市'},
    '台湾': {'province': '台湾省', 'city': ''},
    '青岛': {'province': '山东省', 'city': '青岛市'},
    '济南': {'province': '山东省', 'city': '济南市'},
    '烟台': {'province': '山东省', 'city': '烟台市'},
    '石家庄': {'province': '河北省', 'city': '石家庄市'},
    '保定': {'province': '河北省', 'city': '保定市'},
    '唐山': {'province': '河北省', 'city': '唐山市'},
    '郑州': {'province': '河南省', 'city': '郑州市'},
    '洛阳': {'province': '河南省', 'city': '洛阳市'},
    '开封': {'province': '河南省', 'city': '开封市'},
    '南京': {'province': '江苏省', 'city': '南京市'},
    '苏州': {'province': '江苏省', 'city': '苏州市'},
    '无锡': {'province': '江苏省', 'city': '无锡市'},
    '杭州': {'province': '浙江省', 'city': '杭州市'},
    '宁波': {'province': '浙江省', 'city': '宁波市'},
    '温州': {'province': '浙江省', 'city': '温州市'},
    '广州': {'province': '广东省', 'city': '广州市'},
    '深圳': {'province': '广东省', 'city': '深圳市'},
    '珠海': {'province': '广东省', 'city': '珠海市'},
    '成都': {'province': '四川省', 'city': '成都市'},
    '绵阳': {'province': '四川省', 'city': '绵阳市'},
    '长沙': {'province': '湖南省', 'city': '长沙市'},
    '岳阳': {'province': '湖南省', 'city': '岳阳市'},
    '武汉': {'province': '湖北省', 'city': '武汉市'},
    '宜昌': {'province': '湖北省', 'city': '宜昌市'},
    '西安': {'province': '陕西省', 'city': '西安市'},
    '咸阳': {'province': '陕西省', 'city': '咸阳市'},
    '太原': {'province': '山西省', 'city': '太原市'},
    '大同': {'province': '山西省', 'city': '大同市'},
    '沈阳': {'province': '辽宁省', 'city': '沈阳市'},
    '大连': {'province': '辽宁省', 'city': '大连市'},
    '长春': {'province': '吉林省', 'city': '长春市'},
    '哈尔滨': {'province': '黑龙江省', 'city': '哈尔滨市'},
    '合肥': {'province': '安徽省', 'city': '合肥市'},
    '芜湖': {'province': '安徽省', 'city': '芜湖市'},
    '福州': {'province': '福建省', 'city': '福州市'},
    '厦门': {'province': '福建省', 'city': '厦门市'},
    '南昌': {'province': '江西省', 'city': '南昌市'},
    '昆明': {'province': '云南省', 'city': '昆明市'},
    '贵阳': {'province': '贵州省', 'city': '贵阳市'},
    '南宁': {'province': '广西壮族自治区', 'city': '南宁市'},
    '桂林': {'province': '广西壮族自治区', 'city': '桂林市'},
    '兰州': {'province': '甘肃省', 'city': '兰州市'},
    '呼和浩特': {'province': '内蒙古自治区', 'city': '呼和浩特市'},
    '包头': {'province': '内蒙古自治区', 'city': '包头市'},
    '乌鲁木齐': {'province': '新疆维吾尔自治区', 'city': '乌鲁木齐市'},
    '拉萨': {'province': '西藏自治区', 'city': '拉萨市'},
    '银川': {'province': '宁夏回族自治区', 'city': '银川市'},
    '西宁': {'province': '青海省', 'city': '西宁市'},
    '海口': {'province': '海南省', 'city': '海口市'},
    '三亚': {'province': '海南省', 'city': '三亚市'},
    '台北': {'province': '台湾省', 'city': '台北市'},
    '北京市': {'province': '北京市', 'city': '北京市'},
    '上海市': {'province': '上海市', 'city': '上海市'},
    '天津市': {'province': '天津市', 'city': '天津市'},
    '重庆市': {'province': '重庆市', 'city': '重庆市'},
}


def _parse_location_text(original_name, country='中国'):
    result = {
        'original_name': original_name,
        'standardized_name': '',
        'country': country,
        'province': '',
        'city': '',
        'district': '',
        'town': '',
        'village': '',
        'detail': '',
        'level': 'detail',
        'alias_names': [],
    }

    if not original_name or not original_name.strip():
        return result

    text = original_name.strip()
    text = text.replace(' ', '').replace('　', '')

    matched = False
    sorted_keys = sorted(PROVINCE_CITY_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in text:
            info = PROVINCE_CITY_MAP[key]
            result['province'] = info['province']
            result['city'] = info['city']
            remain = text.replace(key, '', 1)
            if remain:
                result['detail'] = remain
                if '区' in remain or '县' in remain:
                    result['level'] = 'district'
                else:
                    result['level'] = 'detail'
            else:
                if info['city']:
                    result['level'] = 'city'
                else:
                    result['level'] = 'province'
            matched = True
            break

    if not matched:
        result['detail'] = text
        result['level'] = 'detail'

    parts = []
    if result['province']:
        parts.append(result['province'])
    if result['city'] and result['city'] != result['province']:
        parts.append(result['city'])
    if result['district']:
        parts.append(result['district'])
    if result['detail']:
        parts.append(result['detail'])
    result['standardized_name'] = ''.join(parts) or original_name

    result['alias_names'] = [original_name]

    return result


def _get_or_create_location(original_name, country='中国'):
    if not original_name or not original_name.strip():
        return None

    text = original_name.strip()

    existing = StandardizedLocation.objects.filter(
        Q(original_name=text) | Q(standardized_name=text)
    ).first()
    if not existing:
        for loc in StandardizedLocation.objects.all():
            if isinstance(loc.alias_names, list) and text in loc.alias_names:
                existing = loc
                break
    if existing:
        return existing

    parsed = _parse_location_text(text, country)
    try:
        loc = StandardizedLocation.objects.create(**parsed)
        return loc
    except Exception:
        return None


def _year_to_decade(year):
    if not year:
        return ''
    try:
        y = int(year)
        return f'{(y // 10) * 10}s'
    except (ValueError, TypeError):
        return ''


def _check_node_conflict(new_node_data, existing_nodes):
    if not existing_nodes:
        return None, 'none'

    person_id = new_node_data.get('related_person_id')
    node_type = new_node_data.get('node_type')
    new_year = new_node_data.get('year')
    new_location_id = new_node_data.get('location_id')
    new_from_location_id = new_node_data.get('from_location_id')

    for existing in existing_nodes:
        if existing.status == 'rejected':
            continue

        same_person = (
            person_id and existing.related_person_id == person_id
        )
        same_type = node_type and existing.node_type == node_type

        if not (same_person and same_type):
            continue

        year_conflict = False
        location_conflict = False

        if new_year and existing.year and abs(new_year - existing.year) > 5:
            year_conflict = True

        loc_same = (
            (new_location_id and existing.location_id == new_location_id) or
            (not new_location_id and not existing.location_id)
        )
        from_loc_same = (
            (new_from_location_id and existing.from_location_id == new_from_location_id) or
            (not new_from_location_id and not existing.from_location_id)
        )
        if new_location_id and existing.location_id and not loc_same:
            location_conflict = True
        if new_from_location_id and existing.from_location_id and not from_loc_same:
            location_conflict = True

        if year_conflict or location_conflict:
            conflict_field = 'both' if (year_conflict and location_conflict) else (
                'year' if year_conflict else 'location'
            )
            return existing, conflict_field

    return None, 'none'


def _generate_conflict_group_id():
    return f'conflict_{uuid.uuid4().hex[:12]}'


def _create_timeline_node(data):
    existing_qs = TimelineNode.objects.filter(
        related_person_id=data.get('related_person_id'),
        node_type=data.get('node_type'),
        source_type=data.get('source_type'),
        source_id=data.get('source_id'),
    )
    if existing_qs.exists():
        return existing_qs.first(), False

    conflict_check_qs = TimelineNode.objects.filter(
        related_person_id=data.get('related_person_id'),
        node_type=data.get('node_type'),
    )
    conflict_existing, conflict_field = _check_node_conflict(data, list(conflict_check_qs))

    if conflict_existing and conflict_field != 'none':
        group_id = conflict_existing.conflict_version_group or _generate_conflict_group_id()
        if not conflict_existing.conflict_version_group:
            conflict_existing.conflict_version_group = group_id
            conflict_existing.status = 'conflicted'
            conflict_existing.conflict_field = conflict_field
            conflict_existing.save()

        data['status'] = 'conflicted'
        data['conflict_field'] = conflict_field
        data['conflict_version_group'] = group_id

        try:
            cv = ConflictVersion.objects.create(
                related_person_id=data.get('related_person_id'),
                related_photo_id=data.get('related_photo_id'),
                related_memory_id=data.get('related_memory_id'),
                conflict_field='photo_location' if conflict_field in ['location', 'both'] else 'photo_date',
                version_a=f"已有记录: 年份={conflict_existing.year or '未知'}, 地点={conflict_existing.original_location or (conflict_existing.location.standardized_name if conflict_existing.location else '未知')}",
                version_a_author=conflict_existing.created_by,
                version_b=f"新记录: 年份={data.get('year') or '未知'}, 地点={data.get('original_location') or '未知'}",
                version_b_author=data.get('created_by', '系统'),
                description=f'时间线节点冲突: {conflict_field}',
                status='open',
            )
            data['related_conflict_id'] = cv.id
        except Exception:
            pass

    node = TimelineNode.objects.create(**data)
    return node, True


def _sync_nodes_from_person(person):
    created_count = 0

    if person.birth_year or person.birth_place:
        loc = _get_or_create_location(person.birth_place) if person.birth_place else None
        data = {
            'node_type': 'birth',
            'source_type': 'person',
            'source_id': person.id,
            'related_person_id': person.id,
            'title': f'{person.name} 出生',
            'description': f'{person.name} 出生于 {person.birth_year or "年份不详"} 年 {person.birth_place or "地点不详"}',
            'original_location': person.birth_place or '',
            'location_id': loc.id if loc else None,
            'year': person.birth_year,
            'decade': _year_to_decade(person.birth_year),
            'year_unknown': person.birth_year is None,
            'status': 'confirmed' if person.status == 'confirmed' else 'pending',
            'created_by': person.created_by,
        }
        _, created = _create_timeline_node(data)
        if created:
            created_count += 1

    if person.death_year:
        data = {
            'node_type': 'death',
            'source_type': 'person',
            'source_id': person.id,
            'related_person_id': person.id,
            'title': f'{person.name} 逝世',
            'description': f'{person.name} 逝世于 {person.death_year} 年',
            'original_location': '',
            'year': person.death_year,
            'decade': _year_to_decade(person.death_year),
            'year_unknown': False,
            'status': 'confirmed' if person.status == 'confirmed' else 'pending',

            'created_by': person.created_by,
        }
        _, created = _create_timeline_node(data)
        if created:
            created_count += 1

    return created_count


def _sync_nodes_from_migration(migration):
    person = migration.person
    to_loc = _get_or_create_location(migration.to_place) if migration.to_place else None
    from_loc = _get_or_create_location(migration.from_place) if migration.from_place else None

    data = {
        'node_type': 'migration',
        'source_type': 'migration_info',
        'source_id': migration.id,
        'related_person_id': person.id,
        'related_migration_id': migration.id,
        'title': f'{person.name} 迁居',
        'description': f'{migration.from_place or "?"} → {migration.to_place or "?"}' + (f'（{migration.reason}）' if migration.reason else ''),
        'original_location': migration.to_place or '',
        'location_id': to_loc.id if to_loc else None,
        'from_location_id': from_loc.id if from_loc else None,
        'year': migration.move_year,
        'decade': _year_to_decade(migration.move_year),
        'year_unknown': migration.move_year is None,
        'status': 'pending',
        'created_by': migration.added_by,
        'extra_data': {'reason': migration.reason or ''},
    }
    _, created = _create_timeline_node(data)
    return 1 if created else 0


def _sync_nodes_from_photo(photo):
    created_count = 0
    loc = _get_or_create_location(photo.location) if photo.location else None

    people_ids = list(
        PersonInPhoto.objects.filter(photo=photo, person__isnull=False).values_list('person_id', flat=True)
    )

    if not people_ids:
        people_ids = [None]

    for pid in people_ids:
        year = photo.taken_year
        decade = photo.era if photo.era and photo.era != 'unknown' else _year_to_decade(year)

        data = {
            'node_type': 'photo',
            'source_type': 'photo',
            'source_id': photo.id,
            'related_person_id': pid,
            'related_photo_id': photo.id,
            'title': photo.title or f'照片-{photo.id}',
            'description': photo.description or '',
            'original_location': photo.location or '',
            'location_id': loc.id if loc else None,
            'year': year,
            'decade': decade,
            'year_unknown': year is None,
            'status': 'confirmed' if photo.status == 'completed' else 'pending',
            'created_by': photo.uploader,
            'extra_data': {'era': photo.era, 'scene': photo.scene},
        }
        _, created = _create_timeline_node(data)
        if created:
            created_count += 1

    return created_count


def _sync_nodes_from_memory(memory):
    created_count = 0
    loc = _get_or_create_location(memory.occur_place) if memory.occur_place else None

    people_ids = list(memory.related_people.values_list('id', flat=True))
    if not people_ids:
        people_ids = [None]

    for pid in people_ids:
        data = {
            'node_type': 'memory',
            'source_type': 'memory',
            'source_id': memory.id,
            'related_person_id': pid,
            'related_memory_id': memory.id,
            'title': memory.title,
            'description': memory.content[:500],
            'original_location': memory.occur_place or '',
            'location_id': loc.id if loc else None,
            'year': memory.occur_year,
            'decade': _year_to_decade(memory.occur_year),
            'year_unknown': memory.occur_year is None,
            'status': 'confirmed' if memory.status == 'published' else 'pending',
            'created_by': memory.author,
        }
        _, created = _create_timeline_node(data)
        if created:
            created_count += 1

    return created_count


def _sync_nodes_from_task_submission(submission):
    created_count = 0
    task = submission.task
    if task.task_type == 'migration_supplement' and submission.status == 'approved' and task.related_person:
        sd = submission.submission_data or {}
        from_place = sd.get('from_place', '')
        to_place = sd.get('to_place', '')
        move_year = sd.get('move_year')
        to_loc = _get_or_create_location(to_place) if to_place else None
        from_loc = _get_or_create_location(from_place) if from_place else None

        data = {
            'node_type': 'task_result',
            'source_type': 'task_submission',
            'source_id': submission.id,
            'related_person_id': task.related_person_id,
            'title': f'[采集任务] {task.related_person.name} 迁居补注',
            'description': submission.submission_text or str(sd),
            'original_location': to_place,
            'location_id': to_loc.id if to_loc else None,
            'from_location_id': from_loc.id if from_loc else None,
            'year': move_year,
            'decade': _year_to_decade(move_year),
            'year_unknown': move_year is None,
            'status': 'pending',
            'created_by': submission.submitter,
            'extra_data': {'task_id': task.id, 'submission_id': submission.id},
        }
        _, created = _create_timeline_node(data)
        if created:
            created_count += 1

    return created_count


def _sync_all_timeline_nodes():
    total_created = 0
    for person in Person.objects.all():
        total_created += _sync_nodes_from_person(person)
    for migration in MigrationInfo.objects.select_related('person').all():
        total_created += _sync_nodes_from_migration(migration)
    for photo in Photo.objects.all():
        total_created += _sync_nodes_from_photo(photo)
    for memory in MemoryFragment.objects.all():
        total_created += _sync_nodes_from_memory(memory)
    for submission in TaskSubmission.objects.filter(status='approved').select_related('task', 'task__related_person'):
        total_created += _sync_nodes_from_task_submission(submission)
    return total_created


def _get_spacetime_stats():
    try:
        total_nodes = TimelineNode.objects.count()
        confirmed_nodes = TimelineNode.objects.filter(status='confirmed').count()
        pending_nodes = TimelineNode.objects.filter(status='pending').count()
        conflicted_nodes = TimelineNode.objects.filter(status='conflicted').count()

        photos_with_location = Photo.objects.exclude(location='').count()
        total_photos = Photo.objects.count()
        photo_location_rate = round(photos_with_location / total_photos * 100, 1) if total_photos > 0 else 0.0

        location_conflicts_pending = ConflictVersion.objects.filter(
            status='open',
            conflict_field__in=['photo_location', 'photo_date', 'other']
        ).count()

        decade_list = ['1920s', '1930s', '1940s', '1950s', '1960s', '1970s',
                       '1980s', '1990s', '2000s', '2010s', '2020s']
        decade_coverage = []
        for d in decade_list:
            count = TimelineNode.objects.filter(
                Q(decade=d) | Q(year__gte=int(d[:4]), year__lt=int(d[:4]) + 10),
                status__in=['confirmed', 'pending']
            ).count()
            decade_coverage.append({'decade': d, 'label': f'{d[:4]}年代', 'count': count})

        total_persons = Person.objects.count()
        persons_with_nodes = TimelineNode.objects.filter(
            related_person__isnull=False,
            status__in=['confirmed', 'pending']
        ).values('related_person').distinct().count()
        person_coverage_rate = round(persons_with_nodes / total_persons * 100, 1) if total_persons > 0 else 0.0

        top_in_locations = list(
            TimelineNode.objects.filter(
                node_type='migration',
                location__isnull=False,
                status__in=['confirmed', 'pending']
            ).values('location__standardized_name', 'location__province', 'location__city')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        top_in = [
            {'location': t['location__standardized_name'] or f"{t['location__province']}{t['location__city']}",
             'count': t['count']}
            for t in top_in_locations if t['location__standardized_name'] or t['location__province']
        ]

        top_out_locations = list(
            TimelineNode.objects.filter(
                node_type='migration',
                from_location__isnull=False,
                status__in=['confirmed', 'pending']
            ).values('from_location__standardized_name', 'from_location__province', 'from_location__city')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        top_out = [
            {'location': t['from_location__standardized_name'] or f"{t['from_location__province']}{t['from_location__city']}",
             'count': t['count']}
            for t in top_out_locations if t['from_location__standardized_name'] or t['from_location__province']
        ]

        total_locations = StandardizedLocation.objects.count()

        migration_nodes = TimelineNode.objects.filter(node_type='migration').count()
        photo_nodes = TimelineNode.objects.filter(node_type='photo').count()
        memory_nodes = TimelineNode.objects.filter(node_type='memory').count()

        return {
            'total_nodes': total_nodes,
            'confirmed_nodes': confirmed_nodes,
            'pending_nodes': pending_nodes,
            'conflicted_nodes': conflicted_nodes,
            'photos_with_location': photos_with_location,
            'photo_location_rate': photo_location_rate,
            'location_conflicts_pending': location_conflicts_pending,
            'decade_coverage': decade_coverage,
            'persons_with_nodes': persons_with_nodes,
            'person_coverage_rate': person_coverage_rate,
            'top_in_locations': top_in,
            'top_out_locations': top_out,
            'total_locations': total_locations,
            'migration_nodes': migration_nodes,
            'photo_nodes': photo_nodes,
            'memory_nodes': memory_nodes,
        }
    except Exception as e:
        return {
            'total_nodes': 0,
            'confirmed_nodes': 0,
            'pending_nodes': 0,
            'conflicted_nodes': 0,
            'photos_with_location': 0,
            'photo_location_rate': 0.0,
            'location_conflicts_pending': 0,
            'decade_coverage': [],
            'persons_with_nodes': 0,
            'person_coverage_rate': 0.0,
            'top_in_locations': [],
            'top_out_locations': [],
            'total_locations': 0,
            'migration_nodes': 0,
            'photo_nodes': 0,
            'memory_nodes': 0,
            'error': str(e),
        }


class StandardizedLocationViewSet(viewsets.ModelViewSet):
    queryset = StandardizedLocation.objects.all()
    serializer_class = StandardizedLocationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province', 'city', 'level', 'is_verified']

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword', '').strip()
        if not keyword:
            return Response({'count': 0, 'results': []})
        qs = StandardizedLocation.objects.filter(
            Q(original_name__icontains=keyword) |
            Q(standardized_name__icontains=keyword) |
            Q(province__icontains=keyword) |
            Q(city__icontains=keyword) |
            Q(district__icontains=keyword)
        )
        extra_ids = []
        for loc in StandardizedLocation.objects.all():
            if isinstance(loc.alias_names, list) and keyword in ' '.join(loc.alias_names):
                extra_ids.append(loc.id)
        if extra_ids:
            qs = qs | StandardizedLocation.objects.filter(id__in=extra_ids)
        qs = qs.distinct()[:50]
        return Response({
            'count': len(qs),
            'results': StandardizedLocationSerializer(qs, many=True).data
        })

    @action(detail=False, methods=['post'])
    def parse(self, request):
        serializer = LocationParseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        original_name = data['original_name']
        country = data.get('country', '中国')

        try:
            parsed = _parse_location_text(original_name, country)
            existing = StandardizedLocation.objects.filter(
                Q(original_name=original_name) | Q(standardized_name=parsed['standardized_name'])
            ).first()
            if existing:
                return Response({
                    'parsed': parsed,
                    'existing': StandardizedLocationSerializer(existing).data,
                    'is_new': False,
                })
            return Response({
                'parsed': parsed,
                'existing': None,
                'is_new': True,
            })
        except Exception as e:
            return Response({
                'error': f'地点解析失败: {str(e)}',
                'parsed': _parse_location_text(original_name, country),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def parse_and_save(self, request):
        serializer = LocationParseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        loc = _get_or_create_location(data['original_name'], data.get('country', '中国'))
        if not loc:
            return Response({'error': '保存地点失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(StandardizedLocationSerializer(loc).data, status=status.HTTP_201_CREATED)


class TimelineNodeViewSet(viewsets.ModelViewSet):
    queryset = TimelineNode.objects.all()
    serializer_class = TimelineNodeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['node_type', 'source_type', 'status', 'related_person', 'related_photo', 'related_memory', 'decade']

    @action(detail=False, methods=['get'])
    def query(self, request):
        serializer = TimelineQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        params = serializer.validated_data

        qs = TimelineNode.objects.select_related(
            'related_person', 'related_photo', 'related_memory', 'location', 'from_location', 'related_conflict'
        )

        if params.get('person_id'):
            qs = qs.filter(related_person_id=params['person_id'])
        if params.get('photo_id'):
            qs = qs.filter(related_photo_id=params['photo_id'])
        if params.get('memory_id'):
            qs = qs.filter(related_memory_id=params['memory_id'])
        if params.get('decade'):
            qs = qs.filter(
                Q(decade=params['decade']) |
                Q(year__gte=int(params['decade'][:4]), year__lt=int(params['decade'][:4]) + 10)
            )
        if params.get('year_min'):
            qs = qs.filter(Q(year__gte=params['year_min']) | Q(year__isnull=True))
        if params.get('year_max'):
            qs = qs.filter(Q(year__lte=params['year_max']) | Q(year__isnull=True))
        if params.get('location_id'):
            qs = qs.filter(Q(location_id=params['location_id']) | Q(from_location_id=params['location_id']))
        if params.get('location_keyword'):
            kw = params['location_keyword']
            qs = qs.filter(
                Q(original_location__icontains=kw) |
                Q(location__standardized_name__icontains=kw) |
                Q(location__province__icontains=kw) |
                Q(location__city__icontains=kw) |
                Q(from_location__standardized_name__icontains=kw)
            )
        if params.get('node_type'):
            qs = qs.filter(node_type=params['node_type'])
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        elif not params.get('include_conflicted'):
            qs = qs.filter(status__in=['confirmed', 'pending'])

        total = qs.count()

        page = max(1, params.get('page', 1))
        page_size = min(200, max(1, params.get('page_size', 50)))
        start = (page - 1) * page_size
        end = start + page_size
        qs = qs[start:end]

        nodes = list(qs)
        nodes.sort(key=lambda n: n.get_sort_key())

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': TimelineNodeSerializer(nodes, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def aggregate(self, request):
        serializer = TimelineAggregateSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        params = serializer.validated_data
        group_by = params.get('group_by', 'decade')

        qs = TimelineNode.objects.all()
        if params.get('person_id'):
            qs = qs.filter(related_person_id=params['person_id'])
        if not params.get('include_conflicted'):
            qs = qs.filter(status__in=['confirmed', 'pending'])

        if group_by == 'decade':
            decades = ['1920s', '1930s', '1940s', '1950s', '1960s', '1970s',
                       '1980s', '1990s', '2000s', '2010s', '2020s', 'unknown']
            result = []
            for d in decades:
                if d == 'unknown':
                    count = qs.filter(Q(decade='') | Q(decade='unknown') | Q(year__isnull=True)).count()
                else:
                    count = qs.filter(
                        Q(decade=d) | Q(year__gte=int(d[:4]), year__lt=int(d[:4]) + 10)
                    ).count()
                result.append({'decade': d, 'label': f'{d[:4]}年代' if d != 'unknown' else '年代不详', 'count': count})
            return Response({'group_by': 'decade', 'results': result})

        elif group_by == 'year':
            year_data = list(
                qs.exclude(year__isnull=True)
                .values('year')
                .annotate(count=Count('id'))
                .order_by('year')
            )
            return Response({'group_by': 'year', 'results': year_data})

        elif group_by == 'person':
            person_data = list(
                qs.filter(related_person__isnull=False)
                .values('related_person__id', 'related_person__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:50]
            )
            result = [
                {'person_id': p['related_person__id'], 'name': p['related_person__name'], 'count': p['count']}
                for p in person_data
            ]
            return Response({'group_by': 'person', 'results': result})

        elif group_by == 'location':
            loc_data = list(
                qs.filter(location__isnull=False)
                .values('location__id', 'location__standardized_name', 'location__province', 'location__city')
                .annotate(count=Count('id'))
                .order_by('-count')[:50]
            )
            result = [
                {
                    'location_id': l['location__id'],
                    'name': l['location__standardized_name'] or f"{l['location__province']}{l['location__city']}",
                    'count': l['count']
                }
                for l in loc_data
            ]
            return Response({'group_by': 'location', 'results': result})

        elif group_by == 'node_type':
            type_data = list(qs.values('node_type').annotate(count=Count('id')))
            type_label_map = dict(TimelineNode.NODE_TYPE_CHOICES)
            result = [
                {'node_type': t['node_type'], 'label': type_label_map.get(t['node_type'], t['node_type']), 'count': t['count']}
                for t in type_data
            ]
            return Response({'group_by': 'node_type', 'results': result})

        return Response({'group_by': group_by, 'results': []})

    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        group_ids = TimelineNode.objects.exclude(
            conflict_version_group=''
        ).values_list('conflict_version_group', flat=True).distinct()

        conflict_groups = []
        for gid in group_ids:
            nodes = TimelineNode.objects.filter(
                conflict_version_group=gid
            ).select_related('related_person', 'related_conflict')
            if not nodes.exists():
                continue
            first = nodes.first()
            conflict_groups.append({
                'group_id': gid,
                'related_person_id': first.related_person_id,
                'related_person_name': first.related_person.name if first.related_person else None,
                'conflict_field': first.conflict_field,
                'conflict_field_display': first.get_conflict_field_display(),
                'node_count': nodes.count(),
                'nodes': TimelineNodeSerializer(nodes, many=True).data,
                'related_conflict_id': first.related_conflict_id,
            })

        return Response({
            'count': len(conflict_groups),
            'results': conflict_groups,
        })

    @action(detail=False, methods=['post'])
    def sync(self, request):
        try:
            source = request.data.get('source', 'all')
            created = 0
            if source in ['all', 'person']:
                for p in Person.objects.all():
                    created += _sync_nodes_from_person(p)
            if source in ['all', 'migration']:
                for m in MigrationInfo.objects.select_related('person').all():
                    created += _sync_nodes_from_migration(m)
            if source in ['all', 'photo']:
                for ph in Photo.objects.all():
                    created += _sync_nodes_from_photo(ph)
            if source in ['all', 'memory']:
                for mem in MemoryFragment.objects.all():
                    created += _sync_nodes_from_memory(mem)
            if source in ['all', 'task']:
                for s in TaskSubmission.objects.filter(status='approved').select_related('task', 'task__related_person'):
                    created += _sync_nodes_from_task_submission(s)

            return Response({
                'status': 'synced',
                'source': source,
                'created_count': created,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        node = self.get_object()
        serializer = NodeCreateTaskSerializer(data={**request.data, 'node_id': node.id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        title = data.get('title') or f'时空节点补注：{node.title}'
        desc = data.get('description') or f'针对时间线节点的采集任务。\n节点：{node.title}\n时间：{node.year or "年份不详"}\n地点：{node.original_location or (node.location.standardized_name if node.location else "地点不详")}'

        task = CollectionTask(
            task_type=data['task_type'],
            title=title,
            description=desc,
            source_type='person' if node.related_person else ('photo' if node.related_photo else 'memory'),
            related_person=node.related_person,
            related_photo=node.related_photo,
            related_memory=node.related_memory,
            extra_context={'timeline_node_id': node.id, 'node_title': node.title},
            assign_type=data['assign_type'],
            assigned_to=data.get('assigned_to', ''),
            created_by=data.get('created_by', '系统'),
            status='assigned' if data['assign_type'] == 'specific' and data.get('assigned_to') else 'open',
            priority=10,
        )
        task.save()

        return Response({
            'status': 'created',
            'task': CollectionTaskSerializer(task).data,
        })


class SpaceArchiveView(APIView):
    def get(self, request):
        serializer = SpaceArchiveQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        params = serializer.validated_data

        qs = TimelineNode.objects.select_related(
            'related_person', 'related_photo', 'related_memory',
            'related_migration', 'location', 'from_location', 'related_conflict'
        )

        if params.get('person_id'):
            qs = qs.filter(related_person_id=params['person_id'])

        statuses = ['confirmed', 'pending']
        if params.get('include_conflicted'):
            statuses.append('conflicted')
        if params.get('include_rejected'):
            statuses.append('rejected')
        qs = qs.filter(status__in=statuses)

        nodes = list(qs)
        nodes.sort(key=lambda n: n.get_sort_key())

        persons = {}
        locations = set()
        decades = set()

        for node in nodes:
            if node.related_person_id:
                if node.related_person_id not in persons:
                    persons[node.related_person_id] = {
                        'id': node.related_person_id,
                        'name': node.related_person.name if node.related_person else '',
                        'birth_year': node.related_person.birth_year if node.related_person else None,
                        'death_year': node.related_person.death_year if node.related_person else None,
                        'node_count': 0,
                    }
                persons[node.related_person_id]['node_count'] += 1
            if node.location_id:
                locations.add(node.location_id)
            if node.from_location_id:
                locations.add(node.from_location_id)
            if node.decade:
                decades.add(node.decade)

        person_list = sorted(persons.values(), key=lambda p: p.get('birth_year') or 9999)

        loc_objs = list(StandardizedLocation.objects.filter(id__in=locations))
        location_map = {loc.id: StandardizedLocationSerializer(loc).data for loc in loc_objs}

        decade_list = sorted(decades)

        conflict_count = TimelineNode.objects.filter(status='conflicted').count()
        if params.get('person_id'):
            conflict_count = TimelineNode.objects.filter(
                status='conflicted',
                related_person_id=params['person_id']
            ).count()

        return Response({
            'person_id': params.get('person_id'),
            'total_nodes': len(nodes),
            'conflict_count': conflict_count,
            'timeline': TimelineNodeSerializer(nodes, many=True).data,
            'persons': person_list,
            'locations': location_map,
            'decades': decade_list,
        })


class SpacetimeStatsView(APIView):
    def get(self, request):
        stats = _get_spacetime_stats()
        return Response(stats)
