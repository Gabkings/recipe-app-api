from rest_framework import serializers
from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for Tags objects '''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'user',)
        read_only_fields = ('id', )