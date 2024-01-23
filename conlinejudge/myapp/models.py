from django.db import models

# Create your models here.
class TestCaseResult(models.Model):
    num = models.IntegerField()
    passed = models.BooleanField()
    input_data = models.TextField()
    expected_output = models.TextField()
    actual_output = models.TextField()
    time_taken = models.FloatField()  # New field for elapsed time

    def __str__(self):
        return f"Test Case {self.id}: {'Passed' if self.passed else 'Failed'}"