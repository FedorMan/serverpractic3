import shutil

from pyunpack import Archive
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from rest_framework.parsers import (
    FileUploadParser
)
from rest_framework.views import APIView

from rest_framework.response import Response

from untitled.classify_image2 import classificate_all, getResultData, saveProfAnswer


class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        path = default_storage.save('E:\\untitled\\1.rar', ContentFile(file_obj.read()))
        os.mkdir("E:\\untitled\\img")
        Archive('E:\\untitled\\1.rar').extractall('E:\\untitled\\img')
        os.remove("E:\\untitled\\1.rar")
        classificate_all('E:\\untitled\\img')
        shutil.rmtree("E:\\untitled\\img")
        return Response(status=200, data=getResultData())


class PostData(APIView):
    def post(self, request, pk=None):
        print("asfadfds")
        return Response(status=200, data=saveProfAnswer(request.data))

