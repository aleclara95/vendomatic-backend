from django.contrib import admin
from core.models import CoinsAmount, Item, MachineItem


class CoinsAmountAdmin(admin.ModelAdmin):
    pass


class ItemAdmin(admin.ModelAdmin):
    pass


class MachineItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(CoinsAmount, CoinsAmountAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MachineItem, MachineItemAdmin)
