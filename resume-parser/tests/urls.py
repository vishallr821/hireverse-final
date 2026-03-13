from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('generate/<int:candidate_id>/<int:job_id>/',
         views.generate_test, name='generate_test'),
    path('take/<uuid:token>/',
         views.take_test, name='take_test'),
    path('submit/<uuid:token>/',
         views.submit_test, name='submit_test'),
    path('send/<int:candidate_id>/<int:job_id>/<int:ranking_id>/',
         views.send_test_link, name='send_test_link'),
    path('result/<uuid:token>/',
         views.test_result, name='test_result'),
    path('proctor/<uuid:token>/',
         views.check_proctoring, name='check_proctoring'),
    
    # DSA Round Integration
    path('send-dsa/<int:test_id>/',
         views.send_to_dsa_round, name='send_to_dsa_round'),
    path('dsa/take/<uuid:token>/',
         views.dsa_take, name='dsa_take'),
    path('dsa/proctor/<uuid:token>/',
         views.check_dsa_proctoring, name='check_dsa_proctoring'),
    path('final-results/<int:test_id>/',
         views.final_results, name='final_results'),
    path('all-final-results/',
         views.all_final_results, name='all_final_results'),
    path('tab-switch/<uuid:token>/',
         views.report_tab_switch, name='report_tab_switch'),
    path('dsa/tab-switch/<uuid:token>/',
         views.report_dsa_tab_switch, name='report_dsa_tab_switch'),
]
