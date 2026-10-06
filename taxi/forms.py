import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Profile

INPUT = "w-full rounded-2xl bg-mist px-4 py-3.5 outline-none font-semibold placeholder:text-black/40"

class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(label="Rol", choices=Profile.Role.choices, widget=forms.RadioSelect, initial="passenger")
    first_name = forms.CharField(label="Ism", max_length=40)
    phone = forms.CharField(label="Telefon", max_length=20)
    car_model = forms.CharField(label="Mashina modeli (masalan, Chevrolet Cobalt)", max_length=60, required=False)
    car_plate = forms.CharField(label="Mashina raqami (masalan, 01 A 123 BC)", max_length=15, required=False)
    field_order = ["role", "first_name", "username", "phone", "car_model", "car_plate", "password1", "password2"]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Login"
        self.fields["password1"].label = "Parol"
        self.fields["password2"].label = "Parolni takrorlang"
        for f in self.fields.values():
            if not isinstance(f.widget, forms.RadioSelect):
                f.widget.attrs.update({"class": INPUT, "placeholder": f.label})

    def clean_phone(self):
        digits = re.sub(r"\D", "", self.cleaned_data["phone"])
        if len(digits) == 9:
            digits = "998" + digits
        if not (len(digits) == 12 and digits.startswith("998")):
            raise forms.ValidationError("Telefon raqamni +998 90 123 45 67 ko'rinishida kiriting")
        return "+" + digits

    def clean(self):
        data = super().clean()
        if data.get("role") == "driver":
            for name in ("car_model", "car_plate"):
                if not data.get(name):
                    self.add_error(name, "Haydovchi uchun majburiy")
        return data

    def save(self, commit=True):
        user = super().save(commit)
        d = self.cleaned_data
        Profile.objects.create(user=user, role=d["role"], phone=d["phone"],
                               car_model=d.get("car_model", ""), car_plate=d.get("car_plate", "").upper())
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["pickup", "dropoff", "tariff", "distance_km"]

    def clean_distance_km(self):
        km = self.cleaned_data["distance_km"]
        if not (0.5 <= km <= 200):
            raise forms.ValidationError("Masofa 0.5 dan 200 km gacha bo'lishi kerak")
        return km

    def save(self, commit=True):
        order = super().save(commit=False)
        t = order.tariff
        order.price = round((t.base_price + t.per_km * float(order.distance_km)) / 500) * 500
        if commit:
            order.save()
        return order

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ism", max_length=40)
    phone = forms.CharField(label="Telefon", max_length=20)
    field_order = ["first_name", "username", "phone", "password1", "password2"]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Login"
        self.fields["password1"].label = "Parol"
        self.fields["password2"].label = "Parolni takrorlang"
        for f in self.fields.values():
            f.widget.attrs.update({"class": INPUT, "placeholder": f.label})

    def clean_phone(self):
        digits = re.sub(r"\D", "", self.cleaned_data["phone"])
        if len(digits) == 9:
            digits = "998" + digits
        if not (len(digits) == 12 and digits.startswith("998")):
            raise forms.ValidationError("Telefon raqamni +998 90 123 45 67 ko'rinishida kiriting")
        return "+" + digits

    def save(self, commit=True):
        user = super().save(commit)
        Profile.objects.create(user=user, role="passenger", phone=self.cleaned_data["phone"])
        return user
