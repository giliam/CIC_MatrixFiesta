from django.contrib import admin

from common.admin import SlugNameAdmin
from survey import models


class SlugNameAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class SurveyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(SurveyAdmin, self).get_queryset(request)
        return queryset


class QuestionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(QuestionAdmin, self).get_queryset(request)
        return queryset.prefetch_related('survey')


class ResponseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(ResponseAdmin, self).get_queryset(request)
        return queryset.prefetch_related('survey', 'user')


class AnswerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(AnswerAdmin, self).get_queryset(request)
        return queryset.prefetch_related('response', 'question')


admin.site.register(models.Survey, SurveyAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Response, ResponseAdmin)
admin.site.register(models.Answer, AnswerAdmin)
admin.site.register(models.QuestionChoice)
