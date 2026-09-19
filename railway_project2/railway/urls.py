from django.urls import path
from . import views
from .views import *

urlpatterns = [
    # auth
    path("verify-otp",verify_otp,name="verify_otp"),    
    path('register',register, name='register'),
    path("logout", logout, name="logout"),
    path('login',login, name='login'),
    path('home',home, name='home'),

    # admin
    path('admindash',admindash, name='admindash'),
    path('admintrains',admintrains, name='admintrains'),
    path('adminstation',adminstation, name='adminstation'),
    path('adminbooking',adminbooking, name='adminbooking'),
    path('adminuser',adminuser, name='adminuser'),
    path('adminprofile',adminprofile, name='adminprofile'),
    path('adminbookingdetails',adminbookingdetails,name='adminbookingdetails'),
    path("admintrainroute/<int:train_id>/",admintrainroute,name="admintrainroute"),
    path("admincoach/<int:train_id>/",admincoach,name="admincoach"),
    path("admintrainclass/<int:train_id>/",admintrainclass,name="admintrainclass"),
    path("deletebooking/<int:booking_id>/", views.deletebooking, name="deletebooking"),
    path('admincancellations', admincancellations, name='admincancellations'),

    

    # user
    path('helps',helps, name='helps'),
    path('helpans',helpans, name='helpans'),
    path('trains',trains, name='trains'),
    path('pnr',pnr, name='pnr'),
    path('reserv',reserv, name='reserv'),
    path('plan',plan, name='plan'),
    path('tips',tips, name='tips'),
    path('bag',bag, name='bag'),
    path('kerala',kerala, name='kerala'),
    path('rajasthan',rajasthan, name='rajasthan'),
    path('goa',goa, name='goa'),
    path('kashmir',kashmir, name='kashmir'),
    path('classser',classser, name='classser'),
    path('onboard',onboard, name='onboard'),
    # path('searchstation',searchstation, name='searchstation'),
    path("booking/",booking, name="booking"),
    path("mybookings", mybookings, name="mybookings"),
    path("proceed/<int:train_id>/",proceed, name="proceed"),
    path("confirm-booking/",confirm_booking,name="confirm_booking"),
    path("payment/<int:booking_id>/",payment,name="payment"),
    path("payment-handler/", paymenthandler, name="paymenthandler"),
    path("cancelbooking/<int:booking_id>/", cancelbooking, name="cancelbooking"),
    # path("save-booking/<int:booking_id>/", save_booking, name="save_booking"),




    # staff
    path('staffdash',staffdash, name='staffdash'),
    path('chatstaff/', chatstaff, name='chatstaff'),
    path('reply-staff-message/<int:message_id>/',reply_staff_message,name='reply_staff_message'),
    path('delete-staff-message/<int:message_id>/',delete_staff_message,name='delete_staff_message'),
    path('chatai/', chatai, name='chatai'),
    path('chatstaff/', chatstaff, name='chatstaff'),
    ]