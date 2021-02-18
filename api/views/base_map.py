import requests

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.decorators import api_view

# @api_view()
# def hello_world(request):
#   return Response({"message": "Hello, world!"})

class GetFeatureInfo(APIView):

  http_method_names = ['get', ]

  def get(self, request):
    payload = {}

    url = request.GET.get('url', '')

    payload['request'] = request.GET.get('request', '')
    payload['service'] = request.GET.get('service', '')
    payload['srs'] = request.GET.get('srs', '')
    payload['version'] = request.GET.get('version', '')
    payload['bbox'] = request.GET.get('bbox', '')
    payload['height'] = request.GET.get('height', '')
    payload['width'] = request.GET.get('width', '')
    payload['layers'] = request.GET.get('layers', '')
    payload['query_layers'] = request.GET.get('query_layers', '')
    payload['info_format'] = request.GET.get('info_format', '')
    if request.GET.get('x') is not None:
      payload['x'] = request.GET.get('x', '')
    if request.GET.get('y') is not None:
      payload['y'] = request.GET.get('y', '')
    if request.GET.get('i') is not None:
      payload['i'] = request.GET.get('i', '')
    if request.GET.get('j') is not None:
      payload['j'] = request.GET.get('j', '')

    r = requests.get(url, params=payload, timeout=60)

    try:
      response = r.json()

      if r.status_code == 200 and r.json()['type'] == 'FeatureCollection':
        return Response(data=r.json(), status=r.status_code)
      else:
        return Response(data="Les données ne sont pas au format geoJSON", status=r.status_code)

    except:
      return Response(data="Les données sont inaccessibles", status=r.status_code)