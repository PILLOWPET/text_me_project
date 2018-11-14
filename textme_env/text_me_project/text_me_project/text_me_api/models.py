from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class KartUser(models.Model):
    """This class represents the KartUser model which extends the Django User model with the OneToOneField,
    it also contains the list of bookings the user created"""
    user=models.OneToOneField(User, on_delete=models.CASCADE,default="123",related_name="kart_user", primary_key=True,unique=True)
    name=models.CharField(max_length=255, blank=False)
    balance=models.IntegerField(default=5)
    #owner=models.ForeignKey(User, related_name='kart_owner', on_delete=models.CASCADE)
    class Meta:
        ordering=('user',)
    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    "This is used to create a KartUser associated to the User whenever a User is created"
    if created:
        KartUser.objects.create(user=instance,name=instance.email,bookings=[])
        

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    "This is used to update KartUser whenever ths User associated to it is updated"
    instance.kart_user.save()

class Kart(models.Model):
    """This class represents the Kart model which has a ManyToMany relation with Booking"""
    id = models.AutoField(unique=True,primary_key=True)
    type_of_kart= models.CharField(max_length=255,blank=False)
    hourly_price=models.FloatField()
    longitude=models.FloatField(default=0)#We'll represent latitude and longitude with floats
    latitude=models.FloatField(default=0)
    class Meta:
        ordering=('id',)


class Booking(models.Model):
    """This class represents the Booking model, 
    it has a ManyToMany relationship with Kart and a ForeignKey relation with KartUser.
    """
    id=models.AutoField(unique=True,primary_key=True)
    karts=models.ManyToManyField('Kart', related_name='bookings')
    begin_date=models.DateTimeField()
    end_date=models.DateTimeField()
    owner=models.ForeignKey('KartUser', related_name='bookings', on_delete=models.CASCADE)
    price_paid=models.FloatField(default=0)
    class Meta:
        ordering=('id',)