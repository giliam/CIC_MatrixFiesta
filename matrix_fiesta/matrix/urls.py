from django.urls import path, re_path

from matrix import views

urlpatterns = [
    path('', views.homepage, name="matrix.homepage"),
    path('students/ues/', views.ues_list, name="ues.list"),
    path('students/', views.matrix_ues, name="ues.matrix"),
    path('teachers/', views.homepage_teachers, name="ues.homepage_teachers"),

    re_path(r'ues/matrix/(?P<slug>[-\w]+)', views.matrix_course, name="ues.matrix_course"),
    re_path(r'achievement/evaluate/(?P<slug>[-\w]+)', views.evaluate_achievement, name="ues.evaluate_achievement"),
    re_path(r'achievement/self/evaluate/', views.self_evaluate_all, name="ues.self_evaluate_all"),
    
    re_path(r'achievement/(?P<small_class_id>[0-9]+)/student/(?P<student_id>[0-9]+)/evaluate/(?P<slug>[-\w]+)', 
                            views.evaluate_achievement_student, name="ues.evaluate_achievement_student"),
    
    re_path(r'achievements/status/student/([0-9]+)/([0-9]+)', views.status_student, name="ues.status_student"),
    re_path(r'achievements/overall/student/([0-9]+)/([0-9]+)', views.evaluate_student_all, name="ues.evaluate_student_all"),

    path('log_in/', 
            views.log_in, 
            name='users.log_in'),
    path('log_out/',
            views.log_out,
            name='users.log_out'),
]


