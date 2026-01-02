from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    token = serializers.CharField()
    name = serializers.CharField(max_length=120)
    role = serializers.CharField(max_length=120)
    curp = serializers.CharField(max_length=18)
    site_id = serializers.IntegerField()

class IdentifySerializer(serializers.Serializer):
    token = serializers.CharField()
    curp = serializers.CharField(max_length=18)

class SubmitSerializer(serializers.Serializer):
    token = serializers.CharField()
    curp = serializers.CharField(max_length=18)
    answers = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
