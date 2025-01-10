import models
import peewee
import serializers
from operator import and_
from functools import reduce
from peewee import fn

def get_right_id(name):
    if (name != ''):
        id = str([serializers.serialize_rights(model) for model in models.Rights.select().where(models.Rights.name.contains(name))][0]['id'])
    else:
        id = ''
    
    return id

def search_objects_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.type.contains(patterns[1]),
        model.address.contains(patterns[2]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_rights_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.name.contains(patterns[1]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_cars_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    right_id = get_right_id(patterns[5])
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.model.contains(patterns[1]),
        model.plate_number.contains(patterns[2]),
        model.status.contains(patterns[3]),
        model.fk_objects_id.cast('TEXT').contains(patterns[4]),
        model.fk_rights_id.cast('TEXT').contains(right_id),
    ]
    
    query = model.select().where(reduce(and_, conditions))
    return query

def search_drivers_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    right_id = get_right_id(patterns[2])
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.name.contains(patterns[1]),
        model.fk_rights_id.cast('TEXT').contains(right_id),
        model.fk_cars_id.cast('TEXT').contains(patterns[3]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_cargo_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.description.contains(patterns[1]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_organizations_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.name.contains(patterns[1]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_customers_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.name.contains(patterns[1]),
        model.phone.contains(patterns[2]),
        model.fk_organizations_id.cast('TEXT').contains(patterns[3]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_orders_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.description.contains(patterns[1]),
        model.date_start.cast('TEXT').contains(patterns[2]),
        model.date_end.cast('TEXT').contains(patterns[3]),
        model.status.contains(patterns[4]),
        model.price.cast('TEXT').contains(patterns[5]),
        model.fk_customers_id.cast('TEXT').contains(patterns[6]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query

def search_operations_by_pattern(model, patterns):
    # Создаем список условий для каждого поля
    conditions = [
        model.id.cast('TEXT').contains(patterns[0]),
        model.date.cast('TEXT').contains(patterns[1]),
        model.address_start.contains(patterns[2]),
        model.address_end.contains(patterns[3]),
        model.fk_cars_id.cast('TEXT').contains(patterns[4]),
        model.fk_cargo_id.cast('TEXT').contains(patterns[5]),
        model.fk_drivers_id.cast('TEXT').contains(patterns[6]),
        model.fk_orders_id.cast('TEXT').contains(patterns[7]),
    ]
    
    # Объединяем условия с помощью or_
    query = model.select().where(reduce(and_, conditions))
    return query