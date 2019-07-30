from django.conf.urls import url
from nlp import views
from lib.server_tuning import execution_at_startup

urlpatterns = [
    # ************* Test functions *************
    url(r'^test_work/?$', views.test_work),
    url(r'^test_exception_work/?$', views.test_exception_work),
    # **************** Sources *****************
    url(r'^get_source_list/?$', views.get_source_list),
    url(r'^show_source_list/?$', views.show_source_list),
    # **************** Articles ****************
    url(r'^get_article_list/?$', views.get_article_list),
    url(r'^get_article_by_id/?$', views.get_article_by_id),
    url(r'^get_article_list_by_tag/?$', views.get_article_list_by_tag),
    url(r'^show_article_list/?$', views.show_article_list),
    url(r'^show_tagged_article_list/?$', views.show_tagged_article_list),
    # ****************** Tags ******************
    url(r'^get_tag_list/?$', views.get_tag_list),
    url(r'^tag_stat/?$', views.tag_stat),
    # ***************** Phrases ****************
    url(r'^get_phrase_list/?$', views.get_phrase_list),
    url(r'^add_phrase_list/?$', views.add_phrase_list),
    url(r'^delete_phrase_list/?$', views.delete_phrase_list),
    url(r'^update_phrase_list/?$', views.update_phrase_list),
    url(r'^delete_permanent_phrase_list/?$', views.delete_permanent_phrase_list),  # DEVELOPER
    # ******************* Entity ***************
    url(r'^parse_currency/?$', views.parse_currency),
    # ******************** Other ***************
    url(r'^get_geoposition/?$', views.get_geoposition),
    url(r'^show_language_list/?$', views.show_language_list),
    # ****************** Location **************
    url(r'^get_locations_by_level/?$', views.get_locations_by_level),
    url(r'^aggregate_articles_by_locations/?$', views.aggregate_articles_by_locations),
    url(r'^get_location_info_by_id/?$', views.get_location_info_by_id),

    # ********************************************
    # *********  DEVELOPER FUNCTIONS   ***********
    # ********************************************
    # ****************** Fixes *******************
    url(r'^fix_sources_and_add_official_field/?$', views.fix_sources_and_add_official_field),
    url(r'^fix_article_source_with_null_id/?$', views.fix_article_source_with_null_id),
    url(r'^fix_article_content/?$', views.fix_article_content),
    url(r'^fix_one_article_by_id/?$', views.fix_one_article_by_id),
    url(r'^fix_original_fields/?$', views.fix_original_fields),
    url(r'^fix_entity_location/?$', views.fix_entity_location),
    url(r'^dev_find_article_ids_with_tag_length_more_than_length/?$', views.dev_find_article_ids_with_tag_length_more_than_length),
    url(r'^remove_dubles_articles_and_entities/?$', views.remove_dubles_articles_and_entities),
    url(r'^fix_article_content_and_retrain_entity_bt_article_ids/?$', views.fix_article_content_and_retrain_entity_bt_article_ids),
url(r'^delete_trash_from_article_content/?$', views.delete_trash_from_article_content),

    url(r'^get_tags_from_all_articles/?$', views.get_tags_from_all_articles),
    # ***************** Fill up db from zero ***************
    url(r'^fill_up_db_from_zero/?$', views.fill_up_db_from_zero),
    url(r'^update_source_list_from_server/?$', views.update_source_list_from_server),
    url(r'^download_articles_by_phrases/?$', views.download_articles_by_phrases),
    url(r'^load_iso/?$', views.load_iso),
    url(r'^update_country_list/?$', views.update_country_list),
    url(r'^update_state_list/?$', views.update_state_list),
    url(r'^update_pr_city_list/?$', views.update_pr_city_list),
    url(r'^train_on_default_list/?$', views.train_on_default_list),
    url(r'^get_tags_from_untrained_articles/?$', views.get_tags_from_untrained_articles),
    url(r'^add_locations_to_untrained_articles/?$', views.add_locations_to_untrained_articles),
    url(r'^fill_up_geolocation/?$', views.fill_up_geolocation),

    url(r'^add_bad_source/?$', views.add_bad_source),
    url(r'^remove_bad_source/?$', views.remove_bad_source),
    url(r'^remove_all_bad_source/?$', views.remove_all_bad_source),


    url(r'^update_category/?$', views.update_category),
    # url(r'^show_category/?$', views.show_category),  # DONT WORK

    url(r'^update_language_list/?$', views.update_language_list),
    url(r'^get_default_entity/?$', views.get_default_entity),
    url(r'^tag_stat_by_articles_list/?$', views.tag_stat_by_articles_list),  # NEED FOR
    url(r'^predict_entity/?$', views.predict_entity),
    url(r'^get_tags_from_article/?$', views.get_tags_from_article),

    # url(r'^dev_update_sources_by_articles_url/?$', views.dev_update_sources_by_articles_url),
    url(r'^dev_update_sources_by_one_article/?$', views.dev_update_sources_by_one_article),
]

execution_at_startup()
