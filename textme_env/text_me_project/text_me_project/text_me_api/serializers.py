from django.contrib.auth.models import User, Group
from rest_framework import serializers

from models import Kart,KartUser, Booking


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """ 
    This is the serializer for the User class, 
    id and url are read-only to the users but they can choose email and password
    """
    id=serializers.ReadOnlyField(read_only=True)
    url=serializers.ReadOnlyField(read_only=True)
    class Meta:
        model = User
        fields = ('url', 'email','password','id')
    def create(self, validated_data):
            password = validated_data.pop('password', None)
            email=validated_data.pop('email')
            user=User.objects.create_user(username=email,email=email,password=password)
            return user

    
class BookingSerializer(serializers.HyperlinkedModelSerializer):
    """This is the Booking serializer, 
    the only options which can be edited by the owner are begin_date and end_date
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    karts=serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    price_paid=serializers.ReadOnlyField(read_only=True)
    id=serializers.ReadOnlyField(read_only=True)
    class Meta:
        model=Booking
        fields=('id','begin_date','end_date','karts','owner', 'price_paid')

class KartUserSerializer(serializers.HyperlinkedModelSerializer):
    """KartUser class serializer, for practical reasons here, 
    users may update their balance but not their bookings or name
    """
    bookings=BookingSerializer(many=True, read_only=True)
    name=serializers.ReadOnlyField(read_only=True)
    class Meta:
        model=KartUser
        fields=('name','balance','bookings')

class KartSerializer(serializers.HyperlinkedModelSerializer):
    """
    Kart serializer, no one can access this data directly except for admins.
    Latitude and longitude are possibly modified by an API call
    """
    bookings=BookingSerializer(many=True, read_only=True)
    id=serializers.ReadOnlyField(read_only=True)
    class Meta:
        model= Kart
        fields=('id','type_of_kart','bookings', 'hourly_price','latitude','longitude')




