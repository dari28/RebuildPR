from django.conf.urls import url
from nlp import views
from lib.server_tuning import execution_at_startup

urlpatterns = [
    url(r'^test_work/?$', views.test_work),
    url(r'^test_exception_work/?$', views.test_exception_work),

    url(r'^get_location_by_level/?$', views.get_location_by_level),

    url(r'^tag_stat/?$', views.tag_stat),

    url(r'^update_category/?$', views.update_category),
    url(r'^show_category/?$', views.show_category),

    url(r'^update_language_list/?$', views.update_language_list),
    url(r'^show_language_list/?$', views.show_language_list),
    url(r'^get_language/?$', views.get_language),

    url(r'^get_article_language_list/?$', views.get_article_language_list),

    url(r'^show_article_list/?$', views.show_article_list),
    url(r'^show_country_list/?$', views.show_country_list),
    url(r'^show_state_list/?$', views.show_state_list),
    url(r'^show_pr_city_list/?$', views.show_pr_city_list),
    url(r'^show_trained_article_list/?$', views.show_trained_article_list),

    url(r'^get_source_list/?$', views.get_source_list),


    url(r'^get_article_list/?$', views.get_article_list),
    url(r'^get_article_list_by_tag/?$', views.get_article_list_by_tag),
    url(r'^get_article_by_id/?$', views.get_article_by_id),
    url(r'^remove_dubles_articles/?$', views.remove_dubles_articles),


    url(r'^get_tag_list/?$', views.get_tag_list),

    url(r'^get_phrase_list/?$', views.get_phrase_list),
    url(r'^update_phrase_list/?$', views.update_phrase_list),
    url(r'^add_phrase_list/?$', views.add_phrase_list),
    url(r'^delete_phrase_list/?$', views.delete_phrase_list),
    url(r'^delete_permanent_phrase_list/?$', views.delete_permanent_phrase_list),

    url(r'^get_tags_from_article/?$', views.get_tags_from_article),
    url(r'^get_tags_from_all_articles/?$', views.get_tags_from_all_articles),

    url(r'^get_default_entity/?$', views.get_default_entity),

    url(r'^get_geoposition/?$', views.get_geoposition),
    url(r'^find_articles_by_locations/?$', views.find_articles_by_locations),

    url(r'^predict_entity/?$', views.predict_entity),

    # Fill up db
    url(r'^fill_up_db_from_zero/?$', views.fill_up_db_from_zero),
    url(r'^update_source_list_from_server/?$', views.update_source_list_from_server),
    url(r'^download_articles_by_phrases/?$', views.download_articles_by_phrases),
    url(r'^load_iso/?$', views.load_iso),
    url(r'^update_country_list/?$', views.update_country_list),
    url(r'^update_state_list/?$', views.update_state_list),
    url(r'^update_pr_city_list/?$', views.update_pr_city_list),
    url(r'^fill_up_geolocation/?$', views.fill_up_geolocation),
    url(r'^train_on_default_list/?$', views.train_on_default_list),
    url(r'^get_tags_from_untrained_articles/?$', views.get_tags_from_untrained_articles),
]

execution_at_startup()
