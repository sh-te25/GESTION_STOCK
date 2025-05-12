from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Categorie,
    Fournisseur,
    Produit,
    MouvementStock,
    Alerte,
    ProfilUtilisateur
)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact')
    search_fields = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_reference', 'quantite_stock', 'prix_unitaire', 'categorie', 'fournisseur')
    list_filter = ('categorie', 'fournisseur')
    search_fields = ('nom', 'code_reference')


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type_mouvement', 'quantite', 'date', 'utilisateur')
    list_filter = ('type_mouvement', 'date')
    search_fields = ('produit__nom', 'utilisateur__username')


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type_alerte', 'date_creation', 'est_resolue')
    list_filter = ('type_alerte', 'est_resolue')
    search_fields = ('produit__nom', 'message')


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'date_inscription')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
