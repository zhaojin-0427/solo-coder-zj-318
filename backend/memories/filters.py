import django_filters
from django.db.models import Q
from .models import Photo, Person


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
