API_KEY = 'aa5ed9dc9edb4b49b3fe02edc73eca22'#'886e070469344e0381be2fc5cdf24830'
HISTORY_SOURCES_DIR = "../data/history_sources.txt"
HISTORY_NEWS_DIR = "../data/history_news.txt"
DAYS_TO_UPDATE_SOURCES = 30
DAYS_TO_UPDATE_NEWS = 1

TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'
EVERYTHING_URL = 'https://newsapi.org/v2/everything'
SOURCES_URL = 'https://newsapi.org/v2/sources'

countries = {'ae','ar','at','au','be','bg','br','ca','ch','cn','co','cu','cz','de','eg','fr','gb','gr','hk',
             'hu','id','ie','il','in','it','jp','kr','lt','lv','ma','mx','my','ng','nl','no','nz','ph','pl',
             'pt','ro','rs','ru','sa','se','sg','si','sk','th','tr','tw','ua','us','ve','za'}

languages = {'ar','en','cn','de','es','fr','he','it','nl','no','pt','ru','sv','ud'}

categories = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}

sort_method = {'relevancy','popularity','publishedAt'}