from django.db import models
from django.contrib.auth.models import User

class PredictionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to logged-in user

    patient_name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, blank=True)

    pregnancies = models.FloatField()
    glucose = models.FloatField()
    bloodpressure = models.FloatField()
    skinthickness = models.FloatField()
    insulin = models.FloatField()
    bmi = models.FloatField()
    dpf = models.FloatField()
    age = models.FloatField()

    result = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    FEEDBACK_CHOICES = [
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('pending', 'Pending'),
    ]
    feedback = models.CharField(
        max_length=10,
        choices=FEEDBACK_CHOICES,
        default='pending',
    )

    def __str__(self):
        return f"{self.patient_name} ({self.result}) at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
