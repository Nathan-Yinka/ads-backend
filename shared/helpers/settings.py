from administration.models import Settings

def get_settings():
    try:
        return Settings.objects.first()
    except Settings.DoesNotExist:
        return None