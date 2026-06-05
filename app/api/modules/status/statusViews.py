from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

import logging
import django
import sys

status_logger = logging.getLogger('api.status')

def getAppVersion():
    from web.context_processors import versionnumber_processor
    context = versionnumber_processor(None)
    return context['versionnumber'] 

def getAppBuild():
    from web.context_processors import versionnumber_processor
    context = versionnumber_processor(None)
    return context['buildNumber'] 

def getDBType():
    from django.conf import settings
    db_engine = settings.DATABASES['default']['ENGINE']
    # Bestimmen des exakten Namens
    if 'mysql' in db_engine:
        if 'mariadb' in db_engine:
            database_name = "MariaDB"
        else:
            database_name = "MySQL"
    elif 'postgresql' in db_engine:
        database_name = "PostgreSQL"
    else:
        database_name = db_engine.split('.')[-1]  # Gibt den genauen Engine-Namen zurück
    return database_name

def getDBName():
    from django.db import connection
    db_name = connection.settings_dict['NAME']
    return str(db_name)

def getDBVersion():
    from django.db import connection
    db_engine = connection.settings_dict['ENGINE']
    with connection.cursor() as cursor:
        if 'sqlite' in db_engine:
            cursor.execute('select sqlite_version()')
        else:
            cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        return db_version[0]

def getDjangoVerison():
    djangoVersion = django.get_version()
    return djangoVersion

def getInstallType():
    # Prüfe Umgebungsvariable
    import os
    if os.environ.get('container', '') == 'docker':
        return "Docker"
    # Prüfe typische Dateien
    try:
        with open('/proc/1/cgroup', 'rt') as file:
            content = file.read()
            if 'docker' in content or 'containerd' in content:
                return "Docker"
    except Exception:
        pass
    try:
        with open('/proc/self/mountinfo', 'rt') as file:
            if 'docker' in file.read():
                return "Docker"
    except Exception:
        pass
    return "Bare - Standalone"

def getPythonVersion():
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return version

# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
def showStatus(request):
    try:
        # Alle Informationen sammeln
        data = {
            'App Version': getAppVersion(),
            'App Build': getAppBuild(),
            'Python Version': getPythonVersion(),
            'Django Version': getDjangoVerison(),
            'Datenbank Typ': getDBType(),
            'Datenbank Version': getDBVersion(),
            'Datenbank Name': getDBName(),
            'Installationstyp': getInstallType(),
        }
        # Rückgabe des JSON-Feedbacks
        status_logger.info("showStatus successful")
        return Response(data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Fehlerbehandlung
        status_logger.exception("showStatus failed")
        error_message = {'error': 'Interner Serverfehler.'}
        return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)