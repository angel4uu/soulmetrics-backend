from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'age', 'occupation')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            age=validated_data.get('age'),
            occupation=validated_data.get('occupation')
        )
        return user


class PredictionInputSerializer(serializers.Serializer):
    EXT1 = serializers.IntegerField()
    EXT3 = serializers.IntegerField()
    EXT5 = serializers.IntegerField()
    AGR1 = serializers.IntegerField()
    AGR3 = serializers.IntegerField()
    AGR5 = serializers.IntegerField()
    CSN1 = serializers.IntegerField()
    CSN3 = serializers.IntegerField()
    CSN5 = serializers.IntegerField()
    EST1 = serializers.IntegerField()
    EST3 = serializers.IntegerField()
    EST5 = serializers.IntegerField()
    OPN1 = serializers.IntegerField()
    OPN3 = serializers.IntegerField()
    OPN5 = serializers.IntegerField()
