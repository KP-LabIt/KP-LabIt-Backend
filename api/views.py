from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Test
from .serializer import TestSerializer


@api_view(["GET"])
def get_data(request):
    data = Test.objects.all()
    serialized_data = TestSerializer(data, many=True).data
    return Response(serialized_data)

@api_view(["POST"])
def post_test(request):
    data = request.data
    serializer = TestSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_init(request):
    return Response("Endpoint pre api...")
