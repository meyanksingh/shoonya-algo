from NorenRestApiPy.NorenApi import NorenApi
import pandas as pd
import pyotp
from logger.logger import setup_logging

from config import HOST, WEBSOCKET

logger = setup_logging()

class ShoonyaApiPy(NorenApi):
    def __init__(self)->None:
        NorenApi.__init__(self, host=HOST,
                          websocket=WEBSOCKET)
        
class ApiManager:
    def __init__(self) -> None:
        self.api=ShoonyaApiPy()

    def login_to_api(self, user: str, pwd: str, totp_key:str, app_key:str, imei:str)-> tuple[bool,str]:
        """Login Function"""
        try:
            uname=self.api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(
                totp_key).now(), vendor_code=user+'_U', api_secret=app_key, imei=imei)
            return True,uname['uname']
        except Exception as e:
            return False
        

    def get_margin(self)-> int:
        '''Returns Account Margin'''
        try:
            data = self.api.get_limits()
            cash = float(data['cash'])
            return int(cash)-300
        except Exception as e:
            logger.error(f'An error occurred while getting margin: {e}')
            

    def get_stock_token(self,text:str,exch:str)-> tuple[str,str]:
        '''Returns Stock Token and TSYM(Trading Name)'''
        try:
            data = self.api.searchscrip(exch,text)
            token = data['values'][0]['token']
            tsym = data['values'][0]['tsym']
            return token,tsym
        except Exception as e:
            logger.error(f"Error with getting token and tsym for {text}: {e}")
            return False
        

    def get_stock_ltp(self,exch:str,token:str)-> int:
        '''Returns LTP of a stock'''
        try:
            data = self.api.get_quotes(exch,token)
            return float(data['lp'])
        except Exception as e:
            logger.error(f"Error with getting LTP for token {token}: {e}")
            return False
        

    def get_stock_qty(self,margin:int,stock_ltp:int)->int:
        '''Calculate stock quantity based on current margin and LTP'''
        try:
            qty = max(1, int(margin / int(stock_ltp)))
            return qty
        except Exception as e:
            logger.error(f'Error with Calculation Quantity {e}')


    def place_order(self,b_or_s:str,exch:str, tsym: str, qty: int) -> str:
        """Place a market order"""
        try:
            ret = self.api.place_order(buy_or_sell=b_or_s.upper(), product_type='I',
                                exchange=exch, tradingsymbol=tsym,
                                quantity=qty, discloseqty=0, price_type='MKT', price=0.00, trigger_price=0.00,
                                retention='DAY', remarks='my_order_001')
            logger.info(f'Order successfully placed for {tsym} with order number {ret["norenordno"]}')
            return ret["norenordno"]
        except Exception as e:
            logger.error(f"Error placing order for {tsym}: {e}")
            return None
        

    def get_filled_price_qty(self,orderno:str)-> tuple[float,int]:
        '''Get filled price and filled quantity of an order'''
        try:
            data = self.api.get_order_book()
            df = pd.DataFrame(data)
            filter_df = df[df['norenordno'] == orderno]
            avgprc, fillshares = filter_df[['avgprc', 'fillshares']].values[0]
            return int(float(avgprc)), int(float(fillshares))
        except Exception as e:
            logger.error(f"Error fetching filled price and quantity for order {orderno}: {e}")
            return None
        

    def calculate_stoploss(self,filled_price: float) -> float:
        try:
            '''Returns Stoploss Price'''
            stoploss = filled_price / 100
            final_stoploss = round((filled_price - stoploss) * 20) / 20
            return round(final_stoploss, 2)
        except Exception as e:
            logger.error(f"Error Calculating the Stoploss for {filled_price}: {e}")
            return None
        
    def calculate_trigger_price(self,sl_price:int)->int:
        '''Returns Trigger Price for Buying Side Stoploss Only'''
        return sl_price + 0.20 if sl_price < 100 else sl_price + 0.65
        
    def check_order_status(self,orderno:str)-> tuple[str,str]:
        '''Returns the order status of an ordernumber'''
        try:
            ret = self.api.single_order_history(orderno=orderno)
            status = ret[0]['status']
            detail = ret[0]['rejreason'] if status == 'REJECTED' else ret[0]['norentm']
            return status, detail
        except Exception as e:
            logger.error(f"Error checking the status of order {orderno}: {e}")
            return None

    def place_stoploss(self,b_or_s:str, tsym: str, qty: int, price: float, trigger_price: float) -> str:
        '''Place a stop-loss order'''
        try:
            ret = self.api.place_order(buy_or_sell=b_or_s.upper(), product_type='I',
                                exchange="NSE", tradingsymbol=tsym,
                                quantity=qty, discloseqty=0, price_type='SL-LMT', price=price, trigger_price=trigger_price,
                                retention='DAY', remarks='my_order_001')
            logger.info(f'Stop-loss order successfully placed for {tsym} with order number {ret["norenordno"]}')
            return ret["norenordno"]
        except Exception as e:
            logger.error(f"Error placing stop-loss order for {tsym}: {e}")
            return None
        
    def get_MTM(self)->float:
        """Get the mark-to-market value"""
        try:
            ret = self.api.get_positions()
            mtm = sum(float(i['urmtom']) for i in ret)
            pnl = sum(float(i['rpnl']) for i in ret)
            day_m2m = mtm + pnl
            logger.info(f'Daily MTM: {day_m2m}')
            return day_m2m
        except Exception as e:
            logger.error(f"Error getting MTM: {e}")
            return None