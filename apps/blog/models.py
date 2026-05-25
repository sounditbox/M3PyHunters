from django.db import models


# (Почти) Любое изменение требует создания миграции

class MyModel(models.Model):  # Таблица blog_mymodel в БД
    # атрибут класса - столбец в таблице БД
    # id - создаётся автоматически
    counter = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100)
