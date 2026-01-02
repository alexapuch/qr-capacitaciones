from django.db import models
from core.models import Course, Site

class Participant(models.Model):
    curp = models.CharField(max_length=18, unique=True)
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.curp} - {self.name}"

class Enrollment(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["participant", "course"], name="uniq_participant_course")
        ]

    def __str__(self):
        return f"{self.participant.curp} -> {self.course.name}"

class Question(models.Model):
    PRE = "PRE"
    POST = "POST"
    TYPE_CHOICES = [(PRE,"PRE"), (POST,"POST")]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qtype = models.CharField(max_length=4, choices=TYPE_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.course.name} {self.qtype}: {self.text[:40]}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Opt {self.id} Q{self.question_id}"

class Assessment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    qtype = models.CharField(max_length=4, choices=Question.TYPE_CHOICES)
    score = models.IntegerField()
    correct_count = models.IntegerField()
    total = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment.participant.curp} {self.qtype} {self.score}"

class Answer(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
    is_correct = models.BooleanField()

class AssistanceEvent(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    confirmed_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=200)
    meta = models.JSONField(default=dict, blank=True)
