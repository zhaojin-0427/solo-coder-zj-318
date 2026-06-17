from rest_framework import serializers
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation
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
