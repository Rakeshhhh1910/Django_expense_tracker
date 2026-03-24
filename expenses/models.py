from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← NEW

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"

    class Meta:
        ordering = ['-date', '-created_at']  # ← NEW: default sort