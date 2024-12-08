from psqlpy_piccolo import PSQLPyEngine

from piccolo.conf.apps import AppRegistry


DB = PSQLPyEngine(
    config={
        "host": "localhost",
        "database": "piccolo",
        "user": "root",
        "password": "",
        "port": 26257,
    }
)

APP_REGISTRY = AppRegistry(
    apps=[
        "home.piccolo_app",
        "piccolo_admin.piccolo_app",
    ]
)
