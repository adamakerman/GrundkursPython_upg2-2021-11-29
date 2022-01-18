import datetime as dt
from categories import PriceType
from database import CSVdb
from copy import deepcopy

class Product():

    datetime_format = '%Y%m%d'
    
    def __init__(self, id:str, description:str, price:float, price_type: PriceType, amount = 1):
        self._id = str(id)
        self._description = str(description)
        self._price = float(price)
        self._price_type = price_type
        self._amount = float(amount)

        self._campaign = {'price':0, 'start_date':None, 'end_date':None}


    def startCampaign(self, new_price:float, start = dt.datetime, end = dt.datetime):
        campaign_data = {'price':new_price, 'start_date':start, 'end_date':end}
        self._campaign = campaign_data

    def isCampaign(self, date = 'today') -> bool:

        if date == 'today':
            datetime_obj = dt.datetime.today()
        else:
            datetime_obj = dt.datetime.strptime(date, self.datetime_format)
        
        try:
            delta_start = self._campaign['start_date'] - datetime_obj
            delta_end = self._campaign['end_date'] - datetime_obj
        except TypeError:
            # Dates are undefined, no campaign
            return False
        
        if delta_start.days <= 0 and delta_end.days >= 0:
            return True
        else:
            # Currently outside the campaign-window
            return False

    def calculatePrice(self) -> float:
        active_price = self.getActivePrice()
        
        return self.getAmount() * active_price

    def getActivePrice(self) -> float:
        if self.isCampaign():
            return self._campaign['price']
        else:
            return self._price

    def getPrice(self) -> float:
        return self._price

    def setAmount(self, amount:float) -> None:
        self._amount = float(amount)

    def setDescription(self, new_description:str):
        self._description = str(new_description)

    def setPrice(self, new_price:float):
        self._price = float(new_price)

    def getId(self):
        return self._id

    def getDescription(self):
        return self._description
    
    def getAmount(self):
        if self._price_type == PriceType.weight:
            return float(self._amount)
        elif self._price_type == PriceType.quantity:
            return int(self._amount)
        #TODO should not happen
        else:
            return float(self._amount)

    def getPriceTypeString(self) -> str:
        if self._price_type == PriceType.weight:
            return 'w'
        elif self._price_type == PriceType.quantity:
            return 'q'


    def getCampaignString(self) -> str:
        if self.isCampaign():
            return 'yes'
        else:
            return 'no'

    def getRecieptInfo(self):
        #['serial_nr', 'time', 'product_id', 'product_description', 'amount', 'price', 'type', 'campaign']

        if self._price_type == PriceType.weight:
            amount_type = 'w'
        elif self._price_type == PriceType.quantity:
            amount_type = 'q'

        is_campaign = 'yes' if self.isCampaign() else 'no'
        
        receipt_info = [self._id, self._description, str(self._amount), str(self.getActivePrice()), amount_type, is_campaign]
        return receipt_info
    
    def getInfoList(self, *args):
        data_list = []
        all_data_dict = self.__dict__

        for attribute in args:

            key = f"_{attribute}"

            if attribute == 'price_type':
                if self._price_type == PriceType.weight:
                    data_list.append('w')
                elif self._price_type == PriceType.quantity:
                    data_list.append('q')

            elif attribute == 'campaign_dict':
                try:
                    price = str(self._campaign['price'])
                    start = dt.datetime.strftime(self._campaign['start_date'], self.datetime_format)
                    end = dt.datetime.strftime(self._campaign['end_date'], self.datetime_format)
                except TypeError:
                    price = '0'
                    start = '0'
                    end = '0'

                campaign_info = [price, start, end]
                data_list += campaign_info

            elif attribute == 'active_price':
                data_list.append(str(self.getActivePrice()))
            
            else:

                try:   
                    attribute_value = all_data_dict[key]
                    data_list.append(str(attribute_value))

                except KeyError:
                    pass

        return data_list


    def getInfoDict():
        pass

class ProductService:
    _colnames = ['id', 'description', 'price', 'price_type', 'campaign_price', 'campaign_start', 'campaign_end']
    datetime_format = '%Y%m%d'

    def __init__(self, filename):
        self.db = CSVdb(filename, self._colnames)
        self._product_list = self._getAllProducts()

    def _getAllProducts(self):

        product_data = self.db.getData()

        product_list = []

        for row in product_data:
            data = self.db.convertToDataDict(row)

            type_weight = PriceType.weight if data['price_type'] == 'w' else PriceType.quantity

            prod = Product(data['id'], data['description'], float(data['price']), type_weight)

            campaign_price = float(data['campaign_price'])

            if campaign_price > 0:
                start = dt.datetime.strptime(data['campaign_start'], self.db.datetime_format)
                end = dt.datetime.strptime(data['campaign_end'], self.db.datetime_format)
                prod.startCampaign(campaign_price, start, end)
            else:
                start = 0
                end = 0
        
            product_list.append(prod)
        
        return product_list

    def findProduct(self, product_id:str, get_index = False) -> Product:

        for i, prod in enumerate(self._product_list):
            if prod.getId() == product_id:

                if get_index:
                    return deepcopy(prod), i
                else:
                    return deepcopy(prod)

        if get_index:
            return None, None
        else:
            return None

    def updateDB(self):
        old_data = self.db.getData(get_header=True)
        new_data = [self._colnames]

        assert old_data[0] == new_data[0]
        

        for prod in self._product_list:
            new_data.append(prod.getInfoList('id', 'description', 'price', 'price_type', 'campaign_dict'))

        affected_rows = 0
        for i, row in enumerate(new_data):
            if row != old_data[i]:
                affected_rows += 1

        if affected_rows > 0:
            checker = input(f"Are you sure you sure you want to update the database? {affected_rows} row(s) affected (y/n)")
        else:
            checker = 'y'

        if checker == 'y':
            self.db.overwriteFile(new_data)
            return True
        else:
            return False


    def updateProductNamePrice(self, product_id:str, new_description='', new_price = 0):
        old_products = self._product_list.copy()
        prod, index = self.findProduct(product_id, get_index=True)

        if len(new_description) > 0:
            prod.setDescription(new_description)
        
        if new_price > 0:
            prod.setPrice(new_price)

        self._product_list[index] = prod

        if self.updateDB():
            return
        else:
            self._product_list = old_products
            return

    def startCampaignOnProduct(self, prod_id:str, new_price:float, start_date:str, end_date:str) -> bool:

        prod, index = self.findProduct(prod_id, get_index = True)
        try:
            start_datetime = dt.datetime.strptime(start_date, self.datetime_format)
            end_datetime = dt.datetime.strptime(end_date, self.datetime_format)
        except TypeError:
            return False
        if prod is None:
            return False

        prod.startCampaign(new_price, start_datetime, end_datetime)

        self._product_list[index] = prod
        self.updateDB()
        return True

