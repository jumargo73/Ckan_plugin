from sqlalchemy import Column, types
from ckan.model.package import package_table
from ckan.model import Package

def extend_package_table():

    if 'city' not in package_table.c:
        package_table.append_column(
            Column('city', types.UnicodeText)
        )
        Package.city = package_table.c.city

    if 'department' not in package_table.c:
        package_table.append_column(
            Column('department', types.UnicodeText)
        )
        Package.department = package_table.c.department

    if 'update_frequency' not in package_table.c:
        package_table.append_column(
            Column('update_frequency', types.UnicodeText)
        )
        Package.update_frequency = package_table.c.update_frequency