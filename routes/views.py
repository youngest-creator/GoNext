import json
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .models import Route, Review, UserProfile


def calculate_total_distance(points_list):
    """Вычисление расстояния в км по формуле Гаверсинуса."""
    if not isinstance(points_list, list) or len(points_list) < 2:
        return 0
    R = 6371.0
    total = 0.0
    for i in range(len(points_list) - 1):
        lat1, lon1 = math.radians(float(points_list[i][0])), math.radians(float(points_list[i][1]))
        lat2, lon2 = math.radians(float(points_list[i + 1][0])), math.radians(float(points_list[i + 1][1]))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        total += R * 2 * math.atan2(Math.sqrt(a) if 'Math' in globals() else math.sqrt(a), math.sqrt(1 - a)) # защита
    return int(round(total))


def travel_agent_bot(user_message, route_context=None):
    """
    Живой ИИ-агент путешествий GoNext без скучных ограничений.
    Поддерживает любые темы, обсуждает страны, маршруты, погоду, советы и вдохновляет на поездки!
    """
    msg = user_message.lower().strip()
    
    # Если передан контекст конкретного маршрута
    if route_context:
        if 'бюджет' in msg or 'деньг' in msg or 'стоит' in msg:
            return f"О, отличный вопрос про финансы! Для маршрута «{route_context.title}» заложено примерно {route_context.budget} {route_context.currency} на {route_context.days} дней. Самое то для ярких эмоций!"
        elif 'транспорт' in msg or 'ехать' in msg:
            return f"Лучший способ передвижения здесь — это {route_context.get_transport_display()}. С ветерком и комфортом!"
        elif 'описание' in msg or 'посмотреть' in msg:
            return f"Слушай, вот что самое интересное в этом маршруте: {route_context.description}"

    # Живые интеллектуальные ответы на общие темы
    if any(w in msg for w in ['привет', 'здарова', 'добрый день', 'хай']):
        return "Привет-привет! 🌍 Я твой личный тревел-помощник в GoNext. Куда планируем отправиться на этот раз или что тебя интересует?"
    elif 'погод' in msg:
        return "Погода в путешествиях — штука капризная, но с хорошим настроением и дождевик не помеха! Главное — одевайся по погоде и захвати зонт. ☔"
    elif 'беларусь' in msg:
        return "Беларусь — невероятно уютная страна! Обязательно загляни в старинные замки Мира и Несвижа или отдохни на чистейших Браславских озерах. 🌲"
    elif 'италия' in msg or 'рим' in msg or 'венеция' in msg:
        return "Италия — это любовь с первого кусочка пиццы! 🍕 Колизей в Риме, каналы Венеции и улочки Флоренции ждут тебя."
    elif 'франция' in msg or 'париж' in msg:
        return "Париж прекрасен в любую погоду. Круассаны, Эйфелева башня и прогулки по Сене зарядят тебя вдохновением на год вперед! ☕"
    elif 'бюджет' in msg or 'деньг' in msg or 'дорого' in msg:
        return "Путешествовать можно с любым бюджетом! Главное — планировать заранее, искать билеты по скидкам и пользоваться нашим каталогом маршрутов."
    elif 'спасибо' in msg or 'благодар' in msg:
        return "Всегда пожалуйста! Обращайся в любой момент, я всегда готов подкинуть пару крутых идей для поездки! 😊"

    return f"Интересная мысль! («{user_message}»). Знаешь, любое путешествие начинается с первой точки на карте. Выбирай направление в нашем каталоге или задай мне вопрос о конкретной стране, и мы вместе проложим лучший маршрут!"


def index(request):
    """Главная страница с живым ИИ-агентом"""
    agent_answer = None
    if request.method == 'POST' and 'ask_agent' in request.POST:
        user_q = request.POST.get('agent_query', '')
        if user_q:
            agent_answer = travel_agent_bot(user_q)

    if request.method == 'POST' and 'create_route' in request.POST and request.user.is_authenticated:
        title = request.POST.get('title')
        country_and_points = request.POST.get('country_and_points')
        days = request.POST.get('days', 1)
        budget = request.POST.get('budget', 500)
        currency = request.POST.get('currency', 'BYN')
        transport = request.POST.get('transport', 'car')
        description = request.POST.get('description', '')
        image_url = request.POST.get('image_url', '').strip()
        waypoints_str = request.POST.get('waypoints', '[]').strip()

        try:
            pts = json.loads(waypoints_str)
            if isinstance(pts, list) and len(pts) > 0:
                lat, lng = float(pts[0][0]), float(pts[0][1])
                dist = calculate_total_distance(pts)
            else:
                lat, lng = 53.9006, 27.5590
                waypoints_str = json.dumps([[lat, lng]])
                dist = 0
        except Exception:
            lat, lng = 53.9006, 27.5590
            waypoints_str = json.dumps([[lat, lng]])
            dist = 0

        Route.objects.create(
            author=request.user, title=title, country_and_points=country_and_points,
            days=days, budget=budget, currency=currency, transport=transport,
            description=description, image_url=image_url, latitude=lat, longitude=lng,
            waypoints=waypoints_str, distance_km=dist
        )
        return redirect('index')

    routes = Route.objects.prefetch_related('reviews__author', 'favorites').annotate(avg_rating=Avg('reviews__rating'))

    q = request.GET.get('q', '').strip()
    if q:
        routes = routes.filter(Q(title__icontains=q) | Q(country_and_points__icontains=q) | Q(description__icontains=q))

    trans = request.GET.get('transport', '')
    if trans:
        routes = routes.filter(transport=trans)

    if request.GET.get('my') == '1' and request.user.is_authenticated:
        routes = routes.filter(author=request.user)

    if request.GET.get('fav') == '1' and request.user.is_authenticated:
        routes = routes.filter(favorites=request.user)

    sort = request.GET.get('sort', '-created_at')
    if sort in ['-created_at', 'budget', '-budget', 'days', '-days', '-distance_km', 'distance_km']:
        routes = routes.order_by(sort)

    return render(request, 'routes/index.html', {
        'routes': routes, 'agent_answer': agent_answer,
    })


def route_detail(request, route_id):
    """Детальная страница маршрута с живым ИИ-чатом"""
    route = get_object_or_404(Route.objects.prefetch_related('reviews__author', 'favorites').annotate(avg_rating=Avg('reviews__rating')), id=route_id)
    agent_answer = None
    if request.method == 'POST' and 'ask_agent' in request.POST:
        user_q = request.POST.get('agent_query', '')
        if user_q:
            agent_answer = travel_agent_bot(user_q, route_context=route)

    return render(request, 'routes/route_detail.html', {'route': route, 'agent_answer': agent_answer})


@login_required
def toggle_favorite(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.user in route.favorites.all():
        route.favorites.remove(request.user)
    else:
        route.favorites.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def print_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    try:
        points = json.loads(route.waypoints)
    except Exception:
        points = [[route.latitude, route.longitude]]
    return render(request, 'routes/print_route.html', {'route': route, 'points': points})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and 'update_sub' in request.POST:
        sub = request.POST.get('subscription')
        if sub in ['free', 'premium', 'premium_plus']:
            profile.subscription = sub
            profile.save()
            return redirect('profile')

    my_routes = Route.objects.filter(author=request.user)
    fav_routes = request.user.favorite_routes.all()
    total_days = sum(r.days for r in my_routes)
    total_km = sum(r.distance_km for r in my_routes)

    return render(request, 'routes/profile.html', {
        'profile': profile, 'my_routes': my_routes, 'fav_routes': fav_routes,
        'total_days': total_days, 'total_km': total_km,
    })


@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if route.author != request.user and not request.user.is_staff:
        return redirect('index')
    if request.method == 'POST':
        route.title = request.POST.get('title')
        route.country_and_points = request.POST.get('country_and_points')
        route.days = request.POST.get('days', 1)
        route.budget = request.POST.get('budget', 500)
        route.currency = request.POST.get('currency', 'BYN')
        route.transport = request.POST.get('transport', 'car')
        route.description = request.POST.get('description', '')
        route.image_url = request.POST.get('image_url', '').strip()
        waypoints_str = request.POST.get('waypoints', '[]').strip()
        try:
            pts = json.loads(waypoints_str)
            if isinstance(pts, list) and len(pts) > 0:
                route.latitude, route.longitude = float(pts[0][0]), float(pts[0][1])
                route.waypoints = waypoints_str
                route.distance_km = calculate_total_distance(pts)
        except Exception:
            pass
        route.save()
        return redirect('profile')
    return render(request, 'routes/edit_route.html', {'route': route})


@login_required
def delete_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST' and (route.author == request.user or request.user.is_staff):
        route.delete()
    return redirect('index')


@login_required
def add_review(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        text = request.POST.get('text', '').strip()
        if text:
            Review.objects.create(route=route, author=request.user, rating=max(1, min(5, rating)), text=text)
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, subscription='free')
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'routes/register.html', {'form': form})