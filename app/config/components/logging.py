import logging.config

LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },

    'formatters': {
        'short': {
            'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
        'default': {
            'format': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        },
    },
    'handlers': {
    #     "fileHandler": {
    #         "class": "logging.FileHandler",
    #         "formatter": "short",
    #         "filename": "admin_panel.log"
    #     },
        'debug-console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['require_debug_true'],
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['debug-console'],
            'propagate': False,
        },
        # 'file_logger': {
        #     'handlers': ['fileHandler'],
        #     'level': 'DEBUG',
        #     'propagate': True
        # },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['debug-console'],
            'propagate': False,
        }
    }
}

logging.config.dictConfig(LOGGING_CONF)
