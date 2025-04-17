from django.db import models

# Create your models here.


class HealthCheckCardUsage(models.Model):
    cardName = models.CharField(max_length=100)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.cardName} - {self.value}"


class DepartmentPerformance(models.Model):
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # e.g., Mission, Fun, etc.
    score = models.FloatField()
    contribution = models.FloatField()  # for pie chart (optional)

    def __str__(self):
        return f"{self.department} - {self.category}"