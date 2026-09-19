from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
import random
import os
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
# from huggingface_hub import InferenceClient


# Create your views here.
#------------------------------REGISTRATION------------------------------------------
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            usr = form.save()
            otp = random.randint(100000, 999999)
            if request.GET.get("admin") == "1":
                usr.is_admin = True
                usr.save()
            elif request.GET.get("staff") == "1":
                usr.is_staff = True
                usr.is_admin = False
                usr.save()

            emailotp = EmailOTP()
            emailotp.user = usr
            emailotp.otp = otp
            emailotp.save()
            request.session["user_id"] = usr.id
                    # (session remembers user_id)
            send_mail("Railway Booking OTP",f"Your OTP is {otp}",settings.EMAIL_HOST_USER,[usr.email])            
            # messages.success(request,"user registered successfully!!!!!!!")
            return redirect(verify_otp)
    else:
        form = RegistrationForm()
    return render(request,"register.html",{"form": form})



def verify_otp(request):
    user_id = request.session["user_id"]
    user = RailwayUser.objects.get(id=user_id)
    if request.method == "POST":
        entered_otp = request.POST["otp"]
        otp = EmailOTP.objects.get(user=user)
        if entered_otp == otp.otp:
            user.is_verified = True
            user.save()
            messages.success(request, "User registered successfully!!!!!!!")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP, Please try Again")
    return render(request, "verify_otp.html", {"email": user.email})


#------------------------------LOGIN------------------------------------------


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST["username"]
        password = request.POST["password"]
        users = RailwayUser.objects.filter(username=username)
        if users.exists():
            user = users[0]
            if user.password == password:
                request.session["user_id"] = user.id
                if user.is_admin:
                    return redirect("admindash")
                elif user.is_staff:
                    return redirect("staffdash")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid password")
        else:
            messages.error(request, "User not found")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout(request):
    request.session.flush()
    return redirect(login)




#------------------------------USER -------------------------------------------
def home(request):
    if "user_id" in request.session:
        user_id = request.session["user_id"]
        users = RailwayUser.objects.filter(id=user_id)
        if users.exists():
            stations = Station.objects.filter(is_active=True)
            class_types = ClassType.objects.all()
            # Popular Routes
            mumbai = Station.objects.filter(station_code="CSMT").first()
            new_delhi = Station.objects.filter(station_code="NDLS").first()
            bengaluru = Station.objects.filter(station_code="SBC").first()
            chennai = Station.objects.filter(station_code="MAS").first()
            kolkata = Station.objects.filter(station_code="KOAA").first()
            varanasi = Station.objects.filter(station_code="BSP").first()
            hyderabad = Station.objects.filter(station_code="HYB").first()
            pune = Station.objects.filter(station_code="PUNE").first()
            return render(request, "home.html", {
                "stations": stations,
                "class_types": class_types,
                "mumbai": mumbai,
                "new_delhi": new_delhi,
                "bengaluru": bengaluru,
                "chennai": chennai,
                "kolkata": kolkata,
                "varanasi": varanasi,
                "hyderabad": hyderabad,
                "pune": pune,    })
    return redirect("login")

def helps(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    return render(request, "helps.html")

def tips(request):
    return render(request, 'tips.html')

def bag(request):
    return render(request, 'bag.html')

def kerala(request):
    return render(request, 'kerala.html')
def rajasthan(request):
    return render(request, 'rajasthan.html')
def goa(request):
    return render(request, 'goa.html')
def kashmir(request):
    return render(request, 'kashmir.html')

def helpans(request):
    question = request.GET.get("question")
    return render(request, "helpans.html", {"question": question})

def trains(request):
    stations = Station.objects.filter(is_active=True)
    class_types = ClassType.objects.all()
    return render(request,"trains.html",
        {"stations": stations,"class_types": class_types})

def plan(request):
    stations = Station.objects.all()
    class_types = ClassType.objects.all()
    return render(request, 'plan.html', {"stations": stations,"class_types": class_types })

def confirm_booking(request):
    if request.method == "POST":
        train_id = request.POST.get("train_id")
        starting_station = request.POST.get("starting_station")
        destination_station = request.POST.get("destination_station")
        journey_date = request.POST.get("journey_date")
        train_class = request.POST.get("train_class")
        passengers = request.POST.get("passengers")
        total_amount = request.POST.get("total_amount")

        user_id = request.session.get("user_id")
        user = RailwayUser.objects.get(id=user_id)

        train = Train.objects.get(id=train_id)
        selected_class = TrainClass.objects.get(train=train,class_type__class_name=train_class)
        start_station = Station.objects.get(id=starting_station)
        destination = Station.objects.get( id=destination_station)

        pnr = str(random.randint(1000000000, 9999999999))

        booking = Booking()
        booking.pnr = pnr
        booking.user = user
        booking.train = train
        booking.train_class = selected_class
        booking.starting_station = start_station
        booking.destination_station = destination
        booking.journey_date = journey_date
        booking.passengers = passengers
        booking.total_amount = total_amount
        booking.booking_status = "Pending"
        booking.save()

        return redirect( "payment",booking_id=booking.id)
    return redirect("home")


def reserv(request):
    return render(request, 'reserv.html')

def pnr(request):
    booking = None
    pnr_number = request.GET.get("pnr")
    if pnr_number:
        booking = Booking.objects.filter(pnr=pnr_number).first()
    return render(request, 'pnr.html', {"booking": booking,"pnr_number": pnr_number})

def classser(request):
    return render(request, 'classser.html')
def onboard(request):
    return render(request, 'onboard.html')






razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    amount = int(booking.total_amount * 100)
    currency = "INR"
    razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture="0"))
    razorpay_order_id = razorpay_order["id"]
    callback_url = request.build_absolute_uri(f"/railway/payment-handler/?booking_id={booking.id}")

    return render(request, "payment.html", {
        "booking": booking,"razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_key": settings.RAZOR_KEY_ID,"razorpay_amount": amount,
        "currency": currency,"callback_url": callback_url,})


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id", "")
        razorpay_order_id = request.POST.get("razorpay_order_id", "")
        signature = request.POST.get("razorpay_signature", "")
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature}
        try:
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print("PAYMENT ID:", payment_id)
            print("ORDER ID:", razorpay_order_id)
            print("SIGNATURE:", signature)
            print("VERIFY RESULT:", result)
            if result:
                booking_id = request.GET.get("booking_id")
                booking = Booking.objects.get(id=booking_id)
                amount = int(booking.total_amount * 100)

                razorpay_client.payment.capture(payment_id,amount)
                booking.booking_status = "Confirmed"
                booking.save()
                try:
                    send_mail("Railway Ticket Booking Confirmation",
                        f"""
            Dear {booking.user.first_name},

            Your railway ticket has been successfully booked.

            -------------------------------
                    TICKET DETAILS
            -------------------------------

            Train Number : {booking.train.train_number}
            Train Name   : {booking.train.train_name}

            From         : {booking.starting_station.station_name}
            To           : {booking.destination_station.station_name}

            Journey Date : {booking.journey_date}
            Class        : {booking.train_class.class_type.class_name}
            Passengers   : {booking.passengers}

            PNR Number   : {booking.pnr}
            Payment ID   : {payment_id}

            Total Amount : ₹{booking.total_amount}

            Booking Status : Confirmed

            -------------------------------

            Thank you for booking with Indian Railways.

            Have a safe journey!
            """,
                        settings.EMAIL_HOST_USER,
                        [booking.user.email],
                    )
                except Exception as e:
                    print("EMAIL ERROR:", e)

                return render(request, "paymentsuccess.html", {
                    "booking": booking,
                    "payment_id": payment_id,
                })

            else:

                return render(request, "paymentfail.html")

        except Exception as e:

            print("RAZORPAY ERROR:", e)

            return render(request, "paymentfail.html")

    return redirect("home")

def booking(request):

    stations = Station.objects.filter(is_active=True)

    starting_station = request.GET.get("starting_station")
    destination_station = request.GET.get("destination_station")
    journey_date = request.GET.get("journey_date")
    train_class = request.GET.get("train_class")
    passengers = request.GET.get("passengers")

    if starting_station:
        starting_station = int(starting_station)

    if destination_station:
        destination_station = int(destination_station)

    if passengers:
        request.session["passengers"] = passengers
    else:
        passengers = request.session.get("passengers", "1")

    selected_classes = request.GET.getlist("classes")
    selected_class_name = ""

    if selected_classes:
        selected_class_name = selected_classes[0]
        request.session["selected_classes"] = selected_classes
    else:
        saved_classes = request.session.get(
            "selected_classes",   [])
        if saved_classes:
            selected_classes = saved_classes
            selected_class_name = saved_classes[0]

    trains = Train.objects.all()

    if starting_station and destination_station:
        matching_trains = []
        for train in trains:
            route_stations = []
            if train.source:
                route_stations.append(train.source.id)
            routes = TrainRoute.objects.filter(train=train).order_by("stop_number")
            for route in routes:
                if route.station:
                    route_stations.append(route.station.id)
            if train.destination:
                route_stations.append(train.destination.id)
            if (starting_station in route_stations and destination_station in route_stations):
                start_position = route_stations.index(starting_station)
                destination_position = route_stations.index(destination_station)
                if start_position < destination_position:
                    matching_trains.append(train.id)

        trains = trains.filter(id__in=matching_trains)

    if selected_class_name:
        matching_trains = []
        for train in trains:
            class_exists = TrainClass.objects.filter(train=train,class_type__class_name=selected_class_name).exists()
            if class_exists:
                matching_trains.append(train.id)

        trains = trains.filter(id__in=matching_trains)

    selected_start_station = None
    selected_destination_station = None

    if starting_station:
        selected_start_station = Station.objects.get(id=starting_station )

    if destination_station:
        selected_destination_station = Station.objects.get(id=destination_station)

    if starting_station and destination_station:
        for train in trains:
            if (train.source and starting_station == train.source.id):
                train.selected_departure = train.departure
            else:
                start_route = TrainRoute.objects.filter(train=train,station_id=starting_station ).first()
                if start_route:
                    train.selected_departure = (start_route.departure_time)
                else:
                    train.selected_departure = None
            if (train.destination  and  destination_station == train.destination.id):
                train.selected_arrival = train.arrival
            else:
                destination_route = TrainRoute.objects.filter(train=train,station_id=destination_station ).first()
                if destination_route:
                    train.selected_arrival = (destination_route.arrival_time)
                else:
                    train.selected_arrival = None

    return render(request, "booking.html", {
        "stations": stations,
        "trains": trains,
        "selected_start": starting_station,
        "selected_destination": destination_station,
        "selected_start_station": selected_start_station,
        "selected_destination_station": selected_destination_station,
        "journey_date": journey_date,
        "train_class": train_class,
        "passengers": passengers,
        "selected_classes": selected_classes,
        "selected_class_name": selected_class_name,})

def proceed(request, train_id):
    train = Train.objects.get(id=train_id)
    starting_station = request.GET.get("starting_station")
    destination_station = request.GET.get("destination_station")
    journey_date = request.GET.get("journey_date")
    train_class = request.GET.get("train_class")
    passengers = request.GET.get("passengers", "1")

    selected_start_station = Station.objects.get(id=starting_station)
    selected_destination_station = Station.objects.get(id=destination_station)
    selected_class = TrainClass.objects.get(train=train,class_type__class_name=train_class)
    fare = selected_class.fare

    total_amount = fare * int(passengers)
    return render(request, "proceed.html", {
        "train": train,
        "selected_start_station": selected_start_station,
        "selected_destination_station": selected_destination_station,
         "journey_date": journey_date,
        "selected_class": selected_class,
        "passengers": passengers,
        "fare": fare,
        "total_amount": total_amount,})

def mybookings(request):
    user_id = request.session.get("user_id")
    bookings = Booking.objects.filter(user_id=user_id)
    return render(request, "mybookings.html", {
        "bookings": bookings})

def cancelbooking(request, booking_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        booking = Booking.objects.get(id=booking_id, user_id=user_id)
        if booking.booking_status == "Confirmed" or booking.booking_status == "Pending":
            cancellation = Cancellation()
            cancellation.booking = booking
            cancellation.reason = "Cancelled by user"
            cancellation.refund_amount = booking.total_amount
            cancellation.save()

            booking.booking_status = "Cancelled"
            booking.save()

            messages.success(request,"Your ticket has been cancelled successfully.")
    return redirect("mybookings")











#------------------------------ADMIN DASHBOARD------------------------------------------
def admindash(request):
    user_id = request.session["user_id"]
    user = RailwayUser.objects.get(id=user_id)

    if user.is_admin:
        user_count = RailwayUser.objects.filter(is_admin=False).count()
        train_count = Train.objects.count()
        station_count = Station.objects.count()
        booking_count = Booking.objects.count()
        bookings = Booking.objects.all().order_by("-id")[:5]

        return render(request, "admin/admindash.html", {
            "user": user,"user_count": user_count,
            "train_count": train_count,
            "station_count": station_count,
            "booking_count": booking_count,
            "bookings": bookings})

    messages.error(request, "You are not authorized to access this page.")
    return redirect("home")

def adminprofile(request):
    user_id = request.session.get("user_id")
    user = RailwayUser.objects.get(id=user_id)
    if request.method == "POST":
        form = AdminProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password:       
                if new_password == confirm_password:
                    user.password = new_password
                    user.save()
            return redirect("adminprofile")
    else:
        form = AdminProfileForm(instance=user)
    return render(request, "admin/adminprofile.html", {"form": form})


def adminuser(request):
    if request.method == "POST":
        action = request.POST["action"]

        if action == "edit":
            user_id = request.POST["user_id"]
            user = RailwayUser.objects.get(id=user_id)
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]
            user.email = request.POST["email"]
            user.phone = request.POST["phone"]
            user.username = request.POST["username"]
            if request.POST["is_admin"] == "True":
                user.is_admin = True
            else:
                user.is_admin = False
            user.save()

        elif action == "delete":
            user_id = request.POST["user_id"]
            user = RailwayUser.objects.get(id=user_id)
            user.delete()
    search = request.GET.get("search")
    if search:
        users = RailwayUser.objects.filter(username=search)
    else:
        users = RailwayUser.objects.all()
    return render(request, "admin/adminuser.html", { "users": users})


def adminstation(request):
    if request.method == "POST":
        action = request.POST["action"]
        if action == "add":
            # takes the data entered in your Add Station popup and saves it into your Station database table.
            station_name = request.POST["station_name"]
            station_code = request.POST["station_code"]
            city = request.POST["city"]
            state = request.POST["state"]

            station = Station()
            # creates a new Station object and fill that empty record:
            station.station_name = station_name
            station.station_code = station_code
            station.city = city
            station.state = state
            station.save()

        elif action=="edit":
            station_id = request.POST["station_id"]
            station = Station.objects.get(id=station_id)
            station.station_name = request.POST["station_name"]
            station.station_code = request.POST["station_code"]
            station.city = request.POST["city"]
            station.state = request.POST["state"]
            station.save()

        elif action == "delete":
            station_id = request.POST["station_id"]
            station = Station.objects.get(id=station_id)
            station.delete()

    search = request.GET.get("search", "")
    if search:
        search = search.strip()
        stations = Station.objects.filter(station_code=search.upper())
        if not stations:
            stations = []
            search_first_word = search.split()[0].capitalize()
            all_stations = Station.objects.all()
            for station in all_stations:
                first_word = station.station_name.split()[0]
                if first_word.capitalize() == search_first_word:
                    stations.append(station)
    else:
        stations = Station.objects.all()

    # PAGINATION
    paginator = Paginator(stations, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "admin/adminstation.html", {"page_obj": page_obj,"search": search})

#    TRAINS
def admintrains(request):
    if request.method == "POST":
        action = request.POST["action"]
        if action == "add":
            train_name = request.POST["train_name"]
            train_number = request.POST["train_number"]
            source = request.POST["source"]
            destination = request.POST["destination"]
            departure = request.POST["departure"]
            arrival = request.POST["arrival"]
            journey_days = request.POST["journey_days"]
            classes = request.POST["classes"]
            status = request.POST["status"]

            train = Train()
            train.train_name = train_name
            train.train_number = train_number
            train.source = Station.objects.get(id=source)
            train.destination = Station.objects.get(id=destination)
            train.departure = departure
            train.arrival = arrival
            train.journey_days = journey_days
            train.classes = classes
            train.status = status

            train.save()
        elif action == "edit":

            train_id = request.POST["train_id"]
            train = Train.objects.get(id=train_id)
            train.train_name = request.POST["train_name"]
            train.train_number = request.POST["train_number"]
            train.source = Station.objects.get( id=request.POST["source"])
            train.destination = Station.objects.get( id=request.POST["destination"])

            train.departure = request.POST["departure"]
            train.arrival = request.POST["arrival"]
            train.journey_days = request.POST["journey_days"]
            train.classes = request.POST["classes"]
            train.status = request.POST["status"]
            train.save()

        elif action == "delete":
            train_id = request.POST["train_id"]
            train = Train.objects.get(id=train_id)
            train.delete()


    train_number = request.GET.get("train_number", "")
    source = request.GET.get("source", "")
    destination = request.GET.get("destination", "")

    trains = Train.objects.all()
    if train_number:
        trains = Train.objects.filter(train_number=train_number)
    if source:
        trains = trains.filter(source=source)
    if destination:
        trains = trains.filter(destination=destination)
    for train in trains:
        if train.departure:
            train.departure = train.departure.strftime("%H:%M")

        if train.arrival:
            train.arrival = train.arrival.strftime("%H:%M")

    paginator = Paginator(trains, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    stations = Station.objects.all()
    return render(request, "admin/admintrains.html", {"page_obj": page_obj,"stations": stations,
        "train_number": train_number,"source": source,"destination": destination})

def admintrainroute(request, train_id):
    train = Train.objects.get(id=train_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            station_id = request.POST.get("station")
            stop_number = request.POST.get("stop_number")
            day_number = request.POST.get("day_number")
            arrival_time = request.POST.get("arrival_time")
            departure_time = request.POST.get("departure_time")
            # Convert empty values to None
            if stop_number:
                stop_number = int(stop_number)
            else:
                stop_number = None

            if day_number:
                day_number = int(day_number)
            else:
                day_number = None

            # Do not allow intermediate station to be Stop 1
            if stop_number is not None and stop_number <= 1:
                messages.error(request,"Intermediate station must be after Stop 1.")
            else:
                # Find destination route
                destination_route = TrainRoute.objects.filter(train=train,station=train.destination).first()
                # Keep destination as last station
                if destination_route and stop_number is not None:
                    if stop_number >= destination_route.stop_number:
                        stop_number = destination_route.stop_number
                # Shift existing routes
                if stop_number is not None:
                    existing_routes = TrainRoute.objects.filter(train=train,stop_number__gte=stop_number).order_by("-stop_number")
                    for existing_route in existing_routes:
                        existing_route.stop_number = (existing_route.stop_number + 1)
                        existing_route.save()

                # Create route
                route = TrainRoute()
                route.train = train

                if station_id:
                    route.station = Station.objects.get(id=station_id)
                else:
                    route.station = None
                route.stop_number = stop_number
                route.day_number = day_number
                route.arrival_time = ( arrival_time if arrival_time else None)
                route.departure_time = (departure_time if departure_time else None)
                route.save()

        elif action == "edit":
            route_id = request.POST.get("route_id")
            route = TrainRoute.objects.get(id=route_id,train=train)
            source_id = request.POST.get("source")
            if source_id:
                train.source = Station.objects.get(id=source_id)
            else:
                train.source = None
            destination_id = request.POST.get("destination")
            if destination_id:
                train.destination = Station.objects.get(id=destination_id)
            else:
                train.destination = None
            train.save()

            station_id = request.POST.get("station")
            if station_id:
                route.station = Station.objects.get( id=station_id)
            else:
                route.station = None

            stop_number = request.POST.get("stop_number")
            if stop_number:
                route.stop_number = int(stop_number)
            else:
                route.stop_number = None

            day_number = request.POST.get("day_number")
            if day_number:
                route.day_number = int(day_number)
            else:
                route.day_number = None


            arrival_time = request.POST.get("arrival_time")
            if arrival_time:
                route.arrival_time = arrival_time
            else:
                route.arrival_time = None

            departure_time = request.POST.get("departure_time")
            if departure_time:
                route.departure_time = departure_time
            else:
                route.departure_time = None
            route.save()
            messages.success( request, "Route updated successfully!")

        elif action == "delete":
            route_id = request.POST.get("route_id")
            route = TrainRoute.objects.get(id=route_id,train=train)
            route.delete()
            messages.success(request,"Station removed from route.")

    routes = TrainRoute.objects.filter( train=train).order_by("stop_number")
    if not routes:
        if train.source:
            source_route = TrainRoute()
            source_route.train = train
            source_route.station = train.source
            source_route.stop_number = 1
            source_route.day_number = 1
            source_route.arrival_time = None
            source_route.departure_time = train.departure
            source_route.save()

        if train.destination:
            destination_route = TrainRoute()
            destination_route.train = train
            destination_route.station = train.destination
            destination_route.stop_number = 2
            destination_route.day_number = train.journey_days
            destination_route.arrival_time = train.arrival
            destination_route.departure_time = None
            destination_route.save()

    # Get routes again
    routes = TrainRoute.objects.filter(train=train).order_by("stop_number")
    stations = Station.objects.all()

    if train.source:
        stations = stations.exclude(id=train.source.id)
    if train.destination:
        stations = stations.exclude(id=train.destination.id)
    all_stations = Station.objects.all()

    route_map_path = os.path.join(settings.BASE_DIR,"static","images","routes", str(train.train_number) + ".png")
    train.route_map_exists = os.path.exists(route_map_path)
    return render(request,"admin/admintrainroute.html",{   "train": train, "routes": routes,"stations": stations, "all_stations": all_stations})




def adminbooking(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "edit":
            booking_id = request.POST.get("booking_id")
            booking = Booking.objects.get(id=booking_id)
            booking.pnr = request.POST.get("pnr")
            booking.journey_date = request.POST.get("journey_date")
            # Calculate fare per passenger from existing booking
            fare_per_passenger = booking.total_amount / booking.passengers
            # Get new passenger count
            new_passengers = int(request.POST.get("passengers"))
            booking.passengers = new_passengers

            # Calculate new total amount
            booking.total_amount = fare_per_passenger * new_passengers
            booking.booking_status = request.POST.get("booking_status")
            booking.save()
            messages.success(request, "Booking updated successfully!")

        elif action == "delete":
            booking_id = request.POST.get("booking_id")
            booking = Booking.objects.get(id=booking_id)
            booking.delete()
            messages.success(request, "Booking deleted successfully!")
    bookings = Booking.objects.all()
    return render(request, "admin/adminbooking.html", {"bookings": bookings})



def deletebooking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.delete()
    return redirect("adminbooking")

def admincoach(request, train_id):
    train = Train.objects.get(id=train_id)
    if request.method == "POST":
        action = request.POST["action"]
        if action == "add":
            train_class = request.POST["train_class"]
            coach_number = request.POST["coach_number"]
            total_seats = request.POST["total_seats"]
            coach = Coach()
            coach.train = train
            coach.train_class = TrainClass.objects.get(id=train_class)
            coach.coach_number = coach_number
            coach.total_seats = total_seats
            coach.save()

        elif action == "delete":
            coach_id = request.POST["coach_id"]
            coach = Coach.objects.get(id=coach_id)
            coach.delete()
    classes = TrainClass.objects.filter(train=train)
    coaches = Coach.objects.filter(train=train)

    return render(request, "admin/admincoach.html", { "train": train, "classes": classes, "coaches": coaches})



def admintrainclass(request, train_id):
    train = Train.objects.get(id=train_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            class_name = request.POST.get("class_name")
            total_seats = request.POST.get("total_seats")
            fare = request.POST.get("fare")
            if class_name and total_seats and fare:
                # Find the ClassType
                class_type = ClassType.objects.filter(class_name=class_name).first()
                # If ClassType does not exist, create it
                if not class_type:
                    class_type = ClassType()
                    class_type.class_name = class_name
                    class_type.save()

                # Create TrainClass
                train_class = TrainClass()
                train_class.train = train
                train_class.class_type = class_type
                train_class.total_seats = total_seats
                train_class.fare = fare
                train_class.save()

        elif action == "delete":
            class_id = request.POST.get("class_id")
            if class_id:
                train_class = TrainClass.objects.filter( id=class_id, train=train).first()
                if train_class:
                    train_class.delete()

    classes = TrainClass.objects.filter(train=train)
    return render(request, "admin/admintrainclass.html", { "train": train, "classes": classes})


def adminbookingdetails():
    pass

def admincancellations(request):
    cancellations = Cancellation.objects.all().order_by("-id")
    return render(request, "admin/admincancellations.html", {"cancellations": cancellations})















def staffdash(request):
    staff_messages = StaffMessage.objects.filter(user__is_admin=False).order_by("-created_at")
    total_messages = StaffMessage.objects.filter(user__is_admin=False).count()
    resolved_messages = StaffMessage.objects.filter(user__is_admin=False, is_read=True).count()
    return render(request, "staff/staffdash.html", {"staff_messages": staff_messages,"total_messages": total_messages, "resolved_messages": resolved_messages})


def chatstaff(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = RailwayUser.objects.get(id=user_id)
    if request.method == "POST":
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        booking = Booking.objects.filter( user_id=user_id ).order_by("-id").first()
        message = StaffMessage()
        message.user = user
        message.booking = booking
        message.subject = subject
        message.message = message_text
        message.save()
        messages.success(request, "Your message has been sent to staff.")
        return redirect("chatstaff")

    user_messages = StaffMessage.objects.filter(user_id=user_id).order_by("created_at")
    return render(request, "chatstaff.html", {"user_messages": user_messages})


def reply_staff_message(request, message_id):
    staff_id = request.session.get("user_id")
    if not staff_id:
        return redirect("login")
    staff = RailwayUser.objects.get(id=staff_id)
    if staff.is_staff == False:
        return redirect("home")
    message = StaffMessage.objects.get(id=message_id)
    if request.method == "POST":
        reply_text = request.POST.get("staff_reply")
        if reply_text:
            message.staff_reply = reply_text
            message.replied_at = timezone.now()
            message.is_read = True
            message.save()
            messages.success(request,"Reply sent successfully.")
    return redirect("staffdash")

def delete_staff_message(request, message_id):
    staff_id = request.session.get("user_id")
    # Check staff is logged in
    if not staff_id:
        return redirect("login")
    staff = RailwayUser.objects.get(id=staff_id)
    # Only staff can delete messages
    if not staff.is_staff:
        return redirect("home")
    # Delete only when form is submitted
    if request.method == "POST":
        message = StaffMessage.objects.get(id=message_id)
        message.delete()
        messages.success(request,"Message deleted successfully.")
    return redirect("staffdash")





from huggingface_hub import InferenceClient
client = InferenceClient(api_key="" ,provider="novita")

def chatai(request):
    if request.method == "POST":
        prompt = request.POST.get("prompt")
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {  "role": "system",
                    "content": """
                    You are the Railway Booking System AI Assistant.
                    Help users with:
                    - Train booking
                    - Train cancellation
                    - PNR
                    - Railway classes
                    - Payments
                    - Stations
                    - Journey information
                    - General questions about using this railway booking website.

                    Give clear, simple and helpful answers.

                    If the question is unrelated to railway services,
                    politely say that you can mainly help with railway
                    booking and related questions.
                    """
                },
                {"role": "user", "content": prompt}],
            max_tokens=500,stream=False)
        msg = response.choices[0].message.content
        # Get logged-in user's previous staff messages
        user_id = request.session.get("user_id")
        if user_id:
            user_messages = StaffMessage.objects.filter(user_id=user_id).order_by("subject", "created_at")
        else:
            user_messages = []
        return render(request,"chatai.html", {"result": msg,"prompt": prompt})
    return render(request, "chatai.html")