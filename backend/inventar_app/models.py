from django.db import models


class Artikel(models.Model):
    """
    Modell für dein Inventar-System.
    Wichtig für die Bestandsverwaltung in der Desktop- und Web-App.
    """
    name = models.CharField(max_length=200, verbose_name="Artikelname")
    menge = models.IntegerField(default=0, verbose_name="Bestand")
    standort = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lagerort")
    artikelnummer = models.CharField(max_length=50, unique=True, verbose_name="Artikel-Nr.")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.artikelnummer})"

    class Meta:
        db_table = 'artikel'
        verbose_name = "Artikel"
        verbose_name_plural = "Artikelbestand"
        ordering = ['-id']


# WICHTIG: Diese Klasse MUSS ganz links am Rand starten (keine Einrückung!)
class Profile(models.Model):
    """
    Modell für deine persönlichen Daten auf der Portfolio-Webseite.
    """
    name = models.CharField(max_length=100, default="Milijan Davidovic")
    titel = models.CharField(max_length=100, default="Junior Python Developer")
    bio = models.TextField(verbose_name="Über mich")
    email = models.EmailField()
    github_url = models.URLField(blank=True, verbose_name="GitHub Link")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn Link")
    standort = models.CharField(max_length=100, default="Kempten / Gera")

    skills = models.TextField(
        help_text="Gib deine Skills mit Komma getrennt ein, z.B. Python, Django, FastAPI",
        verbose_name="Tech Stack"
    )

    def __str__(self):
        return f"Profil von {self.name}"

    class Meta:
        verbose_name = "Mein Profil"
        verbose_name_plural = "Mein Profil"