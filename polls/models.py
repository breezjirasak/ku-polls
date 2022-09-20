import datetime
from re import S
from statistics import mode

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Question(models.Model):
    """ Question model"""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('ended date', null=True, blank=True)
    
    def __str__(self):
        """ 
        display question text.
        """
        return self.question_text
    
    def was_published_recently(self):
        """
        To check that polls was published recently. 
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    def is_published(self):
        """ 
        Return true if you current time is on published date
        """
        now = timezone.localtime()
        return now >= self.pub_date
    
    def can_vote(self):
        """ 
        Return true if you current time is between publish date and ended date.
        """
        now = timezone.localtime()
        if self.end_date is None:
            return now >= self.pub_date
        return self.end_date >= now >= self.pub_date


class Choice(models.Model):
    """ Choice model"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)
    
    @property
    def votes(self):
        return Vote.objects.filter(choice=self).count()
    
    def __str__(self):
        """ 
        display choices.
        """
        return self.choice_text
    
class Vote(models.Model):
    """ Vote model"""
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
