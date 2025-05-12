from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.utils.timezone import localtime, now
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .models import (
    Produit, Categorie, Fournisseur,
    MouvementStock, Alerte, ProfilUtilisateur
)
from .forms import (
    ProduitForm, CategorieForm,
    FournisseurForm, MouvementStockForm,
    UserRegisterForm
)
from .utils import role_required


class RegisterView(FormView):
    template_name = 'gestion_stock/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('produit_list')

    def form_valid(self, form):
        user = form.save()
        profil = user.profilutilisateur
        profil.role = form.cleaned_data['role']
        profil.save()
        login(self.request, user)
        return super().form_valid(form)


class ProduitListView(ListView):
    model = Produit
    template_name = 'gestion_stock/produit_list.html'
    context_object_name = 'produits'

    def get_queryset(self):
        qs = Produit.objects.all()
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(nom__icontains=query) | Q(code_reference__icontains=query))
        if cat := self.request.GET.get('categorie'):
            if cat.isdigit():
                qs = qs.filter(categorie__id=cat)
        if four := self.request.GET.get('fournisseur'):
            if four.isdigit():
                qs = qs.filter(fournisseur__id=four)
        if qmin := self.request.GET.get('qmin'):
            if qmin.isdigit():
                qs = qs.filter(quantite_stock__gte=int(qmin))
        if tri := self.request.GET.get('sort'):
            if tri in ['nom', 'quantite_stock', 'prix_unitaire', '-nom', '-quantite_stock', '-prix_unitaire']:
                qs = qs.order_by(tri)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        context['fournisseurs'] = Fournisseur.objects.all()
        return context


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class ProduitCreateView(CreateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'gestion_stock/produit_form.html'
    success_url = reverse_lazy('produit_list')


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class ProduitUpdateView(UpdateView):
    model = Produit
    form_class = ProduitForm
    template_name = 'gestion_stock/produit_form.html'
    success_url = reverse_lazy('produit_list')


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class ProduitDeleteView(DeleteView):
    model = Produit
    template_name = 'gestion_stock/produit_confirm_delete.html'
    success_url = reverse_lazy('produit_list')


class CategorieListView(ListView):
    model = Categorie
    template_name = 'gestion_stock/categorie_list.html'
    context_object_name = 'categories'


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class CategorieCreateView(CreateView):
    model = Categorie
    form_class = CategorieForm
    template_name = 'gestion_stock/categorie_form.html'
    success_url = reverse_lazy('categorie_list')


class FournisseurListView(ListView):
    model = Fournisseur
    template_name = 'gestion_stock/fournisseur_list.html'
    context_object_name = 'fournisseurs'


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class FournisseurCreateView(CreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'gestion_stock/fournisseur_form.html'
    success_url = reverse_lazy('fournisseur_list')


class MouvementStockListView(ListView):
    model = MouvementStock
    template_name = 'gestion_stock/mouvement_list.html'
    context_object_name = 'mouvements'
    ordering = ['-date']


@method_decorator(role_required(['admin', 'gestionnaire']), name='dispatch')
class MouvementStockCreateView(CreateView):
    model = MouvementStock
    form_class = MouvementStockForm
    template_name = 'gestion_stock/mouvement_form.html'
    success_url = reverse_lazy('mouvement_list')

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        produit = form.instance.produit
        quantite = form.instance.quantite
        type_mvt = form.instance.type_mouvement

        if type_mvt in ['entree', 'retour', 'ajustement']:
            produit.quantite_stock += quantite
        elif type_mvt in ['sortie', 'perte', 'transfert']:
            produit.quantite_stock -= quantite
        produit.save()

        if produit.quantite_stock < produit.seuil_alerte:
            if not Alerte.objects.filter(produit=produit, type_alerte='seuil', est_resolue=False).exists():
                Alerte.objects.create(
                    produit=produit,
                    type_alerte='seuil',
                    message=f"Le stock de {produit.nom} est critique ({produit.quantite_stock} unités)."
                )

        if produit.date_peremption and produit.date_peremption < now().date():
            if not Alerte.objects.filter(produit=produit, type_alerte='expiration', est_resolue=False).exists():
                Alerte.objects.create(
                    produit=produit,
                    type_alerte='expiration',
                    message=f"Le produit {produit.nom} est périmé depuis le {produit.date_peremption.strftime('%d/%m/%Y')}."
                )

        return super().form_valid(form)


class AlerteListView(ListView):
    model = Alerte
    template_name = 'gestion_stock/alerte_list.html'
    context_object_name = 'alertes'
    ordering = ['-date_creation']

@role_required(['admin', 'gestionnaire'])
def resolve_alerte(request, pk):
    alerte = get_object_or_404(Alerte, pk=pk)
    alerte.est_resolue = True
    alerte.save()
    return redirect('alerte_list')


class DashboardView(TemplateView):
    template_name = 'gestion_stock/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = Produit.objects.count()
        critiques = Produit.objects.filter(quantite_stock__lt=F('seuil_alerte')).count()
        normaux = total - critiques

        context['stock_data'] = {
            'labels': ['Stock Critique', 'Stock Normal'],
            'values': [critiques, normaux],
        }

        top = Produit.objects.order_by('-quantite_stock')[:5]
        context['bar_data'] = {
            'labels': [p.nom for p in top],
            'values': [p.quantite_stock for p in top],
        }
        return context


def export_pdf_inventaire(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventaire.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Rapport d'inventaire")
    y -= 40

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Nom")
    p.drawString(200, y, "Référence")
    p.drawString(320, y, "Quantité")
    p.drawString(400, y, "Prix")
    y -= 20

    p.setFont("Helvetica", 11)

    produits = Produit.objects.all()
    for produit in produits:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(50, y, produit.nom)
        p.drawString(200, y, produit.code_reference)
        p.drawString(320, y, str(produit.quantite_stock))
        p.drawString(400, y, f"{produit.prix_unitaire:.2f} MAD")
        y -= 18

    # Affichage de la valorisation totale du stock
    valeur_totale = sum(
        p.quantite_stock * p.prix_unitaire for p in produits
    )
    if y < 80:
        p.showPage()
        y = height - 50
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Valeur totale du stock :")
    p.setFont("Helvetica", 12)
    p.drawString(250, y, f"{valeur_totale:.2f} MAD")

    p.showPage()
    p.save()
    return response


def export_pdf_mouvements(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mouvements_stock.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Rapport des mouvements de stock")
    y -= 40
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Produit")
    p.drawString(200, y, "Type")
    p.drawString(280, y, "Quantité")
    p.drawString(350, y, "Date")
    p.drawString(470, y, "Utilisateur")
    y -= 20
    p.setFont("Helvetica", 10)

    mouvements = MouvementStock.objects.select_related('produit', 'utilisateur').order_by('-date')
    for m in mouvements:
        if y < 50:
            p.showPage()
            y = height - 50
        date_str = localtime(m.date).strftime('%d/%m/%Y %H:%M')
        utilisateur = m.utilisateur.username if m.utilisateur else '-'
        p.drawString(50, y, m.produit.nom[:25])
        p.drawString(200, y, m.get_type_mouvement_display())
        p.drawString(280, y, str(m.quantite))
        p.drawString(350, y, date_str)
        p.drawString(470, y, utilisateur)
        y -= 18

    p.showPage()
    p.save()
    return response
