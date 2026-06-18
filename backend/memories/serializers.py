from rest_framework import serializers
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation,
    CollectionTask, TaskSubmission, Contribution,
    StandardizedLocation, TimelineNode
)


class AliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = '__all__'


class MigrationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationInfo
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):
    from_person_name = serializers.CharField(source='from_person.name', read_only=True)
    to_person_name = serializers.CharField(source='to_person.name', read_only=True)
    relation_type_display = serializers.CharField(source='get_relation_type_display', read_only=True)

    class Meta:
        model = Relationship
        fields = '__all__'


class PersonSimpleSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'name', 'gender', 'avatar', 'avatar_url', 'status']

    def get_avatar_url(self, obj):
        if obj.avatar:
            try:
                return obj.avatar.url
            except ValueError:
                return None
        return None


class PersonSerializer(serializers.ModelSerializer):
    aliases = AliasSerializer(many=True, read_only=True)
    migrations = MigrationInfoSerializer(many=True, read_only=True)
    relationships_from = RelationshipSerializer(many=True, read_only=True)
    relationship_count = serializers.IntegerField(read_only=True)
    photo_count = serializers.IntegerField(read_only=True)
    memory_count = serializers.IntegerField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = '__all__'

    def get_avatar_url(self, obj):
        if obj.avatar:
            try:
                return obj.avatar.url
            except ValueError:
                return None
        return None


class PersonInPhotoSerializer(serializers.ModelSerializer):
    person_detail = PersonSimpleSerializer(source='person', read_only=True)
    photo_title = serializers.CharField(source='photo.title', read_only=True)
    photo_image = serializers.SerializerMethodField()

    class Meta:
        model = PersonInPhoto
        fields = '__all__'

    def get_photo_image(self, obj):
        if obj.photo and obj.photo.image:
            try:
                return obj.photo.image.url
            except ValueError:
                return None
        return None


class PhotoSerializer(serializers.ModelSerializer):
    people_in_photo = PersonInPhotoSerializer(many=True, read_only=True)
    era_display = serializers.CharField(source='get_era_display', read_only=True)
    scene_display = serializers.CharField(source='get_scene_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    person_count = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except ValueError:
                return None
        return None


class PhotoSimpleSerializer(serializers.ModelSerializer):
    era_display = serializers.CharField(source='get_era_display', read_only=True)
    scene_display = serializers.CharField(source='get_scene_display', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'title', 'image', 'image_url', 'era', 'era_display', 'scene', 'scene_display', 'taken_year']

    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except ValueError:
                return None
        return None


class MemoryFragmentSerializer(serializers.ModelSerializer):
    related_photos_detail = PhotoSimpleSerializer(source='related_photos', many=True, read_only=True)
    related_people_detail = PersonSimpleSerializer(source='related_people', many=True, read_only=True)
    related_photos = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Photo.objects.all(), required=False, allow_empty=True
    )
    related_people = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Person.objects.all(), required=False, allow_empty=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MemoryFragment
        fields = '__all__'


class ConflictVersionSerializer(serializers.ModelSerializer):
    conflict_field_display = serializers.CharField(source='get_conflict_field_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    related_person_name = serializers.CharField(source='related_person.name', read_only=True, allow_null=True)
    related_photo_title = serializers.CharField(source='related_photo.title', read_only=True, allow_null=True)
    related_memory_title = serializers.CharField(source='related_memory.title', read_only=True, allow_null=True)

    class Meta:
        model = ConflictVersion
        fields = '__all__'


class FamilyConfirmationSerializer(serializers.ModelSerializer):
    confirm_type_display = serializers.CharField(source='get_confirm_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FamilyConfirmation
        fields = '__all__'


class StatsSerializer(serializers.Serializer):
    total_photos = serializers.IntegerField()
    total_persons = serializers.IntegerField()
    pending_persons = serializers.IntegerField()
    total_memories = serializers.IntegerField()
    open_conflicts = serializers.IntegerField()
    pending_confirmations = serializers.IntegerField()
    era_coverage = serializers.ListField()
    top_persons = serializers.ListField()
    annotation_completion = serializers.DictField()
    clue_stats = serializers.DictField()


class CluePhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'title', 'image', 'image_url', 'era', 'taken_year', 'scene']

    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except ValueError:
                return None
        return None


class ClueItemSerializer(serializers.ModelSerializer):
    photo_detail = CluePhotoSerializer(source='photo', read_only=True)

    class Meta:
        model = PersonInPhoto
        fields = ['id', 'photo', 'photo_detail', 'position_note', 'old_title', 'role_note', 'added_by', 'created_at']


class ClueSerializer(serializers.Serializer):
    clue_name = serializers.CharField()
    clue_key = serializers.CharField()
    count = serializers.IntegerField()
    items = ClueItemSerializer(many=True)
    first_seen = serializers.DateTimeField()
    last_seen = serializers.DateTimeField()
    position_notes = serializers.ListField()
    old_titles = serializers.ListField()


class ClaimClueSerializer(serializers.Serializer):
    clue_key = serializers.CharField(required=False)
    clue_keys = serializers.ListField(required=False, child=serializers.CharField())
    mode = serializers.ChoiceField(choices=['existing', 'new'])
    person_id = serializers.IntegerField(required=False, allow_null=True)
    person_data = serializers.DictField(required=False)
    add_as_alias = serializers.BooleanField(default=True)
    claimed_by = serializers.CharField(default='家属')

    def validate(self, data):
        if not data.get('clue_key') and not data.get('clue_keys'):
            raise serializers.ValidationError('clue_key 或 clue_keys 必须提供一个')
        if data['mode'] == 'existing' and not data.get('person_id'):
            raise serializers.ValidationError('认领已有人物时必须提供 person_id')
        if data['mode'] == 'new' and not data.get('person_data'):
            raise serializers.ValidationError('认领新建人物时必须提供 person_data')
        return data


class ClaimResultSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    person_id = serializers.IntegerField()
    person_name = serializers.CharField()
    claimed_count = serializers.IntegerField()
    updated_photos = serializers.ListField()
    message = serializers.CharField()


class CollectionTaskSerializer(serializers.ModelSerializer):
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assign_type_display = serializers.CharField(source='get_assign_type_display', read_only=True)
    related_photo_detail = PhotoSimpleSerializer(source='related_photo', read_only=True, allow_null=True)
    related_person_detail = PersonSimpleSerializer(source='related_person', read_only=True, allow_null=True)
    related_memory_title = serializers.CharField(source='related_memory.title', read_only=True, allow_null=True)
    submission_count = serializers.IntegerField(read_only=True, default=0)
    has_submission = serializers.SerializerMethodField()

    class Meta:
        model = CollectionTask
        fields = '__all__'

    def get_has_submission(self, obj):
        return obj.submissions.exists()


class TaskSubmissionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_type = serializers.CharField(source='task.task_type', read_only=True)
    task_type_display = serializers.CharField(source='task.get_task_type_display', read_only=True)

    class Meta:
        model = TaskSubmission
        fields = '__all__'


class ContributionSerializer(serializers.ModelSerializer):
    contribution_type_display = serializers.CharField(source='get_contribution_type_display', read_only=True)

    class Meta:
        model = Contribution
        fields = '__all__'


class TaskStatsSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    open_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    submitted_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    rejected_tasks = serializers.IntegerField()
    conflicted_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    conflict_rate = serializers.FloatField()
    total_submissions = serializers.IntegerField()
    approved_submissions = serializers.IntegerField()
    contribution_leaderboard = serializers.ListField()
    top_task_persons = serializers.ListField()
    task_type_distribution = serializers.ListField()


class TaskClaimSerializer(serializers.Serializer):
    claimed_by = serializers.CharField(required=True, max_length=100)


class TaskSubmitSerializer(serializers.Serializer):
    submitter = serializers.CharField(required=True, max_length=100)
    submission_data = serializers.DictField(required=False, default=dict)
    submission_text = serializers.CharField(required=False, allow_blank=True, default='')


class TaskReviewSerializer(serializers.Serializer):
    reviewer = serializers.CharField(required=True, max_length=100)
    action = serializers.ChoiceField(choices=['approve', 'reject', 'to_conflict'])
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class GenerateTasksSerializer(serializers.Serializer):
    source_type = serializers.ChoiceField(choices=['photo', 'person', 'memory', 'all'])
    source_id = serializers.IntegerField(required=False, allow_null=True)
    task_types = serializers.ListField(
        required=False,
        child=serializers.ChoiceField(choices=[
            'identity_confirm', 'old_name_supplement',
            'migration_supplement', 'event_narration', 'relation_verify'
        ]),
        default=[]
    )
    assign_type = serializers.ChoiceField(choices=['family', 'specific'], default='family')
    assigned_to = serializers.CharField(required=False, allow_blank=True, default='')
    created_by = serializers.CharField(required=False, default='系统')


class ContributionRankingSerializer(serializers.Serializer):
    contributor = serializers.CharField()
    total_points = serializers.IntegerField()
    task_count = serializers.IntegerField()
    task_approved_count = serializers.IntegerField()
    contribution_detail = serializers.ListField()


class StatsSerializer(serializers.Serializer):
    total_photos = serializers.IntegerField()
    total_persons = serializers.IntegerField()
    pending_persons = serializers.IntegerField()
    total_memories = serializers.IntegerField()
    open_conflicts = serializers.IntegerField()
    pending_confirmations = serializers.IntegerField()
    era_coverage = serializers.ListField()
    top_persons = serializers.ListField()
    annotation_completion = serializers.DictField()
    clue_stats = serializers.DictField()
    task_stats = serializers.DictField(required=False)
    contribution_stats = serializers.DictField(required=False)
    spacetime_stats = serializers.DictField(required=False)


class StandardizedLocationSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = StandardizedLocation
        fields = '__all__'

    def get_full_address(self, obj):
        return obj.get_full_address()


class LocationSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardizedLocation
        fields = ['id', 'standardized_name', 'province', 'city', 'district', 'latitude', 'longitude']


class LocationParseSerializer(serializers.Serializer):
    original_name = serializers.CharField(required=True, max_length=500)
    country = serializers.CharField(required=False, default='中国', max_length=100)


class TimelineNodeSerializer(serializers.ModelSerializer):
    node_type_display = serializers.CharField(source='get_node_type_display', read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    conflict_field_display = serializers.CharField(source='get_conflict_field_display', read_only=True)

    related_person_detail = PersonSimpleSerializer(source='related_person', read_only=True, allow_null=True)
    related_photo_detail = PhotoSimpleSerializer(source='related_photo', read_only=True, allow_null=True)
    related_memory_title = serializers.CharField(source='related_memory.title', read_only=True, allow_null=True)
    location_detail = LocationSimpleSerializer(source='location', read_only=True, allow_null=True)
    from_location_detail = LocationSimpleSerializer(source='from_location', read_only=True, allow_null=True)
    related_conflict_detail = ConflictVersionSerializer(source='related_conflict', read_only=True, allow_null=True)

    class Meta:
        model = TimelineNode
        fields = '__all__'


class TimelineQuerySerializer(serializers.Serializer):
    person_id = serializers.IntegerField(required=False, allow_null=True)
    photo_id = serializers.IntegerField(required=False, allow_null=True)
    memory_id = serializers.IntegerField(required=False, allow_null=True)
    decade = serializers.CharField(required=False, allow_null=True, max_length=20)
    year_min = serializers.IntegerField(required=False, allow_null=True)
    year_max = serializers.IntegerField(required=False, allow_null=True)
    location_id = serializers.IntegerField(required=False, allow_null=True)
    location_keyword = serializers.CharField(required=False, allow_null=True, max_length=200)
    node_type = serializers.CharField(required=False, allow_null=True, max_length=30)
    status = serializers.CharField(required=False, allow_null=True, max_length=20)
    include_conflicted = serializers.BooleanField(required=False, default=False)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=50)


class TimelineAggregateSerializer(serializers.Serializer):
    group_by = serializers.ChoiceField(
        choices=['decade', 'person', 'location', 'node_type', 'year'],
        required=False,
        default='decade'
    )
    person_id = serializers.IntegerField(required=False, allow_null=True)
    include_conflicted = serializers.BooleanField(required=False, default=False)


class SpaceArchiveQuerySerializer(serializers.Serializer):
    person_id = serializers.IntegerField(required=False, allow_null=True)
    include_conflicted = serializers.BooleanField(required=False, default=False)
    include_rejected = serializers.BooleanField(required=False, default=False)


class NodeCreateTaskSerializer(serializers.Serializer):
    node_id = serializers.IntegerField(required=True)
    task_type = serializers.ChoiceField(
        choices=['identity_confirm', 'old_name_supplement', 'migration_supplement', 'event_narration', 'relation_verify'],
        required=True
    )
    title = serializers.CharField(required=False, max_length=300, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    assign_type = serializers.ChoiceField(choices=['family', 'specific'], required=False, default='family')
    assigned_to = serializers.CharField(required=False, allow_blank=True, default='')
    created_by = serializers.CharField(required=False, default='系统', max_length=100)
