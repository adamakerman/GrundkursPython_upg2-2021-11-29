from product import Product
from product import ProductService
import datetime as dt
from database import CSVdb
from categories import PriceType
from copy import deepcopy


class _Receipt():

    datetime_format = '%Y%m%d'
    time_format = '%H:%M:%S'

    def __init__(self):
        self._date_string = ''
        self._time_string = ''
        self._serial_number = ''
        self._products = []

    def addProduct(self, product:Product):
        independent_product = deepcopy(product)
        assert type(independent_product) == Product
        self._products.append(independent_product)

    def getTotal(self) -> float:
        total = 0

        for product in self._products:
            total += product.calculatePrice()

        return total

    def getTime(self):
        return self._time_string

    def getDate(self):
        return self._date_string

    def getDataList(self) -> list:
        data_list = []

        if len(self._products) == 0:
            return data_list
        
        for product in self._products:

            receipt_data = [self._serial_number, self._time_string]
            
            if product.isCampaign():
                is_campaign_string = 'yes'
            else:
                is_campaign_string = 'no'

            product_data = product.getInfoList('id', 'description', 'amount', 'active_price', 'price_type')

            full_row = receipt_data + product_data + [is_campaign_string]
            
            data_list.append(full_row)

        return data_list

    def getProducts(self):
        return self._products

    def getSerialNr(self):
        return self._serial_number

    def printMenuStrings(self) -> None:
        if len(self._products) == 0:
            return
        
        for prod in self._products:
            print_string = f"{prod.getDescription()} {prod.getAmount()} * {prod.getActivePrice()} = {round(prod.calculatePrice(), 2)}"
            print(print_string)
            
        end_string = f"Total: {self.getTotal()}"
        print(end_string)
        return

    def getDatetimeObject(self) -> dt.datetime:
        datetime_string = self.getDate() + self.getTime()
        combo_datetime_format = self.datetime_format + self.time_format

        datetime_obj = dt.datetime.strptime(datetime_string, combo_datetime_format)

        return datetime_obj

class OldReceipt(_Receipt):
    def __init__(self, serial_nr:str, date_string:str, time_string:str):
        self._date_string = str(date_string)
        self._serial_number = str(serial_nr)
        self._time_string = str(time_string)
        self._products = []
    
class NewReceipt(_Receipt):
    def __init__(self, serial_nr:str):
        super().__init__()
        self._serial_number = str(serial_nr)
        self._setInfoAuto()

    def _setInfoAuto(self):
        now = dt.datetime.now()
        self._time_string = dt.datetime.strftime(now, self.time_format)
        self._date_string = dt.datetime.strftime(now, self.datetime_format)

class ReceiptService():
    _colnames = ['serial_nr', 'time', 'product_id', 'product_description', 'amount', 'price', 'type', 'campaign']
    datetime_format = '%Y%m%d'
    time_format = '%H:%M:%S'

    def __init__(self, product_file:str):
        self._db = {} #requires multiple databases because data in different files        
        self._setDatabasesAuto()
        self._old_receipts = self.getReceiptsFromDb()
        self._productService = ProductService(product_file)

    def fileExists(self):
        pass

    def _setDatabasesAuto(self):
        filenames = CSVdb.getFilenames(contains = 'receipt_')
        dates = [file_path.split('_')[1][:-4] for file_path in filenames]

        for i, date in enumerate(dates):
            self._db[date] = CSVdb(filenames[i], self._colnames)

    def getDatabases(self) -> dict:
        return self._db

    # TODO Kinda mixed responsabillities - maybe split into multiple functions
    def getReceiptsFromDb(self) -> dict:
        db_dict = self.getDatabases()
        receipt_dict = {}

        for date in db_dict.keys():
            data = db_dict[date].getData()

            if len(data) == 0:
                continue

            receipt_dict[date] = []
            last_serial_nr = data[0][0]
            old_receipt = OldReceipt(last_serial_nr, date, data[0][1])

            for row in data:
                data_dict = db_dict[date].convertToDataDict(row)
                current_serial_nr = data_dict['serial_nr']
                type_weight = PriceType.weight if data_dict['type'] == 'w' else PriceType.quantity
                prod = Product(data_dict['product_id'], data_dict['product_description'], data_dict['price'], type_weight, data_dict['amount'] )
                
                if row == data[-1]: #special case for last iteration (only works if all rows are unique) possible bug
                    old_receipt.addProduct(prod)
                    receipt_dict[date].append(old_receipt)

                elif last_serial_nr != current_serial_nr:
                    receipt_dict[date].append(old_receipt)
                    old_receipt = OldReceipt(data_dict['serial_nr'], date, data_dict['time'])
                    old_receipt.addProduct(prod)

                else: 
                    old_receipt.addProduct(prod)
                
                last_serial_nr = current_serial_nr
                
        return receipt_dict

    def addNewReceipt(self, receipt:NewReceipt):
        assert type(receipt) == NewReceipt

        date = receipt.getDate()

        try:
            db = self._db[date]

        except KeyError:
            # No db from this date exists
            # New DB class has to be created
            self._db[date] = CSVdb(f"receipt_{date}.txt", self._colnames)
            self._db[date].appendData(self._colnames)
            db = self._db[date]
            self._old_receipts[date] = []

        db.appendData(receipt.getDataList())
        self._old_receipts[date].append(receipt)

    def getLastSerialNr(self) -> int:
        dates = list(self._old_receipts.keys())
        sorted_dates = sorted(dates)
        last_date = sorted_dates[-1]

        last_receipt_data = self._db[last_date].getData()

        last_serial_nr = int(last_receipt_data[-1][0])
        return last_serial_nr

    def createNewReceipt(self) -> NewReceipt:
        serial_nr = str(self.getLastSerialNr() + 1)
        new_receipt = NewReceipt(serial_nr)
        return new_receipt

    def getReceiptDates(self) -> list:        
        return list(self._old_receipts.keys())

    def getOldReceipts(self) -> list:
        return self._old_receipts


    def findReceipt(self, serial_nr:str) -> OldReceipt:
        for date in self._old_receipts.keys():

            receipt_from_date = self._old_receipts[date]

            for receipt in receipt_from_date:
                if receipt.getSerialNr() == serial_nr:
                    return receipt

        return None



