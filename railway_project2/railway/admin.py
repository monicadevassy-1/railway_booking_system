from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(RailwayUser)
admin.site.register(Station)
admin.site.register(Train)
admin.site.register(TrainClass)
admin.site.register(EmailOTP)
admin.site.register(TrainRoute)
admin.site.register(Coach)
admin.site.register(TrainSchedule)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(BookingPassenger)
admin.site.register(Payment)
admin.site.register(Cancellation)
admin.site.register(ClassType)