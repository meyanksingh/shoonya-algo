from api.api_manager import *
from database.database import Database
from logger.logger import setup_logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from config import APPLICATION_STRING
from config import USER, PWD, TOTP_KEY, APP_KEY, IMEI,INSTRUMENT,EXCH,ENTRY,EXIT,LOGIN_TIME,ORDER_PLACEMENT_TIME
from utils.utils import wait_until
import time


class TradingEngine:
    def __init__(self) -> None:
        self.database=Database()
        self.logger=setup_logging()
        self.logger.addHandler(AzureLogHandler(connection_string=APPLICATION_STRING))
        self.ApiManager=ApiManager()
        self.tokens={}
        self.account_margin=0

    def login(self)->None:
        try:
            self.logger.info("Attemping to login inside broker.....")
            login,uname=self.ApiManager.login_to_api(USER,PWD,TOTP_KEY,APP_KEY,IMEI)
            if login:
                self.logger.info(f'Successfully logged in {uname}')
            else:
                self.logger.error(f'Login failed exiting......')
                exit()
        except Exception as e:
            self.logger.error(f'Error with login: {e}')
            exit()

    def fetch_tokens(self)->None:
        self.logger.info(f'Fetching stock tokens.....')
        for symbol in INSTRUMENT:
            try:
                token,tsym=self.ApiManager.get_stock_token(symbol,EXCH)
                self.tokens[tsym]=token
                self.logger.info(f'Fetched token for: {symbol} : {token}')
            except Exception as e:
                self.logger.error(f'Error fetching tokens for {symbol}: {e}')

    def fetch_LTP(self)->dict:
        ltps={}

        for tsym in self.tokens.keys():
                try:
                    ltp = self.ApiManager.get_stock_ltp(EXCH,self.tokens[tsym])
                    ltps[tsym]=ltp
                    self.logger.info(f'{tsym} LTP: {ltp}')
                except Exception as e:
                    self.logger.error(f'Error fetching LTP for {tsym}: {e}')
        return ltps
    
    def place_order(self,ltps:dict)->dict:
        orders={}
        for tsym in ltps.keys():
            try:
                current_ltp = ltps[tsym]
                qty = self.ApiManager.get_stock_qty(self.account_margin,current_ltp)
                order_number = self.ApiManager.place_order(ENTRY,EXCH,tsym,qty)
                orders[tsym]=order_number
                self.logger.info(f'Order placed for {tsym}, Order number: {order_number}')
                try:
                    self.database.insert_data(order_number,"Entry-Orders",tsym,qty,ENTRY,"Market-Order",current_ltp,0.00)
                    self.logger.info(f"Data inserted successfully : {tsym} : {order_number}  ")
                except Exception as e:
                    self.logger.error(f"Data Inserted Failed {e}")
            except Exception as e:
                self.logger.error(f'Error placing order for {tsym}: {e}')
            
        return orders
    

    def confirm_order(self,orders)->dict:
        order_status={}
        rejected_order={}
        pending_orders={}
        for tsym in orders.keys():
            try:
                status,details = self.ApiManager.check_order_status(orders[tsym])
                if status =='REJECTED':
                    self.logger.info(f'Order {orders[tsym]} for {tsym} rejected: {details}')
                    rejected_order[tsym]=details
                elif status =='TRIGGER_PENDING' or status =='OPEN':
                    self.logger.info(f'Order {orders[tsym]} for {tsym} status: {status}')
                    pending_orders[tsym]=status
                else:
                    self.logger.info(f'Order {orders[tsym]} for {tsym} and status : {status}')
                    order_status[tsym]=orders[tsym]
            except Exception as e:
                self.logger.error(f'Error confirming order for {tsym} and order number: {orders[tsym]}: {e}')
        return order_status,rejected_order,pending_orders
    
    def place_stoploss(self,confirmed_order:dict)->dict:
        sl_orders={}
        for tsym in confirmed_order.keys():
            try:
                filled_price,filled_qty = self.ApiManager.get_filled_price_qty(confirmed_order[tsym])
                sl_price = self.ApiManager.calculate_stoploss(filled_price)
                trigger_price = self.ApiManager.calculate_trigger_price(sl_price)
                sl_order_number = self.ApiManager.place_stoploss(EXIT,tsym,filled_qty,sl_price,trigger_price)
                sl_orders[tsym]=sl_order_number
                self.logger.info(f'Stoploss order placed for {tsym}, SL Order number: {sl_order_number}')
                try:
                    self.database.insert_data(sl_order_number,"Stoploss-Orders",tsym,filled_qty,EXIT,"SL-Order-Limit",sl_price,trigger_price)
                    self.logger.info(f"Data inserted successfully : {tsym} : {sl_order_number}  ")
                except Exception as e:
                    self.logger.error(f"Data Inserted Failed {e}")
            except Exception as e:
                self.logger.error(f'Error placing stoploss order for {tsym}: {e}')
            
        return sl_orders
    
    def run(self):
        try:
            """Connect DB and Create Table"""
            self.database.connect_db()
        except Exception as e:
            self.logger.error(f'Error with Database Connection: {e}')
        
        try:
            """ Create Table"""
            self.database.create_table()
        except Exception as e:
            self.logger.error(f'Error with database table creation {e}')

        
        try:
            wait_until(LOGIN_TIME, 'for login')
            self.login()
        except Exception as e:
            self.logger.error(f'Error during login: {e}')
            exit()

        try:
            self.account_margin = self.ApiManager.get_margin()
            self.logger.info(f'Account Margin: {self.account_margin}')
            self.fetch_tokens()
        except Exception as e:
            self.logger.error(f'Error fetching account margin or tokens: {e}')
            return

        try:
            ltps = self.fetch_LTP()
        except Exception as e:
            self.logger.error(f'Error fetching LTPs: {e}')
            return

        try:
            wait_until(ORDER_PLACEMENT_TIME)
            orders = self.place_order(ltps)
        except Exception as e:
            self.logger.error(f'Error during order placement: {e}')
            return

        try:
            confirm_orders, rejected_order,pending_orders = self.confirm_order(orders)
        except Exception as e:
            self.logger.error(f'Error confirming orders: {e}')
            return

        sl_orders = None
        try:
            if confirm_orders:
                time.sleep(10)
                sl_orders = self.place_stoploss(confirm_orders)
            else:
                self.logger.info('All orders got rejected, nothing to place stoploss on')
        except Exception as e:
            self.logger.error(f'Error placing stoploss orders: {e}')

        confirm_sl_orders = None
        try:
            if sl_orders:
                confirm_sl_orders, rejected_sl_orders,pending_orders = self.confirm_order(sl_orders)
        except Exception as e:
            self.logger.error(f'Error confirming stoploss orders: {e}')

        if confirm_sl_orders:
            self.logger.info('All order and stoploss placement done. Please Check Logs!')

if __name__=='__main__':
    bot = TradingEngine()
    bot.run()
