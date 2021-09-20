from django.db import models


class Countable(models.Model):
    count = models.IntegerField(default=0)

    def reset_count(self):
        prev_count = self.count
        self.count = 0
        self.save()
        return prev_count

    def add_to_count(self, to_add_value):
        prev_count = self.count
        new_count = prev_count + to_add_value
        self.count = new_count
        self.save()
        return prev_count, new_count

    def subtract_to_count(self, to_subtract_value):
        prev_count = self.count
        new_count = prev_count - to_subtract_value
        self.count = new_count
        self.save()
        return prev_count, new_count

    class Meta:
        abstract = True
