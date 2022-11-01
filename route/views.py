import json

from bson import ObjectId
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from route import models
from django.db import connection
from mongo_utils import MongoDBConnection

import pymongo


# client = MongoClient('localhost', 27017)

# Create your views here.

###################################################################
def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []
    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")

    filter_string = ' and '.join(query_filter)
    joining = """ SELECT route_route.country,
                         route_route.description,
                         route_route.duration,
                         route_route.stopping_point,
                         route_route.route_type,
                         start_point.name,
                         end_point.name
                    FROM route_route 
                    JOIN route_places AS start_point ON start_point.id = route_route.starting_point
                    JOIN route_places AS end_point ON end_point.id = route_route.destination
                    WHERE """ + filter_string
    print(joining)
    cursor.execute(joining)
    result = cursor.fetchall()

    new_result = [{"country": i[0], "description": i[1], "duration": i[2],
                   "stopping_point": i[3], "route_type": i[4], "start": i[5],
                   "end": i[6]} for i in result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['stop_points']
        stop_point = collec.find_one({"_id": ObjectId(new_result[0]['stopping_point'])})
        print(f"{stop_point}")
    # return HttpResponse(new_result)
    return HttpResponse([new_result, stop_point])


def route_detail(request, id):
    result = models.Route.objects.all().filter(id=id)
    return HttpResponse([{'country': itm.country, 'id': itm.id} for itm in result])


def route_reviews(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    return HttpResponse([{'route_id': itm.route_id, 'review_rate': itm.review_rate} for itm in result])


def route_add(request):
    if request.method == 'GET':
        return render(request, 'add_route.html')
    if request.method == 'POST':
        dest = request.POST.get('destination')
        stop_points = request.POST.get('stop_points')
        start_point = request.POST.get('starting_point')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        route_type = request.POST.get('route_type')

        stop_list = json.loads(stop_points)
        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            collec = db['stop_points']
            id_stop_points = collec.insert_one({'points': stop_list}).inserted_id

        start_obj = models.Places.objects.get(name=start_point)
        dest_obj = models.Places.objects.get(name=dest)

        new_route = models.Route(starting_point=start_obj.id, destination=dest_obj.id,
                                 country=country, location=location, description=description,
                                 duration=duration, route_type=route_type, stopping_point=id_stop_points)
        new_route.save()
    return HttpResponse('Creating a route')


def route_add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event_route.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')
            new_event = models.Event(id_route=route_id,
                                     event_admin=1,
                                     approved_users=[],
                                     pending_users=[],
                                     start_date=start_date, price=price)
            new_event.save()
            return HttpResponse('Adding event')
    else:
        return HttpResponse('Not allowed to add event')


####################################################
# def event_handler(request, event_id):
#     result = models.Event.objects.all().filter(id=event_id)
#     return HttpResponse(
#         [{'id_route': itm.id_route, 'start_date': itm.start_date, 'price': itm.price} for itm in result])

def event_handler(request, event_id):
    cursor = connection.cursor()
    sql_query = f"""  SELECT route_event.id,
       route_event.start_date,
       route_event.price,
       route.country,
       route.description,
       route.duration,
       route.stopping_point,
       route.route_type,
       route_event.event_users
FROM route_event
JOIN route_route AS route ON route.id = route_event.id_route
                                                WHERE route_event.id = {event_id}"""

    cursor.execute(sql_query)
    result = cursor.fetchall()

    new_result = [{"event_id": i[0], "start_date": i[1], "price": i[2],
                   "country": i[3], "description": i[4], "duration": i[5],
                   "stopping_point": i[6], "route_type": i[7], "id_event_users": i[8]} for i in result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collec = db['events_users']
        id_users = collec.find_one({"_id": ObjectId(new_result[0].get('id_event_users'))})

    users_accepted = User.objects.filter(pk__in=id_users['accepted'])
    users_pending = User.objects.filter(pk__in=id_users['pending'])

    list_users_accepted = [{itm.id: itm.username} for itm in users_accepted]
    list_users_pending = [{itm.id: itm.username} for itm in users_pending]

    new_result[0]['accepted user'] = list_users_accepted
    new_result[0]['pending user'] = list_users_pending

    return HttpResponse([new_result])


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('No user')
    else:
        return HttpResponse('<a href="logout">logout</a>')


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'registration.html')
        if request.method == 'POST':
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name'))
            user.save()
            return HttpResponse('User is created')
    else:
        return HttpResponse('<a href="logout">logout</a>')


def logout_user(request):
    logout(request)
    # print(request.user.has_perm('route.event'))
    return redirect('/login')


def add_me_to_event(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        event_users = db['events_users']
        all_event_users = event_users.find_one({"_id": ObjectId(event.event_users)})

        if user not in all_event_users['pending'] and user not in all_event_users['accepted']:
            all_event_users['pending'].append(user)
            event_users.update_one({"_id": ObjectId(all_event_users)}, {"$set": all_event_users}, upsert=False)
        else:
            return HttpResponse('You are in pending users or accepted')


