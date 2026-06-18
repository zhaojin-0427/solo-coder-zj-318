import hashlib
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
    CollectionTask, TaskSubmission, Contribution
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
    ContributionRankingSerializer
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
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)
