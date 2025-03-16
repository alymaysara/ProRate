from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Professor, Module, Rating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ["id", "username", "email"]


class ProfessorSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()  # Use SerializerMethodField

    class Meta:
        model = Professor
        fields = ['identifier', 'name', 'avg_rating']

    def get_avg_rating(self, obj):
        avg = getattr(obj, 'avg_rating', None)
        if avg is None:
            return "no ratings"
        return round(avg)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if rep.get("avg_rating") is None:
            rep["avg_rating"] = "no ratings"
        return rep

class ModuleSerializer(serializers.ModelSerializer):
    professors = ProfessorSerializer(many=True)

    class Meta:
        model = Module
        fields = ['code', 'name', 'semester', 'year', 'professors']

class RatingSerializer(serializers.ModelSerializer):
    professor = serializers.SlugRelatedField(
            slug_field='identifier',
            queryset=Professor.objects.all()
            )
    module = serializers.SlugRelatedField(
            slug_field='code',
            queryset=Module.objects.all()
            )
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ('user',)
    
    def validate(self, data):
        # Retrieve the current user from the serializer context.
        user = self.context['request'].user
        professor = data['professor']
        module = data['module']
        # Check if a rating for this professor and module already exists for this user.
        if Rating.objects.filter(user=user, professor=professor, module=module).exists():
            raise serializers.ValidationError("You have already rated this professor for this module.")
        return data
