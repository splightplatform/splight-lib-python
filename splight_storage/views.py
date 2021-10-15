from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from models.asset import Asset
from serializers import *
import serializers


class AssetView(APIView):

    """/assets/{asset_id}"""

    def get(self, request, asset_id):
        pass
