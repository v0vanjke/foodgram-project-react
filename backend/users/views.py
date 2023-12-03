from django.shortcuts import get_object_or_404
# from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.paginations import CustomPagination
from users.models import Follow, User
from users.serializers import (
    FollowSerializer, UserSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет с обработкой url содержащих me, subscribe, subscriptions."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        methods=['GET'],
        url_path='me',
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('GET',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def read_subscribe(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            page, many=True, context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Вы не можете подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Вы уже подписаны на данного пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            subscription = Follow.objects.create(
                user=user, author=author)
            serializer = FollowSerializer(
                subscription,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            author = self.get_object()
            if Follow.objects.filter(user=user, author=author).exists():
                Follow.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
