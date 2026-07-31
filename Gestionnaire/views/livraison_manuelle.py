from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from Client.decorators import role_required
from Gestionnaire.models import LivraisonManuelle


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required("gestionnaire"), name='dispatch')
class LivraisonManuelleListView(ListView):
    model = LivraisonManuelle
    template_name = 'Gestionnaire/pages/livraisons_manuelles.html'
    context_object_name = 'livraisons'
    paginate_by = 15

    def get_queryset(self):
        queryset = LivraisonManuelle.objects.all()

        facture = self.request.GET.get('facture')
        if facture == 'oui':
            queryset = queryset.filter(numero_facture__isnull=False)
        elif facture == 'non':
            queryset = queryset.filter(numero_facture__isnull=True)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(client_nom__icontains=search_query) |
                Q(client_telephone__icontains=search_query) |
                Q(nature_colis__icontains=search_query) |
                Q(lieu_depart__icontains=search_query) |
                Q(lieu_arrivee__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_facture'] = self.request.GET.get('facture', '')

        kpi = LivraisonManuelle.objects.aggregate(
            total=Count('id'),
            facturees=Count('id', filter=Q(numero_facture__isnull=False)),
            non_facturees=Count('id', filter=Q(numero_facture__isnull=True)),
        )
        context.update(kpi)
        return context


@login_required
@role_required("gestionnaire")
@require_POST
def creer_livraison_manuelle(request):
    """Ajoute une nouvelle ligne au registre des livraisons manuelles."""
    champs_requis = ['date_livraison', 'client_nom', 'nature_colis', 'lieu_depart', 'lieu_arrivee', 'montant']
    if not all(request.POST.get(champ) for champ in champs_requis):
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    try:
        montant = float(request.POST.get('montant'))
    except (TypeError, ValueError):
        messages.error(request, "Le montant saisi n'est pas valide.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    LivraisonManuelle.objects.create(
        date_livraison=request.POST.get('date_livraison'),
        client_nom=request.POST.get('client_nom').strip(),
        client_telephone=request.POST.get('client_telephone', '').strip() or None,
        nature_colis=request.POST.get('nature_colis').strip(),
        lieu_depart=request.POST.get('lieu_depart').strip(),
        lieu_arrivee=request.POST.get('lieu_arrivee').strip(),
        observations=request.POST.get('observations', '').strip() or None,
        montant=montant,
        cree_par=request.user,
    )
    messages.success(request, "La livraison a été ajoutée au registre.")
    return redirect('Gestionnaire:livraisons_manuelles_liste')


@login_required
@role_required("gestionnaire")
@require_POST
def modifier_livraison_manuelle(request, pk):
    """Modifie une ligne du registre — verrouillée dès qu'une facture a été générée."""
    livraison = get_object_or_404(LivraisonManuelle, pk=pk)

    if livraison.numero_facture:
        messages.error(request, "Cette livraison a déjà été facturée et ne peut plus être modifiée.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    champs_requis = ['date_livraison', 'client_nom', 'nature_colis', 'lieu_depart', 'lieu_arrivee', 'montant']
    if not all(request.POST.get(champ) for champ in champs_requis):
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    try:
        montant = float(request.POST.get('montant'))
    except (TypeError, ValueError):
        messages.error(request, "Le montant saisi n'est pas valide.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    livraison.date_livraison = request.POST.get('date_livraison')
    livraison.client_nom = request.POST.get('client_nom').strip()
    livraison.client_telephone = request.POST.get('client_telephone', '').strip() or None
    livraison.nature_colis = request.POST.get('nature_colis').strip()
    livraison.lieu_depart = request.POST.get('lieu_depart').strip()
    livraison.lieu_arrivee = request.POST.get('lieu_arrivee').strip()
    livraison.observations = request.POST.get('observations', '').strip() or None
    livraison.montant = montant
    livraison.save()

    messages.success(request, "La livraison a été mise à jour.")
    return redirect('Gestionnaire:livraisons_manuelles_liste')


@login_required
@role_required("gestionnaire")
@require_POST
def supprimer_livraison_manuelle(request, pk):
    """Supprime une ligne du registre — verrouillée dès qu'une facture a été générée."""
    livraison = get_object_or_404(LivraisonManuelle, pk=pk)

    if livraison.numero_facture:
        messages.error(request, "Cette livraison a déjà été facturée et ne peut plus être supprimée.")
        return redirect('Gestionnaire:livraisons_manuelles_liste')

    livraison.delete()
    messages.success(request, "La livraison a été supprimée du registre.")
    return redirect('Gestionnaire:livraisons_manuelles_liste')
