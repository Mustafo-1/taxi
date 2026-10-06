from django.conf import settings
from django.db import models

class Tariff(models.Model):
    name = models.CharField("Nomi", max_length=40)
    description = models.CharField("Tavsif", max_length=120)
    seats = models.PositiveSmallIntegerField("O'rinlar", default=4)
    eta_min = models.PositiveSmallIntegerField("Kutish (daq.)", default=3)
    base_price = models.PositiveIntegerField("Boshlang'ich narx (so'm)")
    per_km = models.PositiveIntegerField("1 km narxi (so'm)")
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        verbose_name = "Tarif"
        verbose_name_plural = "Tariflar"

    def __str__(self):
        return self.name

class Profile(models.Model):
    class Role(models.TextChoices):
        PASSENGER = "passenger", "Yo'lovchi"
        DRIVER = "driver", "Haydovchi"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField("Rol", max_length=10, choices=Role.choices, default=Role.PASSENGER)
    phone = models.CharField("Telefon", max_length=20)
    car_model = models.CharField("Mashina", max_length=60, blank=True)
    car_plate = models.CharField("Davlat raqami", max_length=15, blank=True)
    is_available = models.BooleanField("Onlayn", default=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"

    @property
    def name(self):
        return self.user.first_name or self.user.username

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Haydovchi qidirilmoqda"
        ASSIGNED = "assigned", "Haydovchi topildi"
        DONE = "done", "Bajarildi"
        CANCELED = "canceled", "Bekor qilindi"

    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="orders", verbose_name="Yo'lovchi")
    driver = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="trips", verbose_name="Haydovchi", limit_choices_to={"role": "driver"})
    pickup = models.CharField("Qayerdan", max_length=200)
    dropoff = models.CharField("Qayerga", max_length=200)
    phone = models.CharField("Telefon", max_length=20)
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, related_name="orders", verbose_name="Tarif")
    distance_km = models.DecimalField("Masofa (km)", max_digits=5, decimal_places=1, default=5)
    price = models.PositiveIntegerField("Narx (so'm)", default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"#{self.pk} {self.pickup} → {self.dropoff}"

    def save(self, *args, **kwargs):
        if self.driver_id and self.status == self.Status.NEW:
            self.status = self.Status.ASSIGNED
        elif not self.driver_id and self.status == self.Status.ASSIGNED:
            self.status = self.Status.NEW
        super().save(*args, **kwargs)


