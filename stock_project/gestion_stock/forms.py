from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Produit,
    Categorie,
    Fournisseur,
    MouvementStock,
    ProfilUtilisateur,
)


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'nom', 'code_reference', 'description', 'quantite_stock',
            'prix_unitaire', 'categorie', 'fournisseur',
            'seuil_alerte', 'date_peremption'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_peremption': forms.DateInput(attrs={'type': 'date'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact']


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        exclude = ['utilisateur', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'lieu_source': forms.TextInput(attrs={'placeholder': 'Entrepôt A'}),
            'lieu_destination': forms.TextInput(attrs={'placeholder': 'Entrepôt B'}),
        }


class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('employe', 'Employé'),
        ('gestionnaire', 'Gestionnaire'),
        ('admin', 'Administrateur'),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
