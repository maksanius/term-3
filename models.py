import peewee as pw

db = pw.PostgresqlDatabase(    
    "term",
    user="postgres",
    password="785412",
    host="localhost")

class BaseModel(pw.Model):
    class Meta:
        database = db

class Objects(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    type = pw.TextField(null=True)
    address = pw.TextField(null=True)

    class Meta:
        table_name = 'objects'

class Rights(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    name = pw.CharField(max_length=30, null = False)

    class Meta:
        table_name = 'rights'

class Cars(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    model = pw.TextField(null=False)
    plate_number = pw.CharField(max_length=15, null=False)
    status = pw.CharField(max_length=40, null=False)
    fk_objects_id = pw.ForeignKeyField(Objects, null=True, on_delete='SET NULL', backref='objects')
    fk_rights_id = pw.ForeignKeyField(Rights, null=False, on_delete='RESTRICT', backref='rights')

    class Meta:
        table_name = 'cars'

class Drivers(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    name = pw.TextField(null=False)
    fk_rights_id = pw.ForeignKeyField(Rights, null=False, on_delete='RESTRICT', backref='rights')
    fk_cars_id = pw.ForeignKeyField(Cars, null=True, unique=True, on_delete='SET NULL', backref='cars')

    class Meta:
        table_name = 'drivers'

class Cargo(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    description = pw.TextField(null=False)

    class Meta:
        table_name = 'cargo'

class Organizations(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    name = pw.TextField(null=False)

    class Meta:
        table_name = 'organizations'

class Customers(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    name = pw.TextField(null=False)
    phone = pw.CharField(max_length=15, null=True)
    fk_organizations_id = pw.ForeignKeyField(Organizations, null=False, on_delete='CASCADE', backref='organizations')

    class Meta:
        table_name = 'customers'

class Orders(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    description = pw.TextField(null=False)
    date_start = pw.DateField(null=False)
    date_end = pw.DateField(null=True)
    status = pw.TextField(null=False)
    price = pw.IntegerField(null=False)
    fk_customers_id = pw.ForeignKeyField(Customers, null=False, on_delete='CASCADE', backref='customers')

    class Meta:
        table_name = 'orders'

class Operations(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    date = pw.DateField(null=False)
    address_start = pw.TextField(null=False)
    address_end = pw.TextField(null=False)
    fk_cars_id = pw.ForeignKeyField(Cars, null=False, on_delete='CASCADE', backref='cars')
    fk_cargo_id = pw.ForeignKeyField(Cargo, null=False, on_delete='CASCADE', backref='cargo')
    fk_drivers_id = pw.ForeignKeyField(Drivers, null=False, on_delete='CASCADE', backref='drivers')
    fk_orders_id = pw.ForeignKeyField(Orders, null=False, on_delete='CASCADE', backref='orders')

    class Meta:
        table_name = 'operations'



class Account(BaseModel):
    id = pw.BigAutoField(primary_key=True)
    name = pw.TextField(null=False)
    password = pw.TextField(null=False)

    class Meta:
        table_name = 'account'