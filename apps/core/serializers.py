from rest_framework import serializers

from core.models import CoinsAmount, Item, MachineItem


class CoinsAmountSerializer(serializers.Serializer):
    coin = serializers.IntegerField(required=True)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'verbose_name', 'volume', 'price']


class MachineItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = MachineItem
        fields = ['id', 'item', 'count']
