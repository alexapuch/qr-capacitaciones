from django.contrib import admin
from .models import Participant, Enrollment, Question, Option, Assessment, Answer, AssistanceEvent, AuditLog

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("curp","name","role")
    search_fields = ("curp","name","role")

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id","participant","course","site","registered_at")
    list_filter = ("course","site")
    search_fields = ("participant__curp","participant__name")

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id","course","qtype","text")
    list_filter = ("course","qtype")
    inlines = [OptionInline]

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("id","enrollment","qtype","score","submitted_at")
    list_filter = ("qtype","enrollment__course","enrollment__site")
    search_fields = ("enrollment__participant__curp","enrollment__participant__name")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id","assessment","question","option","is_correct")

@admin.register(AssistanceEvent)
class AssistanceEventAdmin(admin.ModelAdmin):
    list_display = ("enrollment","confirmed_at")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at","action")
