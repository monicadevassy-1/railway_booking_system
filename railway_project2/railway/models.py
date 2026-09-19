from django.db import models

# Create your models here.

# 1. USER
# =========================================================

class RailwayUser(models.Model):
    username = models.CharField(max_length=50,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50,blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    gender = models.CharField(max_length=20,choices=[
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"), ])
    date_of_birth = models.DateField(null=True,blank=True)
    
    is_verified = models.BooleanField(default=False)
    # not used
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    def __str__(self):
        return self.username


# 2. EMAIL OTP
# =========================================================

class EmailOTP(models.Model):
    user = models.ForeignKey(RailwayUser,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    # not used
    def __str__(self):
        return self.user.email


# 3. STATION
# =========================================================

class Station(models.Model):
    station_code = models.CharField(max_length=10, unique=True)
    station_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.station_name} ({self.station_code})"


# 4. TRAIN
# =========================================================

class Train(models.Model):
    train_name = models.CharField(max_length=100)
    train_number = models.IntegerField()
    source = models.ForeignKey(Station,on_delete=models.CASCADE,related_name="source_trains",null=True,
    blank=True)
    destination = models.ForeignKey( Station,on_delete=models.CASCADE, related_name="destination_trains",null=True,
    blank=True)
    departure = models.TimeField(null=True, blank=True)
    arrival = models.TimeField(null=True, blank=True)
    classes = models.CharField(max_length=100, blank=True,null=True)
    status = models.CharField(max_length=20, blank=True,null=True)
    journey_days = models.IntegerField(default=1,null=True)
    route_map = models.ImageField(upload_to="route_maps/", null=True, blank=True)
    def __str__(self):
        return self.train_name

# 5. TRAIN ROUTE
# =========================================================

class TrainRoute(models.Model):
    train = models.ForeignKey(Train,on_delete=models.CASCADE)
    station = models.ForeignKey( Station, on_delete=models.SET_NULL, null=True, blank=True)
    stop_number = models.IntegerField( null=True, blank=True)
    arrival_time = models.TimeField( null=True, blank=True)
    departure_time = models.TimeField(null=True,blank=True)
    day_number = models.IntegerField(null=True,blank=True)
    def __str__(self):
        if self.station:
            return self.train.train_name + " - " + self.station.station_name
        return self.train.train_name + " - No Station"

class ClassType(models.Model):
    class_name = models.CharField( max_length=50, unique=True)
    def __str__(self):
        return self.class_name

    
# 6. TRAIN CLASS
# =========================================================
class TrainClass(models.Model):
    train = models.ForeignKey(Train,on_delete=models.CASCADE)
    class_type = models.ForeignKey(ClassType,on_delete=models.CASCADE,null=True,blank=True)
    total_seats = models.IntegerField()
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        if self.class_type:
            return self.train.train_name + " - " + self.class_type.class_name
        return self.train.train_name + " - No Class"


# COACH
# =========================================================
class Coach(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    train_class = models.ForeignKey(TrainClass, on_delete=models.CASCADE)
    coach_number = models.CharField(max_length=10)
    total_seats = models.IntegerField()
    def __str__(self):
        return self.coach_number


# 7. TRAIN SCHEDULE---not using
# =========================================================
class TrainSchedule(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    journey_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    def __str__(self):
        return self.train.train_name


# 8. PASSENGER
# =========================================================
class Passenger(models.Model):
    user = models.ForeignKey( RailwayUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# 9. BOOKING
# =========================================================
class Booking(models.Model):
    pnr = models.CharField(max_length=10,unique=True,null=True,blank=True)
    user = models.ForeignKey( RailwayUser, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    starting_station = models.ForeignKey( Station, on_delete=models.CASCADE, related_name="booking_starts", null=True, blank=True)
    destination_station = models.ForeignKey(Station,  on_delete=models.CASCADE,  related_name="booking_destinations",null=True,  blank=True)
    journey_date = models.DateField()
    passengers = models.IntegerField(default=1)
    train_class = models.ForeignKey( TrainClass, on_delete=models.CASCADE, null=True, blank=True)
    fare = models.DecimalField(  max_digits=10,  decimal_places=2,  null=True,  blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_status = models.CharField(  max_length=20,choices=[
            ("Confirmed", "Confirmed"),
            ("Cancelled", "Cancelled"),
            ("Pending", "Pending"),] )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.pnr


# 10. BOOKING PASSENGER
# =========================================================

class BookingPassenger(models.Model):
    booking = models.ForeignKey(Booking,on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger,on_delete=models.CASCADE)
    train_class = models.ForeignKey(TrainClass,on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20,blank=True)
    fare = models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return self.passenger.name


# 11. PAYMENT
# =========================================================

class Payment(models.Model):
    booking = models.ForeignKey(Booking,on_delete=models.CASCADE)
    payment_amount = models.DecimalField( max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=30)
    payment_status = models.CharField(max_length=20,choices=[
            ("Success", "Success"),
            ("Failed", "Failed"),
            ("Pending", "Pending"),])
    payment_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.booking.id)
    
# 12. CANCELLATION
# =========================================================

class Cancellation(models.Model):

    booking = models.ForeignKey( Booking,on_delete=models.CASCADE)
    cancellation_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255,blank=True)
    refund_amount = models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return str(self.booking.id)

    
class StaffMessage(models.Model):
    user = models.ForeignKey( RailwayUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(  Booking, on_delete=models.CASCADE,  null=True,  blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField( auto_now_add=True)
    is_read = models.BooleanField(default=False)
    staff_reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField( blank=True,null=True)
    def __str__(self):
        return self.subject