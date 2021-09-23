from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.urls import reverse

from core.models import CoinsAmount, Item, MachineItem, MAX_MACHINE_ITEMS


class InventoryTests(APITestCase):
    def test_list_inventory(self):
        """
        Ensure we can list all inventory items.
        """
        url = reverse('core:inventory-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_buy_item_ok(self):
        """
        Ensure we can buy an item.
        """
        CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=3)

        item = Item.objects.create(
            name='Coke', volume=0.25, price=0.5)

        machine_item = MachineItem.objects.create(item=item, count=5)

        url = reverse('core:inventory-detail', kwargs={'pk': machine_item.id})
        response = self.client.put(url, {}, format='json')

        new_machine_item = MachineItem.objects.get(id=machine_item.id)

        self.assertEqual(int(response.headers['X-Coins']), 1)
        self.assertEqual(int(response.headers['X-Inventory-Remaining']), 4)
        self.assertEqual(new_machine_item.count, 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_buy_item_not_enough_cash(self):
        """
        Ensure items can't be bought when there is not enough cash.
        """
        CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=1)

        item = Item.objects.create(
            name='Coke', volume=0.25, price=0.5)

        machine_item = MachineItem.objects.create(item=item, count=5)

        url = reverse('core:inventory-detail', kwargs={'pk': machine_item.id})
        response = self.client.put(url, {}, format='json')

        new_machine_item = MachineItem.objects.get(id=machine_item.id)

        self.assertEqual(int(response.headers['X-Coins']), 1)
        self.assertEqual(new_machine_item.count, 5)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_item_no_stock(self):
        """
        Ensure items can't be bought when there is not enough stock.
        """
        CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=3)

        item = Item.objects.create(
            name='Coke', volume=0.25, price=0.5)

        machine_item = MachineItem.objects.create(item=item, count=0)

        url = reverse('core:inventory-detail', kwargs={'pk': machine_item.id})
        response = self.client.put(url, {}, format='json')

        new_machine_item = MachineItem.objects.get(id=machine_item.id)

        self.assertEqual(int(response.headers['X-Coins']), 3)
        self.assertEqual(new_machine_item.count, 0)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_refill(self):
        """
        Ensure machines are refilled.
        """
        item1 = Item.objects.create(
            name='Coke', volume=0.25, price=0.5)
        item2 = Item.objects.create(
            name='Sprite', volume=0.25, price=0.5)
        item3 = Item.objects.create(
            name='Fanta', volume=0.25, price=0.5)

        machine_item1 = MachineItem.objects.create(item=item1, count=0)
        machine_item2 = MachineItem.objects.create(item=item2, count=2)
        machine_item3 = MachineItem.objects.create(item=item3, count=3)

        url = reverse('core:inventory-refill')
        response = self.client.post(url, {}, format='json')

        new_machine_item1 = MachineItem.objects.get(id=machine_item1.id)
        new_machine_item2 = MachineItem.objects.get(id=machine_item2.id)
        new_machine_item3 = MachineItem.objects.get(id=machine_item3.id)

        self.assertEqual(new_machine_item1.count, MAX_MACHINE_ITEMS)
        self.assertEqual(new_machine_item2.count, MAX_MACHINE_ITEMS)
        self.assertEqual(new_machine_item3.count, MAX_MACHINE_ITEMS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CoinsTests(APITestCase):
    def test_get_coins_count(self):
        """
        Ensure we can get the current active coin count.
        """
        CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=1)

        url = reverse('core:coin')
        response = self.client.get(url, format='json')
        self.assertEqual(int(response.headers['X-Coins']), 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_coin(self):
        """
        Ensure we can add a coin in the machine.
        """
        coins_amount = CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=1)

        url = reverse('core:coin')
        response = self.client.put(url, {'coin': 1}, format='json')

        new_coins_amount = CoinsAmount.objects.get(id=coins_amount.id)

        self.assertEqual(int(response.headers['X-Coins']), 2)
        self.assertEqual(new_coins_amount.count, 2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_dispense_coins(self):
        """
        Ensure we can dispense the machine coins.
        """
        coins_amount = CoinsAmount.objects.create(
            id=settings.DEFAULT_COIN_AMOUNT, value='0.25', count=3)

        url = reverse('core:coin')
        response = self.client.delete(url, format='json')

        new_coins_amount = CoinsAmount.objects.get(id=coins_amount.id)

        self.assertEqual(int(response.headers['X-Coins']), 3)
        self.assertEqual(new_coins_amount.count, 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
