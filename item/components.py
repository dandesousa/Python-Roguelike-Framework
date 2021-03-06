from peewee import SqliteDatabase, Model, IntegerField, ForeignKeyField
from .models import Item
from settings import DATABASE_NAME


database = SqliteDatabase(DATABASE_NAME)


class Inventory(object):
    """
    The inventory object containing Items via InventorySlots
    """
    def __init__(self):
        self.inventory_id = None
        self.items = {}

    def add_item(self, item):
        item_id = item.get_id()
        if not self.__check_if_item_in_inventory(item_id):
            self.items[item.get_id()] = item

    def remove_item(self, item):
        item_id = item.get_id()
        if self.__check_if_item_in_inventory(item_id):
            del self.items[item.get_id()]

    def get_item(self, item):
        item_id = item.get_id()
        if self.__check_if_item_in_inventory(item_id):
            return self.items[item.get_id()]

    def get_all_items(self):
        return self.items.values()

    def __check_if_item_in_inventory(self, item_id):
        if item_id not in self.items:
            return False
        else:
            return True

    def save(self):
        if self.inventory_id and self.items:
            # This is to avoid keeping disposed items in the database.
            InventorySlot.delete().filter(inventory_id=self.inventory_id)
            for item in self.get_all_items():
                InventorySlot(inventory_id=self.inventory_id, item_id=item.get_id()).save()

    @classmethod
    def load(cls, inventory_id):
        loaded_inventory = Inventory()
        loaded_inventory.inventory_id = inventory_id
        for slot in InventorySlot.select().filter(inventory_id=inventory_id):
            item = Item.get(id=slot.item_id)
            loaded_inventory.add_item(item)


class InventorySlot(Model):
    """
    Describes a slot containing an item and referring to an inventory.
    """

    class Meta(object):
        database = database

    inventory_id = IntegerField(index=True)
    item_id = ForeignKeyField(Item, null=True)

    def __init__(self, inventory_id=None, item_id=None):
        super().__init__()
        if inventory_id is None:
            self.inventory_id = InventorySlot.raw("SELECT COUNT(inventory_id) FROM Inventory").execute()
        else:
            self.inventory_id = inventory_id