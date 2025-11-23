from .models import Organization, Course, Enrollment
from rest_framework import serializers


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request.user != instance.owner:
            raise serializers.ValidationError("You do not have permission to update this organization.")
        return super().update(instance, validated_data)


class CourseSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('organization', 'created_at')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['organization'] = request.user.organizations.first()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request.user.role != 'organization':
            raise serializers.ValidationError("You do not have permission to update this course.")
        return super().update(instance, validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_name', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
