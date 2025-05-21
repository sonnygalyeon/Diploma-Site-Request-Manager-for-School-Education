from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    teachers = models.ManyToManyField('auth.User', related_name='courses')

    def __str__(self):
        return self.title