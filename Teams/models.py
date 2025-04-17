from django.db import models

# Create your models here.


class HealthCheckCardUsage(models.Model):
    cardName = models.CharField(max_length=100)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.cardName} - {self.value}"