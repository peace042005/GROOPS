from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Modèle utilisateur personnalisé
class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    telephone = models.CharField(max_length=16, blank=True, null=True)
    profile = models.ImageField(upload_to='profile/', blank=True, null=True)
    pays = models.CharField(max_length=30, blank=True, null=True)

    username = models.CharField(max_length=30, unique=False, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# --- Autres modèles ---
from django.contrib.auth import get_user_model

User = get_user_model()


class Categorie(models.Model):
    nom = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class Pays(models.Model):
    nom = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class Group(models.Model):
    PLATFORMS = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('facebook', 'Facebook'),
    ]

    createur = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(unique=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    pays = models.ForeignKey(Pays, on_delete=models.SET_NULL, null=True)
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupClick(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='clicks')
    user_id = models.CharField(max_length=100)  # UUID envoyé depuis le client (non relié à User)
    cliquer = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user_id')  # évite les doublons


class GroupScroll(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='scrolls')
    user_id = models.CharField(max_length=100)  # UUID string venant du client
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.group.name} - {self.user_id}"



class GroupFeedback(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='feedbacks')
    type=models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True,null=True)
    note = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])  # 1 à 5
    created_at = models.DateTimeField(auto_now_add=True)


