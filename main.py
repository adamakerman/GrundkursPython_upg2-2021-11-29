from menu import ConsoleMenu, CheckoutMenu, AdminMenu

def kassan(product_filename = 'products.txt'):
    while True:
        main_menu_string = 'KASSA \n1. Ny Kund \n2. Admin \n0. Avsluta'
        start_menu = ConsoleMenu(main_menu_string, 2)
        start_menu.askOption()
        
        option1 = start_menu.getCurrentOption()

        if option1 == '0':
            print('Shutting down...')
            break

        elif option1 == '1':
            checkout_menu = CheckoutMenu('KASSA', product_filename)
            checkout_menu.checkout()
            del checkout_menu

        elif option1 == '2':
            while True:
                admin_menu_text = 'ADMIN \n1. Ändra pris & namn \n2. Starta kampanj \n3. Hitta kvitton \n0. Avsluta'
                admin_menu = AdminMenu(admin_menu_text, 3, product_filename)
                admin_menu.askOption()
                option2 = admin_menu.excecuteFromOption()

                if option2 == 'exit':
                    del admin_menu
                    break

kassan('products.txt')




        

