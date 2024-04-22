from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewDelivery, ProductStorage

@receiver(post_save, sender=NewDelivery)
def update_storage_quantity(sender, instance, **kwargs):
    if kwargs['created']:
        option = instance.option 

        product_storages = ProductStorage.objects.filter(product__name=instance.product, option=option)

        for product_storage in product_storages:
            product_storage.storage += instance.quantity
            product_storage.save()

