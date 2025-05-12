from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    contact = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class ProfilUtilisateur(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('gestionnaire', 'Gestionnaire'),
        ('employe', 'Employé'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Produit(models.Model):
    nom = models.CharField(max_length=100)
    code_reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    quantite_stock = models.IntegerField(default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True)

    seuil_alerte = models.PositiveIntegerField(default=5)
    date_peremption = models.DateField(null=True, blank=True)

    def get_valeur_stock(self):
        return self.quantite_stock * self.prix_unitaire

    def __str__(self):
        return f"{self.nom} ({self.code_reference})"


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('perte', 'Perte'),
        ('transfert', 'Transfert'),
        ('retour', 'Retour'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    lieu_source = models.CharField(max_length=100, blank=True)
    lieu_destination = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"


class Alerte(models.Model):
    TYPE_CHOICES = [
        ('seuil', 'Seuil critique'),
        ('expiration', 'Date de péremption'),
        ('autre', 'Autre'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type_alerte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    est_resolue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_type_alerte_display()} - {self.produit.nom}"
