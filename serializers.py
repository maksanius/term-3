def serialize_rights(model):
    return{
        'id': model.id,
        'name': model.name
    }

def serialize_objects(model):
    return{
        'id': model.id,
        'type': model.type,
        'address': model.address
    }

def serialize_cars(model):
    return{
        'id': model.id,
        'model': model.model,
        'plate_number': model.plate_number,
        'status': model.status,
        'objects': model.fk_objects_id,
        'rights': model.fk_rights_id.name
    }

def serialize_drivers(model):
    return{
        'id': model.id,
        'name': model.name,
        'rights': model.fk_rights_id.name,
        'cars': model.fk_cars_id
    }

def serialize_cargo(model):
    return{
        'id': model.id,
        'description': model.description
    }

def serialize_organizations(model):
    return{
        'id': model.id,
        'name': model.name
    }

def serialize_customers(model):
    return{
        'id': model.id,
        'name': model.name,
        'phone': model.phone,
        'organizations': model.fk_organizations_id
    }

def serialize_orders(model):
    return{
        'id': model.id,
        'description': model.description,
        'date_start': model.date_start,
        'date_end': model.date_end,
        'status': model.status,
        'price': model.price,
        'customers': model.fk_customers_id
    }

def serialize_operations(model):
    return{
        'id': model.id,
        'date': model.date,
        'address_start': model.address_start,
        'address_end': model.address_end,
        'cars': model.fk_cars_id,
        'cargo': model.fk_cargo_id,
        'drivers': model.fk_drivers_id,
        'orders': model.fk_orders_id
    }