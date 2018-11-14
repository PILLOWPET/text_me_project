from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from text_me_project.text_me_api.serializers import UserSerializer,  KartUserSerializer, BookingSerializer, KartSerializer
from models import KartUser, Booking, Kart
from rest_framework.decorators import action
from rest_framework import permissions
from permissions import IsOwner
from rest_framework.response import Response
import datetime
from django.http import HttpResponse, JsonResponse
from math import ceil
from django.db.models import F


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Override default permissions with ours,
        anyone can create a User, but only Admins can list them all.
        Users authenticated may also access their personal data
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsOwner or permissions.IsAdminUser]
        return [permission() for permission in permission_classes]





class KartUsersViewSet(viewsets.ModelViewSet):
    queryset = KartUser.objects.all()
    serializer_class = KartUserSerializer

    def get_permissions(self):
        """
        Override default permissions with ours,
        Admins are the only ones able to list, delete or create profiles.
        We restrict the creation to avoir the situation where KartUser instances would have no User instance linked
        Users may access their personal data again and update it including their balance
        """
        if self.action == 'create' or self.action == 'list' or self.action == "delete":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def get_permissions(self):
        """
        Override default permissions with ours,
        users are not allow to list bookings or delete a booking,
        because the company has no refund policy.
        They may access their bookings and update them but through an action which is different from the update action,
        same goes for the create action
        """
        if (self.action=='delete' or self.action=='list' or self.action=="update" or self.action==create):
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes= [permissions.IsOwner]
        return [permission() for permission in permission_classes]


    @action(detail=False,methods=['POST'])
    def add_booking(self, request):
        """
        This action allows users to create bookings with multiple karts in them.
        The request contains, the list of karts, the begin date and the end date of the booking
        It returns string1 if it succeeds and string2 if not.
        """
        begin_date=datetime.datetime.strptime(request.data.get('begin_date'),'%Y-%m-%dT%H:%MZ')
        end_date=datetime.datetime.strptime(request.data.get('end_date'),'%Y-%m-%dT%H:%MZ')
        duration_days=(end_date-begin_date).days
        duration=(end_date-begin_date).seconds
        pks=request.data.get('karts_id')
        kartuser=KartUser.objects.get(pk=request.user)
        karts=[]
        price=0
        areAllAvailable=True
        for pk in pks:
            kart=Kart.objects.get(pk=pk)
            karts.append(kart)
            price+=(kart.hourly_price)*ceil(duration/3600.0)
            areAllAvailable=areAllAvailable and kart.bookings.filter(begin_date__lt=end_date,end_date__gt=begin_date).count()==0
            #we check for all karts that there are no bookings overlaping the period of time requested by the user
        if (areAllAvailable and kartuser.balance>=price and duration>=0 and duration_days>=0):
            #if all the karts are available for this period, the duration is consistent and the user's balance is enough for the price to pay
            new_booking=Booking(begin_date=begin_date, end_date=end_date,owner=request.user.kart_user, price_paid=price)
            new_booking.save()
            kartuser.balance=kartuser.balance-price
            kartuser.save()
            for kart in karts:
                kart.bookings.add(new_booking)
            return(Response('passed'))
        else:
            return(Response('failed'))
    
    @action(detail=True,methods=['POST'])
    def update_booking(self,request, pk):
        """
        This allows the user to update his bookings,
        the new version of the booking must not overlap with another booking and the price must be greater than
        the previous price ot pay (no refund policy).
        The input is the new begin_date and the new end_date of the booking
        We return string1 in case of success and string2 in case of failure
        """
        booking=Booking.objects.get(pk=pk)
        begin_date=datetime.datetime.strptime(request.data.get('begin_date'),'%Y-%m-%dT%H:%MZ')
        end_date=datetime.datetime.strptime(request.data.get('end_date'),'%Y-%m-%dT%H:%MZ')
        duration=(end_date-begin_date).seconds
        duration_days=(end_date-begin_date).days
        old_duration=(booking.end_date-booking.begin_date).seconds
        old_price=booking.price_paid
        kartuser=KartUser.objects.get(pk=request.user)
        areAllAvailable=True
        price=0
        for kart in booking.karts.all():
            areAllAvailable= areAllAvailable and kart.bookings.filter(begin_date__lt=end_date,end_date__gt=begin_date).distinct().count()==0
            price+=(kart.hourly_price)*ceil(duration/3600.0)
        if (duration>=old_duration and duration_days>=0 and kartuser.balance-(price-old_price)>=0 and areAllAvailable):
            #Again if the dates are consistent, and the balance covers the cost and the karts are all available we proceed
            booking.begin_date=begin_date
            booking.end_date=end_date
            booking.price_paid=price
            kartuser.balance=kartuser.balance-(price-old_price)
            kartuser.save()
            booking.save()
            return(Response('passed'))
        else:
            return(Response('failed'))
    


class KartViewSet(viewsets.ModelViewSet):
    queryset=Kart.objects.all()
    serializer_class=KartSerializer
    def get_permissions(self):
        """
        Override default permissions with ours,
        users are not allowed to change anything in karts.
        However they make check the karts availabilities through our custom action 
        (to avoid them checking the bookings of other users)
        """
        if (self.action=='availablekarts'):
            permissions_classes=[permissions.IsAuthenticated]
        else:
            permissions_classes=[permissions.IsAdminUser]
        return([permission() for permission in permissions_classes])

    @action(detail=False,methods=['GET'])
    def availablekarts(self,request):
        """This function shows the karts available in the selected period of time.
        It returns a JSON with the list of karts available sorted by ascending distance to the user
        """
        begin_date=datetime.datetime.strptime(self.request.GET['begin_date'],'%Y-%m-%dT%H:%MZ')
        end_date=datetime.datetime.strptime(self.request.GET['end_date'],'%Y-%m-%dT%H:%MZ')
        longitude=self.request.GET['latitude']
        latitude=self.request.GET['longitude']
        qs=Kart.objects.exclude(bookings__begin_date__lt=end_date,bookings__end_date__gt=begin_date).annotate(distance=(F('longitude')-longitude)**2+(F('latitude')-latitude)**2).order_by('distance')
        #We remove the karts which have at least 1 booking overlaping with our period of time, and compute the distance
        #of the selected karts to the user
        qs=qs.values('id','type_of_kart','hourly_price','distance')
        return(JsonResponse({'listofkarts': list(qs)}))

        
