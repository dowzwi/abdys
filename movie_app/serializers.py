from django.db.models import FloatField
from rest_framework import serializers
from .models import Movie, Director, Review
from rest_framework.exceptions import ValidationError

class MovieDetailSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField()

    class Meta:
        model = Movie
        fields = '__all__'

class DirectorSerializer(serializers.ModelSerializer):
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Director
        fields = ['id', 'name', 'movie_count']

    def get_movie_count(self, obj):
        return obj.movie_set.count()

class DirectorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['id', 'name']

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id' ,'movie', 'text', 'stars']

class ReviewsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id' ,'movie', 'text', 'stars']

class MovieSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField()
    reviews = ReviewsSerializer(source='review_set', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration', 'director', 'reviews', 'average_rating']

    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews.exists():
            return sum(review.stars for review in reviews) / reviews.count()
        return 0

class MovieValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=150, min_length=3)
    description = serializers.CharField(required=False)
    duration = serializers.IntegerField(max_value=100.00, min_value=1.00)
    director = serializers.CharField(required=True, max_length=150, min_length=2)

    def validate_title(self, title):
        if Movie.objects.filter(title__exact=title):
           raise ValidationError('Movie title already exists')
        return title

class MovieCreateSerializer(MovieValidateSerializer):
    def validate_title(self, title):
        if Movie.objects.filter(title__exact=title):
            raise ValidationError('Movie title already exists')
        return title


class MovieUpdateSerializer(MovieValidateSerializer):
    def validate_title(self, title):
        movie = self.context.get('movie')
        if Movie.objects.filter(title__exact=title).exclude(id=movie.id):
            raise ValidationError('Movie title already exists')
        return title

class DirectorValidateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=150, min_length=2)
    def validate_name(self, name):
        if Director.objects.filter(name__exact=name):
            raise ValidationError('Director name already exists')
        return name

class DirectorCreateSerializer(DirectorValidateSerializer):
    pass
class DirectorUpdateSerializer(DirectorValidateSerializer):
    def validate_name(self, name):
        director = self.context.get('director')
        if Director.objects.filter(name__exact=name).exclude(id=director.id):
            raise ValidationError('Director name already exists')
        return name

class ReviewValidateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=150, min_length=3)
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all() ,required=True)
    stars = serializers.IntegerField(max_value=5, min_value=0)
    def validate_movie(self, movie):
        movie = self.context.get('movie')
        if Movie.objects.filter(id__exact=movie.id).exclude(id=movie.id):
            raise ValidationError('Movie does not exist')
        return movie

class ReviewCreateSerializer(ReviewValidateSerializer):
    pass

class ReviewUpdateSerializer(ReviewValidateSerializer):
    def validate_movie(self, movie):
        movie = self.context.get('movie')
        if Movie.objects.filter(id__exact=movie.id).exclude(id=movie.id):
            raise ValidationError('Movie does not exist')
        return movie