from product import ProductService
from receipt import ReceiptService
from categories import AdminMenuOption
import datetime as dt

class ConsoleMenu:
    def __init__(self, menu_string:str, max_option:int):
        self._menu_string = menu_string
        self._max_options = int(max_option)
        self._current_option = ''

    def askOption(self):
        while True:
            self.printMenu()
            option = input('> ')

            if self.checkNumericalInput(option):
                self._current_option = option
                return


    def getCurrentOption(self) -> str:
        return self._current_option

    def printMenu(self):
        print(self._menu_string)

    def checkNumericalInput(self, your_input:str) -> bool:

        try:
            your_input = int(your_input)
        except ValueError:
            return False

        if your_input in range(0, self._max_options + 1):
            return True
        else:
            return False

class CheckoutMenu(ConsoleMenu):
    def __init__(self, menu_string:str, product_file):
        self._menu_string = str(menu_string)
        self._productService = ProductService(product_file)
        self._receiptService = ReceiptService(product_file)

    def checkout(self):
        new_receipt = self._receiptService.createNewReceipt()

        while True:
            self.printMenu()
            print(f"KVITTO   {new_receipt.getDatetimeObject()}")
            new_receipt.printMenuStrings()

            option = input('Kommandon: \n<product id> <antal> \nPAY \nKommando: ')
            input_values = option.lower().split(' ')

            if self.isValidCheckoutInput(input = input_values):
                prod_id = input_values[0]
                if prod_id.lower() == 'pay':

                    if len(new_receipt.getProducts()) > 0:
                        self._receiptService.addNewReceipt(new_receipt)
                    break
                
                prod_id = str(input_values[0])
                amount = float(input_values[1])
                
                prod = self._productService.findProduct(prod_id)
                prod.setAmount(amount)

                new_receipt.addProduct(prod)



    #TODO kind of messy logic
    def isValidCheckoutInput(self, input:list):
        if input[0].lower() == 'pay':
            return True

        if len(input) == 2:
            prod_id = input[0]
            amount = input[1]

            if self._productService.findProduct(prod_id) is not None:
                pass
            else:
                #print('Product ID does not exist')
                return False

            if amount.isnumeric():
                pass
            else:
                #print('Invalid amount)
                return False

            return True
        
        return False

class AdminMenu(ConsoleMenu):
    # Adminmenu
    # Ändra pris och namn
    # Starta kampanj
    # Hitta kvitton
    # Avsluta
    def __init__(self, menu_string:str, max_option:int, product_file:str):
        super().__init__(menu_string, max_option)
        self._current_option = AdminMenuOption.reset
        self._productService = ProductService(product_file)
        self._receiptService = ReceiptService(product_file)

    def askOption(self):
        while True:
            self.printMenu()
            option = input('> ')

            if self.checkNumericalInput(option):

                option = int(option)

                try:
                    self._current_option = AdminMenuOption(option)
                    return
                except ValueError:
                    #option does not exist, try again
                    pass
                


    def excecuteFromOption(self):
        # TODO add Categories(?)
        if self._current_option == AdminMenuOption.reset:
            pass

        elif self._current_option == AdminMenuOption.exit:
            return 'exit'

        elif self._current_option == AdminMenuOption.priceAndName:
            self.changePriceAndName()

        elif self._current_option == AdminMenuOption.manageCampaign:
            self.campaignManagement()

        elif self._current_option == AdminMenuOption.manageReceipts:
            self.receiptManagement()

        self._current_option = AdminMenuOption.reset
        return None


    def campaignManagement(self):

        while True:
            prod_id = input('Produkt ID: ')
            prod = self._productService.findProduct(prod_id)

            if prod is not None:
                break
        
        while True:
            print('Vilket blir produktens nya pris? ([enter] om du inte vill ändra)')
            print(f'Ordinarie pris: {prod.getPrice()}')
            new_campaign_price = input('> ')

            if new_campaign_price == '':
                break

            try:
                new_campaign_price = float(new_campaign_price)
                break
            except ValueError:
                pass

        while True:
            print('Vilket datum ska kampanjen börja? (Format: yyyymmdd)')
            campaign_start_date = input('> ')

            print('Vilket datum ska kampanjen sluta? (Format: yyyymmdd)')
            campaign_end_date = input('> ')

            try:
                start_datetime = dt.datetime.strptime(campaign_start_date, self._productService.datetime_format)
                end_datetime = dt.datetime.strptime(campaign_end_date, self._productService.datetime_format)
                break
            except ValueError:
                print('DATETIME ERROR WARNING WARNING')
                pass

        if self._productService.startCampaignOnProduct(prod_id, new_campaign_price, campaign_start_date, campaign_end_date):
            return True
        else:
            return False

    def changePriceAndName(self):
        while True:
            prod_id = input('Produkt ID: ')
            prod = self._productService.findProduct(prod_id)

            if prod is not None:
                break

        print('Vilket blir produktens nya namn? ([enter] om du inte vill ändra)')
        print(f'Nuvarande namn: {prod.getDescription()}')
        new_description = input('> ')

        while True:
            print('Vilket blir produktens nya pris? ([enter] om du inte vill ändra)')
            print(f'Nuvarande pris: {prod.getPrice()}')
            new_price = input('> ')

            if new_price == '':
                new_price = 0
                break

            else:
                try:
                    new_price = float(new_price)
                    break
                except ValueError:
                    print('Ange giltigt pris')

        self._productService.updateProductNamePrice(prod_id, new_description, new_price)
        return
    
    def receiptManagement(self):
        while True:
            receipt_dict = self._receiptService.getOldReceipts()
            available_dates = self._receiptService.getReceiptDates()
            print('Tillgängliga datum: ')
            for available_date in available_dates:
                print(available_date)
            #print('\n')
            print('Vilket datum vill du se? [yyyymmdd]-format')
            print('[0] för att gå tillbaka')
            date = input('> ')
            if date == '0':
                return True
            
            try:
                for receipt in receipt_dict[date]:
                    print_string = f"Serienummer: {receipt.getSerialNr()}, Total: {receipt.getTotal()}"
                    print(print_string)
                    
                input('fortsätt > ')
                while True:
                    print('Vill du se specifikt kvitto? [0] för att gå tillbaka')
                    serial_nr = input('Ange serienummer: ')

                    if serial_nr == '0':
                        break

                    specific_receipt = self._receiptService.findReceipt(serial_nr)

                    if specific_receipt is not None:
                        specific_receipt.printMenuStrings()
                        input('fortsätt > ')
                        
            except KeyError:
                pass
                
            




