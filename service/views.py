from rest_framework.views import APIView
from rest_framework import generics, permissions, status,viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Group, GroupClick, GroupScroll, GroupFeedback,Categorie,Pays,Notification,Device
import random
from django.core.cache import cache
from django.core.mail import send_mail
from .serializer import (
    GroupSerializer,
    GroupClickSerializer,
    GroupScrollSerializer,
    GroupFeedbackSerializer,
    UtilisateurSerializer,
    CategorieSerializer,
    PaysSerializer,
    NotificationSerializer,
    AuthenticationSerializer
)
from django.contrib.auth import get_user_model
User=get_user_model()

class AuthenticationView(TokenObtainPairView):
    serializer_class=AuthenticationSerializer

class CategorieListView(generics.ListAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class PaysListView(generics.ListAPIView):
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
    
class RegisterUserView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = []  # public

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ModifyUserView(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]  # public
    
class GetUserConnect(APIView):
    # Option 1 (mieux) : utilise les permissions DRF
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Aucun utilisateur avec cet email."}, status=status.HTTP_404_NOT_FOUND)

        code = str(random.randint(100000, 999999))
        cache.set(f"reset_code:{email}", code, timeout=600)  # 600s = 10 minutes

        send_mail(
            "Code de réinitialisation de mot de passe",
            f"Voici votre code : {code}",
            "tonapp@example.com",
            [email],
            fail_silently=False,
        )

        return Response({"detail": "Code envoyé par email."}, status=status.HTTP_200_OK)


from django.contrib.auth.hashers import make_password

class VerifyCodeView(APIView):
    def post(self,request):
        email=request.data.get('email')
        code=request.data.get('code')
        if not all([email,code]):
            return Response({"detail": "Champs requis : email, code"}, status=status.HTTP_400_BAD_REQUEST)
        saved_code = cache.get(f"reset_code:{email}")
        if code != saved_code:
            return Response({"detail": "Code invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "code verifier"}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not all([email, code, new_password]):
            return Response({"detail": "Champs requis : email, code, nouveau mot de passe."}, status=status.HTTP_400_BAD_REQUEST)

        saved_code = cache.get(f"reset_code:{email}")
        if saved_code != code:
            return Response({"detail": "Code invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        user.password = make_password(new_password)
        user.save()

        cache.delete(f"reset_code:{email}")  # Supprimer le code du cache après utilisation

        return Response({"detail": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)


# 🔐 Utilisateur (si tu veux gérer les utilisateurs)
class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.AllowAny]  # Tu peux mettre IsAuthenticated pour les autres vues


# ✅ Groupes
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-created_at')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    def get_queryset(self):
        user=self.request.user
        return Group.objects.filter(createur=user)
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            # Affiche dans la console Django
            print("❌ Erreur lors de la création du groupe :", str(e))
            # Ou via logging
            # Et on relance pour que DRF affiche aussi l'erreur dans la réponse
            raise
        
class AllGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-created_at')
    serializer_class = GroupSerializer
    

    


# ✅ Feedback sur les groupes
class GroupFeedbackViewSet(viewsets.ModelViewSet):
    queryset = GroupFeedback.objects.all()
    serializer_class = GroupFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ✅ Scrolls (liaison automatique de user)
from rest_framework.exceptions import ValidationError

class GroupScrollViewSet(viewsets.ModelViewSet):
    queryset = GroupScroll.objects.all()
    serializer_class = GroupScrollSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        group = serializer.validated_data['group']
        user_id = serializer.validated_data['user_id']

        if GroupScroll.objects.filter(group=group, user_id=user_id).exists():
            raise ValidationError("Ce groupe a déjà été vu par cet utilisateur.")
        
        serializer.save()



class GroupClickCreateView(APIView):
    """
    Enregistrer un click unique par user_id (UUID côté Expo)
    Pas besoin d'être connecté
    """

    def post(self, request, group_id):
        user=self.request.user
        group = get_object_or_404(Group, id=group_id)
        user_id = request.data.get("user_id")
        if not user_id or not user.is_authenticated:
            return Response({"error": "user_id requis"}, status=status.HTTP_400_BAD_REQUEST)

        exists = GroupClick.objects.filter(group=group, user_id=user_id).exists() or GroupClick.objects.filter(group=group, cliquer=user).exists()
        
        if exists:
            return Response({"detail": "Déjà cliqué"}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_authenticated:
            click = GroupClick.objects.create(group=group, user_id=user_id,cliquer=user)
        else:
            click = GroupClick.objects.create(group=group, user_id=user_id)
        serializer = GroupClickSerializer(click)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyGroupsStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        groups = Group.objects.filter(createur=user).order_by('-created_at')
        data = GroupSerializer(groups, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    
    
from django.db.models import Count

class ProfileState(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = Group.objects.filter(createur=user)
        addesion=GroupClick.objects.filter(cliquer=user).count()
        feed=GroupFeedback.objects.filter(user=user).count()
        #clicks_count = groups.aggregate(total_clicks=Count('clicks'))['total_clicks'] or 0
        group_count = groups.count()

        return Response(
            {
                "group": group_count,
                "feedbacks": feed,
                "addesion": addesion
            },
            status=status.HTTP_200_OK
        )


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retourne seulement les notifications de l'utilisateur connecté, triées par date décroissante
        return Notification.objects.filter(destinataire=self.request.user).order_by('-created_at')

    def partial_update(self, request, *args, **kwargs):
        """
        Permet de marquer une notification comme lue via PATCH.
        Exemple payload : {"lue": true}
        """
        return super().partial_update(request, *args, **kwargs)
    
class Logout(APIView):
    def post(self,request):
        token=request.data.get('token',None)
        user=self.request.user
        if not (token and user):
            return Response({"message":"requete mal envoyer"},status=status.HTTP_400_BAD_REQUEST)
        device=Device.objects.filter(user=user,token=token,is_active=True).first()
        if device:
            device.is_active=False
            device.save()
            
        return Response({"message":"vous etes déconnecter"})