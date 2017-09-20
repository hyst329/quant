import django_tables2 as tables

class PageTable(tables.Table):
    key = tables.Column()
    value = tables.Column()