from django.contrib import admin
from .models import (
    Person, Alias, MigrationInfo, Relationship, Photo,
    PersonInPhoto, MemoryFragment, ConflictVersion, FamilyConfirmation
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'birth_year', 'death_year', 'status', 'created_at')
    list_filter = ('gender', 'status')
    search_fields = ('name', 'birth_place')


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ('person', 'alias_name', 'usage_context', 'added_by')
    search_fields = ('alias_name', 'person__name')


@admin.register(MigrationInfo)
class MigrationInfoAdmin(admin.ModelAdmin):
    list_display = ('person', 'move_year', 'from_place', 'to_place')
    search_fields = ('person__name', 'from_place', 'to_place')


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_person', 'relation_type', 'to_person', 'relation_note')
    list_filter = ('relation_type',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'era', 'scene', 'source', 'taken_year', 'status', 'uploader')
    list_filter = ('era', 'scene', 'source', 'status')
    search_fields = ('title', 'location', 'description')


@admin.register(PersonInPhoto)
class PersonInPhotoAdmin(admin.ModelAdmin):
    list_display = ('photo', 'person', 'person_name_override', 'position_note', 'old_title')
    search_fields = ('person_name_override', 'position_note', 'old_title')


@admin.register(MemoryFragment)
class MemoryFragmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'occur_year', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content')


@admin.register(ConflictVersion)
class ConflictVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'conflict_field', 'status', 'created_at')
    list_filter = ('conflict_field', 'status')


@admin.register(FamilyConfirmation)
class FamilyConfirmationAdmin(admin.ModelAdmin):
    list_display = ('title', 'confirm_type', 'status', 'vote_approve', 'vote_reject', 'proposer')
    list_filter = ('confirm_type', 'status')
