from rest_framework import serializers
from .models import Group, GroupClick,GroupFeedback,GroupScroll,Categorie,Pays
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

from rest_framework import serializers
from .models import Group, GroupClick, GroupFeedback, GroupScroll
from django.contrib.auth import get_user_model

User = get_user_model()


# 🔐 UtilisateurSerializer
class UtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'telephone','profile', 'pays', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom']

class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ['id', 'nom']

# ✅ GroupClickSerializer
class GroupClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupClick
        fields = ['id', 'group','cliquer','user_id','created_at']
        read_only_fields = ['id', 'created_at']



# ✅ GroupFeedbackSerializer (corrigé: commentaire au lieu de message)
class GroupFeedbackSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GroupFeedback
        fields = ['id','type', 'group', 'user', 'commentaire', 'note', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

# ✅ GroupScrollSerializer
class GroupScrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupScroll
        fields = ['id', 'group', 'user_id', 'created_at']
        read_only_fields = ['id', 'created_at']

        
        
# ✅ GroupSerializer (avec noms corrigés et champs automatiques en read-only)
class GroupSerializer(serializers.ModelSerializer):
    createur = serializers.PrimaryKeyRelatedField(read_only=True)
    clicks = GroupClickSerializer(read_only=True, many=True)
    scrolls = GroupScrollSerializer(read_only=True, many=True)
    feedbacks = GroupFeedbackSerializer(read_only=True, many=True)
    pays_name = serializers.SerializerMethodField()
    categorie_name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id', 'createur', 'name', 'description', 'link',
            'categorie', 'pays', 'platform', 'clicks', 'scrolls', 'feedbacks',
            'created_at', 'pays_name', 'categorie_name'
        ]
        read_only_fields = [
            'id', 'createur', 'clicks', 'scrolls', 'feedbacks', 'created_at'
        ]

    def get_pays_name(self, obj):
        return obj.pays.nom if obj.pays else None

    def get_categorie_name(self, obj):
        return obj.categorie.nom if obj.categorie else None

