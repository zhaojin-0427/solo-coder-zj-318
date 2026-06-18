import django_filters
from django.db.models import Q
from .models import Photo, Person, FamilyArtifact


class ArtifactFilter(django_filters.FilterSet):
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')
    has_image = django_filters.BooleanFilter(method='filter_has_image')
    has_persons = django_filters.BooleanFilter(method='filter_has_persons')
    has_story = django_filters.BooleanFilter(method='filter_has_story')
    has_dispute = django_filters.BooleanFilter(method='filter_has_dispute')
    custodian = django_filters.CharFilter(field_name='current_custodian', lookup_expr='icontains')

    class Meta:
        model = FamilyArtifact
        fields = ['artifact_type', 'era', 'status', 'material', 'condition']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(story__icontains=value) |
            Q(location__icontains=value) |
            Q(current_custodian__icontains=value) |
            Q(artifact_no__icontains=value) |
            Q(tags__contains=[value])
        ).distinct()

    def filter_has_image(self, queryset, name, value):
        if value:
            return queryset.filter(Q(image__isnull=False) & ~Q(image='')).distinct()
        else:
            return queryset.filter(Q(image__isnull=True) | Q(image='')).distinct()

    def filter_has_persons(self, queryset, name, value):
        if value:
            return queryset.filter(related_person_relations__isnull=False).distinct()
        else:
            return queryset.filter(related_person_relations__isnull=True).distinct()

    def filter_has_story(self, queryset, name, value):
        if value:
            return queryset.filter(Q(story__isnull=False) & ~Q(story='')).distinct()
        else:
            return queryset.filter(Q(story__isnull=True) | Q(story='')).distinct()

    def filter_has_dispute(self, queryset, name, value):
        return queryset.filter(has_dispute=value).distinct()


class PhotoFilter(django_filters.FilterSet):
    taken_year_min = django_filters.NumberFilter(field_name='taken_year', lookup_expr='gte')
    taken_year_max = django_filters.NumberFilter(field_name='taken_year', lookup_expr='lte')
    has_people = django_filters.BooleanFilter(method='filter_has_people')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Photo
        fields = ['era', 'scene', 'source', 'status']

    def filter_has_people(self, queryset, name, value):
        if value:
            return queryset.filter(people_in_photo__isnull=False).distinct()
        else:
            return queryset.filter(people_in_photo__isnull=True).distinct()

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(location__icontains=value) |
            Q(people_in_photo__person_name_override__icontains=value) |
            Q(people_in_photo__person__name__icontains=value)
        ).distinct()


class PersonFilter(django_filters.FilterSet):
    birth_year_min = django_filters.NumberFilter(field_name='birth_year', lookup_expr='gte')
    birth_year_max = django_filters.NumberFilter(field_name='birth_year', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Person
        fields = ['gender', 'status']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(aliases__alias_name__icontains=value) |
            Q(birth_place__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
