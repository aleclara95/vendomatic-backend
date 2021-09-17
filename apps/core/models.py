from django.db import models

# Create your models here.


class CoinsAmount(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    value = models.DecimalField(max_digits=6, decimal_places=3)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.value} - {self.count}"


class Item(models.Model):
    name = models.CharField(max_length=64)
    verbose_name = models.CharField(max_length=64)
    volume = models.DecimalField(max_digits=3, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f"{self.verbose_name} - {self.volume}L"


class MachineItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.item} - {self.count}"
