from flask import abort, render_template, request, redirect
from webapp.ext.database import instance
from .forms import FlagForm
from flask_paginate import Pagination, get_page_parameter
from bson.objectid import ObjectId

ROWS_PER_PAGE = 5
 
def index():
    return render_template("index.html")

def monitored():
    collection_monitored = 'monitored_animals'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    result = get_documents(collection_monitored, None, (page-1)*ROWS_PER_PAGE)
    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=result.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("monitored.html",pagination=pagination, monitored_animals=result, title="Animais Monitorados")

def identified():
    collection_identified = 'identified_animals'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    result = get_documents(collection_identified, {'identified': True}, (page-1)*ROWS_PER_PAGE)
    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=result.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("identified.html",pagination=pagination, identified_animals=result, title="Animais Identificados")

def not_identified():
    collection_identified = 'identified_animals'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    result = get_documents(collection_identified, {'identified': False}, (page-1)*ROWS_PER_PAGE)
    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=result.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("notidentified.html",pagination=pagination, identified_animals=result, title="Animais não Identificados")

def notification():
    collection_notifications = 'notifications'
    collection_monitored = 'monitored_animals'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)

    action = request.args.get('action')
    if action:
        obj = {'read': True}
        id_doc = request.args.get('_id')
        filter = {'_id': ObjectId(id_doc)}
        up_document(collection_notifications, filter, obj)
    notifications = get_documents(collection_notifications, {'read': False}, (page-1)*ROWS_PER_PAGE)
    result = []
    for notification in notifications:
        monitored_animal = get_one_document(collection_monitored, {'_id': notification['animal_id']})
        notification['date'] = monitored_animal['capture_date']
        result.append(notification)
    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=notifications.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("notification.html", pagination=pagination, notifications=result, title="Notificações")

def flag():
    filtro = {'active': True}
    collection_flags = 'flags'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    action = request.args.get('action')
    if action:
        obj = {'active': False}
        id_doc = request.args.get('_id')
        filter = {'_id': ObjectId(id_doc)}
        up_document(collection_flags, filter, obj)
   
    form = FlagForm()
    
    if request.method == 'POST':
        if form.inserir_flag.data:
            labels = form.labels.data.splitlines()
            animal = form.animal.data
            new_flag = dict()
            new_flag['labels'] = labels
            new_flag['animal'] = animal
            new_flag['active'] = True
            add_document(collection_flags, new_flag)
            form.labels.data = ''
            form.animal.data = ''
    result = get_documents(collection_flags,filtro, (page-1)*ROWS_PER_PAGE)
    
    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=result.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("flag.html",pagination=pagination, form=form, flags=result, title="Flags")

def history():
    collection_notifications = 'notifications'
    collection_monitored = 'monitored_animals'
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    notifications = get_documents(collection_notifications, None, (page-1)*ROWS_PER_PAGE)
    result = []
    for notification in notifications:
        monitored_animal = get_one_document(collection_monitored, {'_id': notification['animal_id']})
        notification['date'] = monitored_animal['capture_date']
        result.append(notification)

    pagination = Pagination(page=page, per_page=ROWS_PER_PAGE, 
                                    total=notifications.count(), search=search, css_framework='bootstrap3', record_name='result')
    return render_template("history.html", pagination=pagination, notifications=result, title="Histórico de Notificações")

def add_document(collection: str, document: dict()):
    instance.db[collection].insert_one(document)

def get_documents(collection: str, filter: object, skip: int):
    if filter is None:
        return instance.db[collection].find().skip(skip).limit(ROWS_PER_PAGE)
    return instance.db[collection].find(filter).skip(skip).limit(ROWS_PER_PAGE)

def up_document(collection: str, filter: str, obj_up: object):
    return instance.db[collection].update_one(filter, {'$set': obj_up} )

def get_one_document(collection: str, filter: object):
    if filter is None:
        return instance.db[collection].find_one()
    return instance.db[collection].find_one(filter)