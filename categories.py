from enum import Enum

class PriceType(Enum):
    weight = 1
    quantity = 2

class AdminMenuOption(Enum):
    exit = 0
    priceAndName = 1
    manageCampaign = 2
    manageReceipts = 3
    reset = 99