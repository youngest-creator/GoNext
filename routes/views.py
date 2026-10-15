from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Route


def index(request):
    if request.method == 'POST' and request.user.is_authenticated:
        title = request.POST.get('title')
        country_and_points = request.POST.get('country_and_points')
        days = request.POST.get('days', 1)
        budget = request.POST.get('budget', 500)
        currency = request.POST.get('currency', 'BYN')
        transport = request.POST.get('transport', 'car')
        description = request.POST.get('description', '')
        
        lat_str = request.POST.get('latitude', '53.9006').replace(',', '.')
        lng_str = request.POST.get('longitude', '27.5590').replace(',', '.')
        
        try:
            latitude = float(lat_str)
            longitude = float(lng_str)
        except ValueError:
            latitude, longitude = 53.9006, 27.5590

        Route.objects.create(
            author=request.user,
            title=title,
            country_and_points=country_and_points,
            days=days,
            budget=budget,
            currency=currency,
            transport=transport,
            description=description,
            latitude=latitude,
            longitude=longitude
        )
        return redirect('index')

    routes = Route.objects.all()

    search_query = request.GET.get('q', '').strip()
    if search_query:
        routes = routes.filter(
            Q(title__icontains=search_query) |
            Q(country_and_points__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    transport_filter = request.GET.get('transport', '')
    if transport_filter:
        routes = routes.filter(transport=transport_filter)

    only_my = request.GET.get('my', '') == '1'
    if only_my and request.user.is_authenticated:
        routes = routes.filter(author=request.user)

    return render(request, 'routes/index.html', {
        'routes': routes,
        'search_query': search_query,
        'transport_filter': transport_filter,
        'only_my': only_my,
    })


@login_required
def delete_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST' and (route.author == request.user or request.user.is_staff):
        route.delete()
    return redirect('index')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'routes/register.html', {'form': form})