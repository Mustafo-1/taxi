import random
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import OrderForm, RegisterForm
from .models import Order, Profile, Tariff

def index(request):
    return render(request, "index.html", {"tariffs": Tariff.objects.all()})

def register(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("driver_panel" if user.profile.role == "driver" else "index")
    return render(request, "register.html", {"form": form})

@login_required
def order(request):
    if request.method != "POST":
        return redirect("index")
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "passenger":
        messages.error(request, "Buyurtma berish uchun yo'lovchi akkaunti bilan kiring")
        return redirect("/#buyurtma")
    form = OrderForm(request.POST)
    if not form.is_valid():
        for errs in form.errors.values():
            messages.error(request, errs[0])
        return redirect("/#buyurtma")
    o = form.save(commit=False)
    o.passenger, o.phone = request.user, profile.phone
    busy = Order.objects.filter(status="assigned", driver__isnull=False).values_list("driver", flat=True)
    free = list(Profile.objects.filter(role="driver", is_available=True).exclude(pk__in=busy))
    if free:
        o.driver, o.status = random.choice(free), "assigned"
    o.save()
    return redirect("order_detail", pk=o.pk)

@login_required
def order_detail(request, pk):
    o = get_object_or_404(Order.objects.select_related("driver__user", "tariff"), pk=pk)
    p = getattr(request.user, "profile", None)
    if not (request.user.is_staff or o.passenger_id == request.user.id or (p and o.driver_id == p.id)):
        raise Http404
    step = {"new": 0, "assigned": 1, "done": 2}.get(o.status, -1)
    steps = [("Buyurtma qabul qilindi", "Dispetcher haydovchi qidirmoqda"),
             ("Haydovchi topildi", "Haydovchi yo'lda va tez orada qo'ng'iroq qiladi"),
             ("Safar yakunlandi", "Yo'l bo'lsin!")]
    return render(request, "order_detail.html", {"order": o, "step": step, "steps": steps})

@login_required
def driver_panel(request):
    p = getattr(request.user, "profile", None)
    if not p or p.role != "driver":
        return redirect("index")
    active = Order.objects.filter(driver=p, status="assigned").select_related("tariff", "passenger").first()
    if request.method == "POST":
        action, pk = request.POST.get("action"), request.POST.get("pk", "")
        if action == "toggle":
            p.is_available = not p.is_available
            p.save()
        elif action == "accept" and not active and pk.isdigit():
            Order.objects.filter(pk=pk, status="new").update(driver=p, status="assigned")
        elif action == "finish" and active:
            active.status = "done"
            active.save()
        return redirect("driver_panel")
    new_orders = [] if active else Order.objects.filter(status="new").select_related("tariff")
    return render(request, "driver_panel.html", {"p": p, "active": active, "new_orders": new_orders})

@login_required
def order(request):
    if request.method != "POST":
        return redirect("index")
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != "passenger":
        messages.error(request, "Buyurtma berish uchun yo'lovchi akkaunti bilan kiring")
        return redirect("/#buyurtma")
    form = OrderForm(request.POST)
    if not form.is_valid():
        for errs in form.errors.values():
            messages.error(request, errs[0])
        return redirect("/#buyurtma")
    o = form.save(commit=False)
    o.passenger, o.phone = request.user, profile.phone
    o.save()
    return redirect("order_detail", pk=o.pk)

@login_required
def driver_panel(request):
    p = getattr(request.user, "profile", None)
    if not p or p.role != "driver":
        return redirect("index")
    active = Order.objects.filter(driver=p, status="assigned").select_related("tariff", "passenger").first()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle":
            p.is_available = not p.is_available
            p.save()
        elif action == "finish" and active:
            active.status = "done"
            active.save()
        return redirect("driver_panel")
    return render(request, "driver_panel.html", {"p": p, "active": active})
