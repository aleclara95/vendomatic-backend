from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.http import Http404

from core.error_messages import API_ERROR_MESSAGES
from core.models import CoinsAmount, MachineItem, MAX_MACHINE_ITEMS
from core.serializers import CoinsAmountSerializer, MachineItemSerializer


class CoinView(APIView):
    def get_object(self):
        try:
            return CoinsAmount.objects.get(pk=settings.DEFAULT_COIN_AMOUNT)
        except CoinsAmount.DoesNotExist:
            raise Http404

    def get(self, request):
        coins_amount = self.get_object()

        headers = {
            'Access-Control-Expose-Headers': "X-Coins",
            'X-Coins': coins_amount.count
        }

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

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
            'Access-Control-Expose-Headers': "X-Coins",
            'X-Coins': new_count
        }

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def delete(self, request, pk=None, format=None):
        coins_amount = self.get_object()
        returned_count = coins_amount.count
        coins_amount.reset_count()

        headers = {
            'Access-Control-Expose-Headers': "X-Coins",
            'X-Coins': returned_count
        }

        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        exception_handler = self.get_exception_handler()

        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)

        if response is None:
            self.raise_uncaught_exception(exc)

        response.exception = True

        response.headers['Access-Control-Expose-Headers'] = "X-Coins"
        response.headers['X-Coins'] = 0

        return response


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
            pk=settings.DEFAULT_COIN_AMOUNT)

        if machine_item.count == 0:
            headers = {
                'Access-Control-Expose-Headers': "X-Coins",
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
                'Access-Control-Expose-Headers': "X-Inventory-Remaining, X-Coins",
                'X-Inventory-Remaining': new_stock,
                'X-Coins': new_count
            }

            body = {
                'quantity': 1
            }

            response_status = status.HTTP_200_OK
        else:
            headers = {
                'Access-Control-Expose-Headers': "X-Coins",
                'X-Coins': coins_amount.count
            }

            coins_amount.reset_count()

            body = None

            response_status = status.HTTP_400_BAD_REQUEST

        return Response(body, status=response_status, headers=headers)

    @action(detail=False, methods=['post'])
    def refill(self, request, *args, **kwargs):
        self.get_queryset().update(count=MAX_MACHINE_ITEMS)

        serializer = MachineItemSerializer(
            self.get_queryset().all(), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
