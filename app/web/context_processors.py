from django.db import connection

def versionnumber_processor(request):
    buildYear = 2026
    versionNumber = "0.1.0"
    buildNumber = "0000004"
    return {'versionnumber': versionNumber,'buildNumber': buildNumber, 'buildYear':buildYear,}
def datenbank_processor(request):
    db_name = connection.settings_dict['NAME']
    return {'db_name': db_name,}
def softwarename_processor(request):
    softwarename = "Hello World PWA"
    softwarenameshort = "HWP"
    return {'softwarename': softwarename,'softwarenameshort': softwarenameshort,}