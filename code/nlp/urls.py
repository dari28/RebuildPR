from django.conf.urls import url
from nlp import views
from lib.server_tuning import execution_at_startup

urlpatterns = [
    url(r'^test_work/?$', views.test_work)
]

execution_at_startup()