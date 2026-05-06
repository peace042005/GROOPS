from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Group, Categorie, Pays, Platform, Utilisateur

User = get_user_model()

class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'link', 'pays', 'categorie', 'platform']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pays'].queryset = Pays.objects.all()
        self.fields['categorie'].queryset = Categorie.objects.all()

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    list_display = ['name', 'pays', 'categorie', 'platform', 'created_at']
    list_filter = ['pays', 'categorie', 'platform']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    # Modification
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)

    # Suppression
    actions = ['supprimer_groupes']

    def supprimer_groupes(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} groupe(s) supprimé(s) avec succès.")
    supprimer_groupes.short_description = "Supprimer les groupes sélectionnés"

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']
    search_fields = ['nom']

@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']
    search_fields = ['nom']

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']
    search_fields = ['nom']

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'telephone']