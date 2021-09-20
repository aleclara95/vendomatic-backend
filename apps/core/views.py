from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.http import Http404

from core.error_messages import API_ERROR_MESSAGES
from core.models import CoinsAmount, MachineItem
from core.serializers import CoinsAmountSerializer, MachineItemSerializer


class CoinView(APIView):
    def get_object(self):
        try:
            return CoinsAmount.objects.get(pk=settings.DEFAULT_COIN_AMOUNT_ID)
        except CoinsAmount.DoesNotExist:
            raise Http404

    def put(self, request):
        coins_amount_data = request.data.get('coin')
        coins_amount_data = int(
            coins_amount_data) if coins_amount_data is not None else None

        data = {
            'coin': coins_amount_data
        }

        serializer = CoinsAmountSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        if coins_amount_data > settings.MAX_COINS_AMOUNT:
            raise ValidationError(API_ERROR_MESSAGES['invalid_coins_amount'])

        coins_amount = self.get_object()
        _, new_count = coins_amount.add_to_count(coins_amount_data)

        headers = {
            'X-Coins': new_count
        }

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def delete(self, request, pk=None, format=None):
        coins_amount = self.get_object()
        returned_count = coins_amount.count
        coins_amount.reset_count()

        headers = {
            'X-Coins': returned_count
        }

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def handle_exception(self, exc):
        self.headers['X-Coins'] = 0
        return Response({'detail': exc.detail}, status=exc.status_code, exception=True)


class InventoryViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = MachineItem.objects.all()
    serializer_class = MachineItemSerializer

    def get_object(self, pk=None):
        try:
            return MachineItem.objects.get(pk=pk)
        except MachineItem.DoesNotExist:
            raise Http404

    def update(self, request, pk=None, *args, **kwargs):
        machine_item = self.get_object(pk=pk)

        coins_amount = CoinsAmount.objects.get(
            pk=settings.DEFAULT_COIN_AMOUNT_ID)

        if machine_item.count == 0:
            headers = {
                'X-Coins': coins_amount.count
            }

            coins_amount.reset_count()

            return Response(status=status.HTTP_404_NOT_FOUND, headers=headers)

        if coins_amount.value * coins_amount.count >= machine_item.item.price:
            _, new_stock = machine_item.subtract_to_count(1)

            coins_used = machine_item.item.price // coins_amount.value
            _, new_count = coins_amount.subtract_to_count(coins_used)
            coins_amount.reset_count()

            headers = {
                'X-Inventory-Remaining': new_stock,
                'X-Coins': new_count
            }

            body = {
                'quantity': 1
            }

            response_status = status.HTTP_200_OK
        else:
            headers = {
                'X-Coins': coins_amount.count
            }

            coins_amount.reset_count()

            body = None

            response_status = status.HTTP_400_BAD_REQUEST

        return Response(body, status=response_status, headers=headers)
