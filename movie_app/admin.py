from django.contrib import admin
from . import models
from .models import Director, Movie, Review

admin.site.register(Director)
admin.site.register(Movie)
admin.site.register(Review)
