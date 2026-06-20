from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password = validated_data['password'])
        return user

class PredictionInputSerializer(serializers.Serializer):
    EXT1 = serializers.IntegerField(); EXT3 = serializers.IntegerField(); EXT5 = serializers.IntegerField()
    AGR1 = serializers.IntegerField(); AGR3 = serializers.IntegerField(); AGR5 = serializers.IntegerField()
    CSN1 = serializers.IntegerField(); CSN3 = serializers.IntegerField(); CSN5 = serializers.IntegerField()
    EST1 = serializers.IntegerField(); EST3 = serializers.IntegerField(); EST5 = serializers.IntegerField()
    OPN1 = serializers.IntegerField(); OPN3 = serializers.IntegerField(); OPN5 = serializers.IntegerField()
    EXT_E = serializers.IntegerField(); AGR_E = serializers.IntegerField(); CSN_E = serializers.IntegerField()
    EST_E = serializers.IntegerField(); OPN_E = serializers.IntegerField()
