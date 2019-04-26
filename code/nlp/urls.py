from django.conf.urls import url
from nlp import views
from lib.server_tuning import execution_at_startup

urlpatterns = [
    url(r'^test_work/?$', views.test_work),

    url(r'^get_country_list/?$', views.get_country_list),
    url(r'^get_language_list/?$', views.get_language_list),

    url(r'^get_source_list/?$', views.get_source_list),
    url(r'^update_source_list_from_server/?$', views.update_source_list_from_server),

    url(r'^get_article_list/?$', views.get_article_list),
    url(r'^update_article_list_from_server/?$', views.update_article_list_from_server),

    url(r'^get_tag_list/?$', views.get_tag_list),

    url(r'^get_phrase_list/?$', views.get_phrase_list),
    url(r'^update_phrase_list/?$', views.update_phrase_list),
    url(r'^add_phrase_list/?$', views.add_phrase_list),
    url(r'^delete_phrase_list/?$', views.delete_phrase_list),
    url(r'^delete_permanent_phrase_list/?$', views.delete_permanent_phrase_list),
]

execution_at_startup()