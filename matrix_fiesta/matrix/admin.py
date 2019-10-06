from django.contrib import admin

from common.admin import SlugNameAdmin
from matrix import models

class StudentEvaluationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(StudentEvaluationAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'achievement', 'student',
            'evaluation_value',
            'achievement__course', 'achievement__course__ecue',
            'achievement__course__ecue__ue', 'achievement__course__ecue__ue__semestre'
        )


class CourseAdmin(SlugNameAdmin):
    def get_queryset(self, request):
        queryset = super(CourseAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'ecue',
            'ecue__ue', 'ecue__ue__semestre',
        )


class SmallClassAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(SmallClassAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'course', 'course__ecue',
            'course__ecue__ue', 'course__ecue__ue__semestre',
            'teacher', 'students'
        )


class LearningAchievementAdmin(SlugNameAdmin):
    def get_queryset(self, request):
        queryset = super(LearningAchievementAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'course', 'course__ecue',
            'course__ecue__ue', 'course__ecue__ue__semestre'
        )


class ECUEAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(ECUEAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'ue', 'ue__semestre'
        )


class UEAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(UEAdmin, self).get_queryset(request)
        return queryset.prefetch_related(
            'semestre'
        )


admin.site.register(models.ProfileUser)
admin.site.register(models.SchoolYear)
admin.site.register(models.PromotionYear)
admin.site.register(models.Semestre)
admin.site.register(models.UE, UEAdmin)
admin.site.register(models.ECUE, ECUEAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.EvaluationValue)
admin.site.register(models.LearningAchievement, LearningAchievementAdmin)
admin.site.register(models.StudentEvaluation, StudentEvaluationAdmin)
admin.site.register(models.SmallClass, SmallClassAdmin)
