from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    desc = models.TextField()
    img = models.ImageField(upload_to='static/images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name
    