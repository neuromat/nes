SECRET_KEY = "your_secret_key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "lapisnes.local"]
CSRF_TRUSTED_ORIGINS = [
    "https://localhost:80",
    "https://0.0.0.0",
    "https://lapisnes.local",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "nes_db",
        "USER": "nes_user",
        "PASSWORD": "nes_password",
        "HOST": "nes_db",
        "PORT": "5432",  # default port
    }
}
LIMESURVEY = {
    "URL_API": "http://limesurvey:8080",
    "URL_WEB": "http://limesurvey:8080",
    "USER": "lime_admin",
    "PASSWORD": "lime_admin_password",
}
LOGO_INSTITUTION = "/workspaces/nes/patientregistrationsystem/qdc/logo-institution.png"
