# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

from config.settings import BASE_DIR

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
