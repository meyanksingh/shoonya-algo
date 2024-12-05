import psycopg2
import pytz
from datetime import datetime
from logger.logger import setup_logging
from config import DB_HOST,DB_NAME,DB_PASSWORD,DB_USER

class Database:
    def __init__(self) -> None:
        self.cur = None
        self.conn= None
        self.logger=setup_logging()
        self.DB_HOST=DB_HOST
        self.DB_NAME=DB_NAME
        self.DB_USER=DB_USER
        self.DB_PASSWORD=DB_PASSWORD

    
    def connect_db(self)-> None:
        try:
            self.conn=psycopg2.connect(host=self.DB_HOST, dbname=self.DB_NAME, user=self.DB_USER, password=self.DB_PASSWORD)
            self.cur=self.conn.cursor()
            self.logger.info(f"Database connected: {DB_NAME}")
        except Exception as e:
            self.logger.error(f'Failed to connect to database: {e}')
        

    def create_table(self)->None:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS MunniAlgo (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    OrderNumber BIGINT,
                    Tag VARCHAR(20),
                    TSYM VARCHAR(20),
                    Quantity INT,
                    OrderType VARCHAR(20),
                    OrderPricingType VARCHAR(20),
                    OrderPrice FLOAT,
                    TriggerPrice FLOAT
                )
            """)
            self.conn.commit()
            self.logger.info('Table created successfully')

    def insert_data(self, order_number:int, tag:str, tsym:str, quantity:int, order_type:str, order_pricing_type:str, order_price:float, trigger_price:float)->None:
        try:
            utc_now = datetime.now()
            ist = pytz.timezone('Asia/Kolkata')
            date = str(utc_now.replace(tzinfo=pytz.utc).astimezone(ist))
            timestamp=date.split('.')[0]
            self.cur.execute("""
                INSERT INTO MunniAlgo (timestamp, ordernumber, tag, tsym, quantity, ordertype, orderpricingtype, orderprice, triggerprice)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (timestamp, order_number, tag, tsym, quantity, order_type, order_pricing_type, order_price, trigger_price))
            self.conn.commit()
            self.logger.info(f'Data inserted successfully for order number: {tsym} : {order_number}')
        except Exception as e:
            self.logger.error(f'Failed to insert data: {e}')
            
    
    def close(self)-> None:
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")