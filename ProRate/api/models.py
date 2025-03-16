from django.db import models
from django.contrib.auth.models import User


#Creating professor database model
class Professor(models.Model):
    identifier = models.CharField(max_length = 10, unique = True) #professor ID
    name = models.CharField(max_length=100)

class Module(models.Model):
    code = models.CharField(max_length=10, unique=True) #Module ID
    name = models.CharField(max_length=100)
    semester = models.IntegerField()
    year = models.IntegerField()

    #Allows multiple professors to be associated with multiple Modules and vise versa (Many To Many)
    professors = models.ManyToManyField(Professor, related_name="modules")

class Rating(models.Model):
    #every Rating will have a 1 User it is associated to, but User's can have multiple ratings
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="ratings")
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ("user", "professor", "module")
