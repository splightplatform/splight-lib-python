import os, ast

# Pusher
PUSHER_CONFIG = {
    'app_id' : os.getenv('PUSHER_APP_ID', "APP_ID"),
    'key' : os.getenv('PUSHER_KEY', "PUSHER_KEY"),
    'secret' : os.getenv('PUSHER_SECRET', "PUSHER_SECRET"),
    'cluster' : os.getenv('PUSHER_CLUSTER', "PUSHER_CLUSTER"),
    'ssl' : ast.literal_eval(os.getenv("PUSHER_SSL", "False"))
}
