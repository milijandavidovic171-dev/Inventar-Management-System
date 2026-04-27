from django.shortcuts import render
from inventar_app.models import Profile, Artikel
from django.db.models import Sum

def portfolio_view(request):
    """
    Standard-View für dein Portfolio.
    """
    profile = Profile.objects.first()
    stats = {
        'arten': Artikel.objects.count(),
        'gesamt': Artikel.objects.aggregate(Sum('menge'))['menge__sum'] or 0
    }
    
    return render(request, 'portfolio.html', {'profile': profile, 'stats': stats})

def ims_view(request):
    """
    Die neue View für dein Inventar-Management-System (IMS).
    Greift auf die gleichen Daten zu wie das Portfolio.
    """
    profile = Profile.objects.first()
    stats = {
        'arten': Artikel.objects.count(),
        'gesamt': Artikel.objects.aggregate(Sum('menge'))['menge__sum'] or 0
    }
    
    return render(request, 'ims.html', {'profile': profile, 'stats': stats})