from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
    name = models.CharField(max_length=200,null=True)
    email = models.EmailField(max_length=200,null=True,unique=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, default="avatar.svg", upload_to='avatars/')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # def __str__(self):
    #     return self.username

#Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) #update every time
    created = models.DateTimeField(auto_now_add=True) #only save once

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) #update every time
    created = models.DateTimeField(auto_now_add=True) #only save once
    def __str__(self):
        return self.body[0:69]