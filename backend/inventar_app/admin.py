from django.contrib import admin
from .models import Artikel, Profile


# 1. Registrierung für die Bestandsverwaltung (Artikel)
@admin.register(Artikel)
class ArtikelAdmin(admin.ModelAdmin):
    # Diese Spalten werden in der Liste angezeigt
    list_display = ('id', 'name', 'artikelnummer', 'menge', 'standort', 'aktualisiert_am')
    # Diese Felder sind durchsuchbar
    search_fields = ('name', 'artikelnummer')
    # Filter-Optionen in der rechten Seitenleiste
    list_filter = ('standort',)


# 2. Registrierung für deine Portfolio-Daten (Profil)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Diese Klasse schaltet den Bereich 'Mein Profil' im Admin frei.
    """
    list_display = ('name', 'titel', 'standort', 'email')

    # Verhindert, dass man versehentlich mehrere Profile anlegt,
    # da du für die Webseite nur eines brauchst.
    def has_add_permission(self, request):
        if Profile.objects.exists():
            return False
        return True