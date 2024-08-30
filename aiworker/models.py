from django.db import models

class BasketAnalysis(models.Model):
  basket_data = models.TextField()