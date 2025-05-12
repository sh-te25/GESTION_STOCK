from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    RegisterView,
    ProduitListView, ProduitCreateView, ProduitUpdateView, ProduitDeleteView,
    CategorieListView, CategorieCreateView,
    FournisseurListView, FournisseurCreateView,
    MouvementStockListView, MouvementStockCreateView,
    AlerteListView, resolve_alerte,
    DashboardView,
    export_pdf_inventaire, export_pdf_mouvements,
)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='gestion_stock/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('produits/', ProduitListView.as_view(), name='produit_list'),
    path('produits/ajouter/', ProduitCreateView.as_view(), name='produit_create'),
    path('produits/<int:pk>/modifier/', ProduitUpdateView.as_view(), name='produit_update'),
    path('produits/<int:pk>/supprimer/', ProduitDeleteView.as_view(), name='produit_delete'),

    path('categories/', CategorieListView.as_view(), name='categorie_list'),
    path('categories/ajouter/', CategorieCreateView.as_view(), name='categorie_create'),

    path('fournisseurs/', FournisseurListView.as_view(), name='fournisseur_list'),
    path('fournisseurs/ajouter/', FournisseurCreateView.as_view(), name='fournisseur_create'),


    path('mouvements/', MouvementStockListView.as_view(), name='mouvement_list'),
    path('mouvements/ajouter/', MouvementStockCreateView.as_view(), name='mouvement_create'),

    path('alertes/', AlerteListView.as_view(), name='alerte_list'),
    path('alertes/<int:pk>/resoudre/', resolve_alerte, name='alerte_resoudre'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('export/inventaire/', export_pdf_inventaire, name='export_pdf_inventaire'),
    path('export/mouvements/', export_pdf_mouvements, name='export_pdf_mouvements'),
]
