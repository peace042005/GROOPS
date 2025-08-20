from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Group, GroupClick,GroupFeedback,GroupScroll,Categorie,Pays,Notification,Device
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
import requests

def envoyer_notification_expo(push_token, title, body, data=None):
    """Envoie une notification push via l’API Expo"""
    if not push_token:
        return None

    message = {
        "to": push_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {}
    }

    response = requests.post(
        "https://exp.host/--/api/v2/push/send",
        json=message,
        headers={"Content-Type": "application/json"}
    )
    return response.json()



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

    def create(self, validated_data):
        # Associer le créateur depuis le contexte (request.user)
        user = self.context['request'].user
        group = Group.objects.create(createur=user, **validated_data)

        # Créer la notification
        utilisateurs = User.objects.all()
        notifications = [
            Notification(
                destinataire=u,
                groupe=group,
                message=f"Un nouveau groupe a été créé : {group.name}"
            )
            for u in utilisateurs
        ]
        Notification.objects.bulk_create(notifications)

        for u in utilisateurs:
            if u.expo_push_token:
                envoyer_notification_expo(
                    u.expo_push_token,
                    title="Nouveau groupe 🎉",
                    body=f"{group.name} vient d’être créé !",
                    data={"groupe_id": group.id}
                )
        return group
    
    
class NotificationSerializer(serializers.ModelSerializer):
    groupe_name = serializers.SerializerMethodField()
    groupe_id = serializers.SerializerMethodField()  # Champ explicite pour l'ID du groupe

    class Meta:
        model = Notification
        fields = [
            'id',
            'destinataire',
            'groupe',
            'groupe_id',
            'groupe_name',
            'message',
            'lue',
            'created_at'
        ]
        read_only_fields = [
            'id', 'destinataire', 'groupe', 'groupe_id', 'groupe_name', 'destinataire_email', 'created_at'
        ]

    def get_groupe_name(self, obj):
        return obj.groupe.name if obj.groupe else None


    def get_groupe_id(self, obj):
        return obj.groupe.id if obj.groupe else None
    

class AuthenticationSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        token=attrs.pop('token',None)
        data= super().validate(attrs)
        user=self.user
        if token :
            Device.objects.update_or_create(
                 user=user,
                 token=token,
                 defaults={"is_active": True}
                )
        return data