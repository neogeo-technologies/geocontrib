import requests

from rest_framework.views import APIView
from rest_framework.response import Response


class GetFeatureInfo(APIView):

    http_method_names = ['get', ]

    def get(self, request):
        payload = {}

        url = request.GET.get('url', '')
        params = [
            'request',
            'service',
            'srs',
            'version',
            'bbox',
            'height',
            'width',
            'layers',
            'query_layers',
            'info_format',
        ]
        for param in params:
            payload[param] = request.GET.get(param, '')

        coords = [
            'x',
            'y',
            'i',
            'j'
        ]
        for coord in coords:
            val = request.GET.get(coord)
            if val:
                payload[coord] = val
        try:
            response = requests.get(url, params=payload, timeout=60)
            data = response.json()
            code = response.status_code
            if code != 200 or not data.get('type', '') == 'FeatureCollection':
                data = "Les données ne sont pas au format geoJSON"
        except Exception:
            data = "Les données sont inaccessibles"
        finally:
            return Response(data=data, status=code)
