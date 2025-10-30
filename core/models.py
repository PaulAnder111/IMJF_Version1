from django.db import models

class BaseModel(models.Model):
    """
    🏗️ Modèl baz pou tout lòt modèl nan sistèm lan.
    Li bay chan komen tankou:
      - email (inik atravè tout sistèm lan)
      - telephone (inik atravè tout sistèm lan)
      - date_created
      - date_updated
    """

    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Pa kreye tab pou BaseModel, li sèlman bay chan pou lòt modèl

    def __str__(self):
        # Yon string reprezantasyon jeneral pou tout modèl ki herite
        # Si modèl lan gen 'nom' oswa 'username', li pral itilize li
        if hasattr(self, 'username'):
            return self.username
        elif hasattr(self, 'nom'):
            return self.nom
        return f"{self.__class__.__name__} ({self.id})"
