from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Default Route
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def getRoutes(request):
    fullUrl = request.build_absolute_uri()

    # Alle Routen
    baseRoutes = {
        'Erhalte alle Routen': fullUrl,
    }

    # Status Routen
    statusRoutes = {
        'Erhalte den Status': fullUrl + "showStatus/",
    }

    sumRoutes = {
            **baseRoutes, 
            **statusRoutes,
        }

    return Response(sumRoutes)