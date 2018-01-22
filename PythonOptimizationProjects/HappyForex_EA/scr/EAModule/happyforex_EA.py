'''
Created on Dec 12, 2017

@author: cao.vu.lam
'''

import random

from DataHandler.happyforex_Datahandler import *


logger = logging.getLogger(__name__)


#===============================================================================
def BrokerIs5Digit_0():
    ''' Return TRUE if the Broker is the 5 Digits Broker '''

    if (DIGITS == 5 or DIGITS == 3): 
        return(True)
    else:
        return(False)


################################################################################
#########################           CLASS           ############################
################################################################################        

class HappyForexEA(object):
    '''
    classdocs
    '''
 
    #===============================================================================
    def __init__(self):
        '''
        Constructor
        '''
        
        # new variables which will be changed in the class
        self.total_win = float(DEFAULT_NUMBER) 
        self.total_loss = float(DEFAULT_NUMBER)
        self.total_orders = float(DEFAULT_NUMBER)
        self.ords_in_a_day = DEFAULT_NUMBER
        self.current_date = ""
        self.current_time = ""
        self.current_datetime = ""
        self.old_date = ""
        self.bid_price = float(DEFAULT_NUMBER)
        self.ask_price = float(DEFAULT_NUMBER)
        self.mode_spread = float(DEFAULT_NUMBER)
        self.order_ID_dict = {}  # a dictionary (as a hash-map) for storing ID
            
        self.SpreadMax = SPREADMAX
        self.Hour_of_trading_from = HOUR_OF_TRADING_FROM
        self.Hour_of_trading_to = HOUR_OF_TRADING_TO
        self.Time_of_closing_in_hours = TIME_OF_CLOSING_IN_HOURS
        self.Time_of_closing_in_minutes = TIME_OF_CLOSING_IN_MINUTES
        self.Time_closing_trades = TIME_CLOSING_TRADES
        self.Lots = LOTS
        self.Slippage = SLIPPAGE
        
        self.balance = DEPOSIT
        self.CurrentProfit = float(DEFAULT_NUMBER)
        self.equity = self.balance + self.CurrentProfit
        
        # Create a dictionary (as a hash-map) for storing Closed and Deleted orders with KEY is OrderID
        self.ORDER_CLOSED_DICT = {} 
        
        # Create a dictionary (as a hash-map) for storing Opened and Pending orders with KEY is OrderID
        self.ORDER_OPENED_DICT = {} 
        
        # Create a dictionary (as a hash-map) for storing Opened and Pending orders with KEY is OrderID
        self.DATE_DATA_DICT = {} 
        
        # old variables from EA
        self.NDigits = DIGITS
        self.PipValue = float(DEFAULT_SECOND_NUMBER)
        self.my_point = POINT
        
        self.ATR_Period = 7.0
        self.ATRPeriod1 = 3.0
        self.ATRPeriod2 = 5.0 
        self.ATRUpLimit1 = 13.0
        self.ATRDnLimit1 = 7.0
        self.ATRUpLimit2 = 21.0 
        self.ATRDnLimit2 = 16.0
        self.ATRUpLimit3 = 28.0
        self.ATRDnLimit3 = 25.0
        self.DeletePOATR = True      
        self.DeleteOrderATR = False
        
        self.LF = "\n"  
        self.ObjCount = DEFAULT_NUMBER  
        self.FirstTime33 = False
        self.FirstTime35 = False
        self.Today6 = -1
        self.Count32 = DEFAULT_NUMBER
        self.dblProfit = float(DEFAULT_NUMBER)
        self.ATR = ""
        self.Trading = ""
        self.OrderCounter = DEFAULT_NUMBER  # total Opened and Pending orders
        self.SellOrderExists = False
        self.BuyOrderExists = False
        self.BuyPOExists = False
        self.SellPOExists = False
        self.Overide = False
        self.Hour1 = DEFAULT_SECOND_NUMBER
        self.Minute1 = DEFAULT_NUMBER
        self.MagicChange = ""
        self.RMStatus = ""
        
        self.clear = False
        
        
#         ObjectsDeleteAll();   //SKIP from original EA
#         Comment("");          //SKIP from original EA
        
        
        # Adjust for 4/5 digit brokers
        if BrokerIs5Digit_0(): 
            self.PipValue = float(10)
            self.my_point *= float(10)
            self.SpreadMax *= float(10)
        
        # Adjust the time following local time
        self.Hour_of_trading_from += GMT_OFFSET
        if(self.Hour_of_trading_from >= HOURS_OF_ADAY):
            self.Hour_of_trading_from -= HOURS_OF_ADAY
        if(self.Hour_of_trading_from < DEFAULT_NUMBER):
            self.Hour_of_trading_from += HOURS_OF_ADAY 
                
        self.Hour_of_trading_to += GMT_OFFSET
        if(self.Hour_of_trading_to >= HOURS_OF_ADAY):
            self.Hour_of_trading_to -= HOURS_OF_ADAY
        if(self.Hour_of_trading_to < DEFAULT_NUMBER):
            self.Hour_of_trading_to += HOURS_OF_ADAY 
        
        self.Time_of_closing_in_hours += GMT_OFFSET
        if(self.Time_of_closing_in_hours >= HOURS_OF_ADAY):
            self.Time_of_closing_in_hours -= HOURS_OF_ADAY
        if(self.Time_of_closing_in_hours < DEFAULT_NUMBER):
            self.Time_of_closing_in_hours += HOURS_OF_ADAY

    #===============================================================================
    def CalculateProfit_5(self, entry_price, exit_price, order_type):
        ''' Calculates the profit or loss of a position in the home currency of the account. 
        1/When you go long, you enter the market at the ASK price and exit the market at BID price.
        2/When you go short, you enter the market at the BID price and exit at the ASK price.
        3/Pip Value = Pip in decimal places / Market Price * Trade Size
        For QUOTE_CURRENCY = 'USD', Pip Value will be multiple to Market Price 1 more time
        
        ==> Pip in decimal places = 0.0001 since 1/10,000th is a pip for all pairs (except JPY pairs)
                              = 0.01 for a JPY pair.
        ==> In all pairs involving the Japanese Yen (JPY), a pip is the 1/100th place -- 2 places to the right of the decimal. 
        In all other currency pairs, a pip is the 1/10,000 the place -- 4 places to the right of the decimal.
        '''
        
#         OLD CODES (17/01/2018_17:00:00)
#         result = float(DEFAULT_NUMBER)
#     
#         if  (order_type == OP_BUY): 
#             result = ((exit_price - entry_price) * self.Lots * (1 / self.my_point) 
#                       * (PIP_VALUE_DICT[SYMBOL] * self.Lots / EXCHANGE_RATE_USD[QUOTE_CURRENCY]))
#         
#         
#         elif (order_type == OP_SELL):
#             result = ((entry_price - exit_price) * self.Lots * (1 / self.my_point) 
#                       * (PIP_VALUE_DICT[SYMBOL] * self.Lots / EXCHANGE_RATE_USD[QUOTE_CURRENCY]))
#         
#         return result
     
        result = float(DEFAULT_NUMBER)
     
        if  (order_type == OP_BUY): 
            result = (exit_price - entry_price) * self.Lots * ONE_LOT_VALUE - COMMISSION
         
        elif (order_type == OP_SELL):
            result = (entry_price - exit_price) * self.Lots * ONE_LOT_VALUE - COMMISSION
        
        return round(float(result), self.NDigits)
        
    #===============================================================================
    def CreateUniqueOrderID_9(self, order_type):
        '''Create the unique order ID. Return -1 when cannot generate an order ID. '''
        
        # create the unique order ID which is the combination of all Values of parameters
        new_id = (convert_string_datetime2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT) 
                  + float(datetime.now().second))
        
        # keep create an individual while the ID is not unique
        while (new_id in self.order_ID_dict):
            new_id = (convert_string_datetime2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT) 
                  + float(datetime.now().second))
        
        # save new ID into the ID dictionary
        self.order_ID_dict[new_id] = order_type
        
        return new_id
    
    #===============================================================================
    def MaxOrders_9(self, num):
        ''' Return TRUE if the total number of orders in a day equal the Orders Limit per Day
            Delete all pending order in Opened and Pending orders pool when max orders reached '''
        
        ords = DEFAULT_NUMBER
        CurrentDay = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
        order_type = -1
        
        if (USE_ORDERSLIMIT == False): 
            return False
        
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        # get all Opened and Pending orders in the pool
        for order_id in self.ORDER_OPENED_DICT.keys():
            # --> get the date-time of the opened/pending orders
            opened_order = self.ORDER_OPENED_DICT[order_id]
            OrderOpenTime = opened_order[DATE_COL_INDEX]
            
            # --> count orders when orders are BUY/SELL and in the current day (replace for: iBarShift(NULL,PERIOD_D1,OrderOpenTime())==0)
            order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
            if (order_type < 2.00 and OrderOpenTime == CurrentDay):
                ords += DEFAULT_SECOND_NUMBER
        
        # get all Closed and Deleted orders in the pool
        for order_id in self.ORDER_CLOSED_DICT.keys():
            # --> get the date-time of the closed/deleted orders and current date-time
            closed_order = self.ORDER_CLOSED_DICT[order_id]
            OrderClosedTime = closed_order[DATE_COL_INDEX]
            
            # --> count orders when orders are BUY/SELL and in the current day (replace for: iBarShift(NULL,PERIOD_D1,OrderOpenTime())==0)
            order_type = self.OrderType_5(order_id, self.ORDER_CLOSED_DICT)
            if (order_type < 2.00 and OrderClosedTime == CurrentDay):
                ords += DEFAULT_SECOND_NUMBER
                
        if (ords >= num):
            # get all Opened and Pending orders in the pool
            for order_id in self.ORDER_OPENED_DICT.keys():
                # --> delete orders when they are BUYLIMIT/SELLLIMIT
                order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
                if (order_type > 1.00):
                    self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
    
            # max number of orders reached
            return True  
        else:
            return False
        
        ''' 
        # SKIP from the original EA
        if ((OrderSelect(k,SELECT_BY_POS,MODE_TRADES))&&(OrderSymbol()==Symbol())&&(OrderMagicNumber()==Magic))s
            if (self.OrderType_5() < 2 and iBarShift(NULL,PERIOD_D1,OrderOpenTime())==0):
                    ords += 0
                     
        for( k=OrdersHistoryTotal()-1;k>=0;k--)
        {
           if((OrderSelect(k,SELECT_BY_POS,MODE_HISTORY))&&(OrderSymbol()==Symbol())&&(OrderMagicNumber()==Magic))
           {
              if(OrderType_5() < 2 && iBarShift(NULL,PERIOD_D1,OrderOpenTime())==0 )
                 ords++;
           }
        }
         
        '''
    #===============================================================================
    def ProfitCheck_3(self):
        ''' Return Profit of all closed trades following the '''
    
        net_profit = float(DEFAULT_NUMBER)
        
        if (len(self.ORDER_OPENED_DICT) == DEFAULT_NUMBER and len(self.ORDER_CLOSED_DICT) == DEFAULT_NUMBER):
            return net_profit
        else:
            # get all the profits from Closed and Deleted orders
            for order_id in self.ORDER_CLOSED_DICT.keys():  # The order of the k's is not defined
                order = self.ORDER_CLOSED_DICT[order_id]
                
                if float_checker(order[PROFIT_COL_INDEX]):
                    net_profit += order[PROFIT_COL_INDEX]
                    
            # get all the profits from Opened and Pending orders
            for order_id in self.ORDER_OPENED_DICT.keys():  # The order of the k's is not defined
                order = self.ORDER_OPENED_DICT[order_id]
    
                if float_checker(order[PROFIT_COL_INDEX]):
                    net_profit += order[PROFIT_COL_INDEX]
            
        return net_profit
        
    #===============================================================================
    def AccountBalance_1(self):
        ''' Return current balance of all orders '''
    
        account_bal = self.balance
        
        if (len(self.ORDER_OPENED_DICT) == DEFAULT_NUMBER and len(self.ORDER_CLOSED_DICT) == DEFAULT_NUMBER):
            return account_bal
        else:
            # get all the balance from Closed and Deleted orders
            for order_id in self.ORDER_CLOSED_DICT.keys():  # The order of the k's is not defined
                order = self.ORDER_CLOSED_DICT[order_id]
                
                if (float_checker(order[BALANCE_COL_INDEX]) and order[BALANCE_COL_INDEX] > account_bal):
                    account_bal = order[BALANCE_COL_INDEX]
    
            # get all the balance from Opened and Pending orders
            for order_id in self.ORDER_OPENED_DICT.keys():  # The order of the k's is not defined
                order = self.ORDER_OPENED_DICT[order_id]
                
                if (float_checker(order[BALANCE_COL_INDEX]) and order[BALANCE_COL_INDEX] > account_bal):
                    account_bal = order[BALANCE_COL_INDEX]

        return account_bal
    
    #===============================================================================
    def DayOfWeek_3(self):
        ''' Return the current zero-based day of the week (0-Monday,1,2,3,4,5,6) of the system time. '''
    
        return datetime.today().weekday()
    
    #===============================================================================
    def TimeHour_4(self):
        ''' Return the Hour of current time. '''
    
        return datetime.now().hour
    
    #===============================================================================
    def TimeMinute_3(self):
        ''' Return the Minute of current time. '''
    
        return datetime.now().minute
    
    #===============================================================================
    def MODE_SPREAD_1(self, row_index):
        ''' Return spread of one record in HISTORY_DATA. '''
    
        spread = abs(float(HISTORY_DATA[row_index][BID_COL_INDEX]) 
             - float(HISTORY_DATA[row_index][ASK_COL_INDEX]))
        
        for i in range(DIGITS):
            spread *= float(10)
        
        return spread
    
#     #===============================================================================
#     def OrdersHistoryTotal(self):
#         ''' Return total number of Closed and Deleted orders. '''
#         
#         return len(self.ORDER_CLOSED_DICT)
#         
#         
#     #===============================================================================
#     def OrdersTotal(self):
#         ''' Return total number of Opened and Pending orders. Return -1 when there is no order'''
#         
#         return len(self.ORDER_OPENED_DICT)
#         
    #===============================================================================
    def OrderType_5(self, order_id, dict_data):
        ''' Return order type of a record in the data. 
            OP_BUY          = 0.00
            OP_SELL         = 1.00
            OP_BUYLIMIT     = 2.00
            OP_SELLLIMIT    = 3.00
            OP_BUYSTOP      = 4.00
            OP_SELLSTOP     = 5.00 '''
    
        if (len(dict_data) != DEFAULT_NUMBER):
            order = dict_data[order_id]
            
            if (order[ORDER_TYPE_COL_INDEX] != "" and float_checker(float(order[ORDER_TYPE_COL_INDEX]))):
                return float(order[ORDER_TYPE_COL_INDEX])
            else:
                print("There is NO type for this order")
                return -1.00
        else:
                print("There is NO data. Data size = 0")
                return -1.00
    
    #===============================================================================
    def OrderDelete_4(self, order_id, dict_data):
        ''' Delete s specific order in data. '''
    
        # delete the order if it's existed in the data
        if (order_id in dict_data):
            del dict_data[order_id]
#             print("Oder %s has been deleted." % order_id)
            return True
        else:
            print("There's NO %s in data. Data is the same as before deleting." % order_id)
            return False
        
    #===============================================================================
    def OrderAdd_10(self, order_id, order, dict_data):
        ''' Add a specific order in data. '''
    
        # add the order if it's NOT existed in the data
        if (order_id in dict_data):
            print("There's the oder %s in data already." % order_id)
            return False
        else:
            # add order to the data
            dict_data[order_id] = order
#             print("Oder %s has been added." % order_id)
            return True
        
    #===============================================================================
    def OrderClose_4(self, order_id, order_type):
        ''' Close a specific old_opended_order in data by:
        * deleting this order in the Opened and Pending orders pool 
        * update the new values for this order from Opened to Close position
        * and save this deleted order in the Closed and Deleted orders pool'''
        
        new_closed_order = self.ORDER_OPENED_DICT[order_id]
        flag_order_closed = False
        entry_price = new_closed_order[PRICE_COL_INDEX]
        exit_price = float(DEFAULT_NUMBER)
        flag_added = False
        
        if (order_type == OP_BUY):
            exit_price = self.bid_price
            
            if (entry_price <= exit_price):
                flag_order_closed = True
            else:
                print("Error closing order OP_BUY %s as: entry_price<=exit_price (%s<=%s)" % (order_id, entry_price, exit_price))
            
        elif (order_type == OP_SELL):
            exit_price = self.ask_price
            
            if (entry_price >= exit_price):
                flag_order_closed = True
            else:
                print("Error closing order OP_SELL %s %s as: entry_price>=exit_price (%s>=%s)" % (order_id, entry_price, exit_price))
            
        else:
            print("This order %s not a BUY or SELL order!" % order_id)
            
        # when the order can be closed
        if (flag_order_closed):
        
            # delete this order in the Opened and Pending orders pool
            flag_deleted = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
            
            if (flag_deleted):
                '''When you go long, you enter the market at the ASK price and exit the market at BID price.
                When you go short, you enter the market at the BID price and exit at the ASK price.'''
                # ORDER_OPENED_DICT[] = ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']
                # update the new values for this order from Opened to Close position
                
                profit = self.CalculateProfit_5(entry_price, exit_price, order_type)
                self.CurrentProfit = self.CurrentProfit + profit
                self.balance = self.balance + profit
                
                new_closed_order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                new_closed_order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                new_closed_order[PROFIT_COL_INDEX] = profit
                new_closed_order[PRICE_COL_INDEX] = exit_price
                new_closed_order[BALANCE_COL_INDEX] = self.balance 
                
                        
                # save this deleted order in the Closed and Deleted orders pool
                flag_added = self.OrderAdd_10(order_id, new_closed_order, self.ORDER_CLOSED_DICT)
                
                if (flag_added == False):
                    print("Error closing order %s as cannot add into Closed and Deleted orders pool." % order_id)
            
            
    #===============================================================================
    def DeletePendingOrder19_3(self):
        ''' Delete an order OP_SELLLIMIT in the Opened and Pending order pool. '''
    
        ''' retry = 10     # SKIP from original EA
        res = False    # SKIP from original EA '''
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_SELLLIMIT
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_SELLLIMIT:
                
                # --> delete this OP_SELLLIMIT in the Opened and Pending orders pool
                order = self.ORDER_OPENED_DICT[order_id]
                flag_deleted = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
               
                if (flag_deleted):
                    # --> update date time and save this deleted OP_SELLLIMIT in the Closed and Deleted orders pool
                    order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    self.OrderAdd_10(order_id, order, self.ORDER_CLOSED_DICT)
        
        ''' 
        # SKIP from original EA
        for (int i=OrdersTotal()-1; i >= 0; i--)
        {
            if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))      
                while(IsTradeContextBusy()) Sleep(100);
                
                while(retry > 0 && !res)
                {
                   res = OrderDelete_4(OrderTicket());
                   retry--;
                   Sleep(500);
                }
                
                if(res == false)
                {
                    Print("OrderDelete_4() error - ", ErrorDescription(GetLastError()));
                }
        '''
        
    #===============================================================================
    def DeletePendingOrder18_3(self):
        ''' Delete an order OP_BUYLIMIT in the Opened and Pending order pool. '''
    
        ''' retry = 10     # SKIP from original EA
        res = False    # SKIP from original EA '''
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_BUYLIMIT
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_BUYLIMIT:
                
                # --> delete this OP_BUYLIMIT in the Opened and Pending orders pool
                order = self.ORDER_OPENED_DICT[order_id]
                flag_deleted = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
               
                if (flag_deleted):
                    # --> update date time and save this deleted OP_BUYLIMIT in the Closed and Deleted orders pool
                    order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    self.OrderAdd_10(order_id, order, self.ORDER_CLOSED_DICT)
        
        ''' 
        # SKIP from original EA
        for (int i=OrdersTotal()-1; i >= 0; i--)
        {
            if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))      
                while(IsTradeContextBusy()) Sleep(100);
        
                while(retry > 0 && !res)
                {
                   res = OrderDelete_4(OrderTicket());
                   retry--;
                   Sleep(500);
                }
                
                if(res == false)
                {
                    Print("OrderDelete_4() error - ", ErrorDescription(GetLastError()));
                }
        '''
            
    #===============================================================================
    def CheckLastOrderType33_4(self):
        ''' Check the last order and delete the pending OP_SELLLIMIT order when the last order was OP_SELL. '''
        
        orderType = -1.00
        lastCloseTime = float(DEFAULT_NUMBER)

        ''' int cnt = OrdersHistoryTotal();  # SKIP from origin EA '''
        
        # get all Closed and Deleted orders in the pool
        # ORDER_CLOSED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_CLOSED_DICT.keys():
            '''  if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;  # SKIP from origin EA '''
            closed_order = self.ORDER_CLOSED_DICT[order_id]
            OrderCloseTime = closed_order[DATE_COL_INDEX]
            
#             order_time = str(closed_order[DATE_COL_INDEX] + "_" + closed_order[TIME_COL_INDEX])
#             OrderCloseTime = convert_string_datetime2float(order_time, MARKET_TIME_STANDARD, DATETIME_FORMAT)
            
            if (lastCloseTime < OrderCloseTime):
                lastCloseTime = OrderCloseTime
                orderType = self.OrderType_5(order_id, self.ORDER_CLOSED_DICT)
        
        # delete the opened OP_SELLLIMIT orders when the last order was OP_SELL
        if (orderType == OP_SELL or self.FirstTime33):
            self.FirstTime33 = False
            self.DeletePendingOrder19_3()
    
    #===============================================================================
    def MathMax_6(self, float_num_1, float_num_2):
        max_number = float(DEFAULT_NUMBER)
    
        if (float_checker(float_num_1) and float_checker(float_num_2)):
            if float_num_1 >= float_num_2:
                max_number = float_num_1
            else:
                max_number = float_num_2
        else:
            print("Either or both of two numbers is not a float number")
                
        return max_number
    
    #===============================================================================
    def NormalizeDouble_9(self, float_num, digit_num):
        
        if (float_checker(float_num)):
            list_normalized_num = str_num = list(str(float_num))
            
            for i in range(len(str_num)):
                if (str_num[i] == '.'):
                    # only normalize when numbers of digit numbers after decimal point matching input digit
                    if (len(str_num) - i > i + digit_num):
                        # get all digits from float number until the expected digit number after decimal point
                        for j in range(i + digit_num):
                            list_normalized_num[j] = str_num[j]
                        
                        # assign the rest of the expected float number
                        k = len(str_num) - DEFAULT_SECOND_NUMBER
                        while (k > i + digit_num):
                            if (digit_num == DEFAULT_NUMBER):
                                list_normalized_num[k] = '0'
                            else:
                                list_normalized_num[k] = '9'
                            k -= DEFAULT_SECOND_NUMBER    
                        
                    break
            
            str_normalized_num = ''.join(list_normalized_num)
            
            return float(str_normalized_num)
        else:
            print("Cannot normalize the number.")
            return float_num
    
    #===============================================================================
    def OrderSend_9(self, order_id, order_type, order_lots, order_price, order_slippage, order_sl, order_tp, order_expire):
        ''' In this EA, this function is to place a Pending order OP_BUYLIMIT or OP_SELLLIMIT. 
        * return False when the order is not a Pending order.
        * order_slippage: Maximum price slippage (for buy or sell orders only). 
        * order_expire: Order expiration time (for pending orders only).'''

        # calculate slippage_in_decimal
        slippage_in_decimal = order_slippage
        for i in range(DIGITS):
            slippage_in_decimal /= float(10)

        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        
        if (order_type != OP_BUYLIMIT and order_type != OP_SELLLIMIT):
            print("This is not a Pending order OP_BUYLIMIT or OP_SELLLIMIT. Its type is %s." % (order_id, order_type))
            return False
        # create a pending order OP_BUYLIMIT or OP_SELLLIMIT
        else:
            if (order_type == OP_BUYLIMIT):
                entry_price = order_price + slippage_in_decimal
                
            elif (order_type == OP_SELLLIMIT):
                entry_price = order_price - slippage_in_decimal
            
            order = [convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT),
                     convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT),
                     OP_BUYLIMIT,
                     order_id,
                     order_lots,
                     round(entry_price, self.NDigits),
                     order_sl,
                     order_tp,
                     float(DEFAULT_NUMBER),
                     float(DEFAULT_NUMBER)]
           
            # save this order in the Opened and Pending orders pool
            flag_added = self.OrderAdd_10(order_id, order, self.ORDER_OPENED_DICT)
            
            if (flag_added):
                return True
            
    #===============================================================================
    def BuyPendingOrder13_8(self):
        ''' Buy Pending Order OP_BUYLIMIT. '''
        
        # exit when reaching maximum orders per day
        if (self.MaxOrders_9(OPENORDERSLIMITDAY)):
            return
        
        # calculate all variables for placing an order
        TimeCurrent = convert_string_datetime2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
        expire = TimeCurrent + MINUTES_OF_ANHOUR * DEFAULT_NUMBER
        
        # assign expire equals 0 for good
        if (0 == 0):
            expire = 0
         
        price = (self.NormalizeDouble_9(self.ask_price, self.NDigits) 
                 + (ARRANGEMENTS_OF_TRADES * self.PipValue) * self.my_point)
        
        # calculate Stop Loss (SL) and Take Profit (TP_
        SL = price - (SINGLEORDERSL * self.PipValue * self.my_point)
        if (SINGLEORDERSL == float(DEFAULT_NUMBER)):
            SL = float(DEFAULT_NUMBER)
        
        TP = price + (SINGLEORDERTP * self.PipValue * self.my_point)
        if (SINGLEORDERTP == float(DEFAULT_NUMBER)):
            TP = float(DEFAULT_NUMBER)
        
           
        # place the pending order OP_BUYLIMIT
        order_id = self.CreateUniqueOrderID_9(OP_BUYLIMIT)
        ticket = self.OrderSend_9(order_id, OP_BUYLIMIT, self.Lots, price, SLIPPAGE, SL, TP, expire)
        
        # inform the result after placing the pending order OP_BUYLIMIT
        if (ticket == False):
            print("OrderSend_9() error for OP_BUYLIMIT %s" % order_id)
#         else:
#             print("Successfully placed the Pending order OP_BUYLIMIT %s." % order_id)
            
    #===============================================================================
    def SellPendingOrder14_8(self):
        ''' Sell Pending Order OP_SELLLIMIT. '''
        
        # exit when reaching maximum orders per day
        if (self.MaxOrders_9(OPENORDERSLIMITDAY)):
            return
        
        # calculate all variables for placing an order
        TimeCurrent = convert_string_datetime2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
        expire = TimeCurrent + MINUTES_OF_ANHOUR * DEFAULT_NUMBER
        
        # assign expire equals 0 for good
        if (0 == 0):
            expire = 0
        
        price = (self.NormalizeDouble_9(self.ask_price, self.NDigits) 
                 - (ARRANGEMENTS_OF_TRADES * self.PipValue) * self.my_point)
        
        # calculate Stop Loss (SL) and Take Profit (TP_
        SL = price + (SINGLEORDERSL * self.PipValue * self.my_point)
        if (SINGLEORDERSL == float(DEFAULT_NUMBER)):
            SL = float(DEFAULT_NUMBER)
        
        TP = price - (SINGLEORDERTP * self.PipValue * self.my_point)
        if (SINGLEORDERTP == float(DEFAULT_NUMBER)):
            TP = float(DEFAULT_NUMBER)
        
        # place the pending order OP_SELLLIMIT
        order_id = self.CreateUniqueOrderID_9(OP_SELLLIMIT)
        ticket = self.OrderSend_9(order_id, OP_SELLLIMIT, self.Lots, price, SLIPPAGE, SL, TP, expire)
        
        # inform the result after placing the pending order OP_SELLLIMIT
        if (ticket == False):
            print("OrderSend_9() error for OP_SELLLIMIT %s" % order_id)
#         else:
#             print("Successfully placed the Pending order OP_SELLLIMIT %s." % order_id)
        
    #===============================================================================
    def IfSellOrderDoesNotExist4_7(self, Mode):
        ''' Check whether the order OP_SELL existed in the Opened and Pending order pool. '''
        exists = False
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_SELL
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_SELL:
                self.SellOrderExists = True
                exists = True
            else:
                self.SellOrderExists = False
                
        if (exists == False and Mode == DEFAULT_SECOND_NUMBER):
            self.BuyPendingOrder13_8()
        
        if (exists == True and Mode == 2):
            self.DeletePendingOrder18_3();
    
    #===============================================================================
    def IfBuyOrderDoesNotExist6_7(self, Mode):
        ''' Check whether the order OP_BUY existed in the Opened and Pending order pool. '''
        exists = False
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_BUY
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_BUY:
                self.BuyOrderExists = True
                exists = True
            else:
                self.BuyOrderExists = False
                
        if (exists == False and Mode == DEFAULT_SECOND_NUMBER):
            self.SellPendingOrder14_8()
        
        if (exists == True and Mode == 2):
            self.DeletePendingOrder19_3();
    
    #===============================================================================
    def IfOrderDoesNotExist11_6(self):
        ''' Check whether the order OP_BUYLIMIT existed in the opned and pending order pool. '''
        exists = False
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_BUYLIMIT
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_BUYLIMIT:
                self.BuyPOExists = True
                exists = True
            else:
                self.BuyPOExists = False
                
        if (exists == False):
            self.IfSellOrderDoesNotExist4_7(1)
        
        if (exists == True):
            self.IfSellOrderDoesNotExist4_7(2);
        
    #===============================================================================
    def IfOrderDoesNotExist12_6(self):
        ''' Check whether the order OP_SELLLIMIT existed in the opned and pending order pool. '''
        exists = False
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_SELLLIMIT
            if self.OrderType_5(order_id, self.ORDER_OPENED_DICT) == OP_SELLLIMIT:
                self.SellPOExists = True
                exists = True
            else:
                self.SellPOExists = False
                
        if (exists == False):
            self.IfBuyOrderDoesNotExist6_7(1)
        
        if (exists == True):
            self.IfBuyOrderDoesNotExist6_7(2);
        
        
    #===============================================================================
    def ATRFilter_5(self):
        ''' ATRFilter_5. '''
        
        atr = [float(DEFAULT_NUMBER) for i in range(int(self.MathMax_6(self.ATRPeriod1, self.ATRPeriod2) + self.ATR_Period))]
        atr_pips = [float(DEFAULT_NUMBER) for i in range(int(self.MathMax_6(self.ATRPeriod1, self.ATRPeriod2) + self.ATR_Period))]
         
        # TODO: Work out the iATR and ATRPips function in Python
#         for i in range(self.MathMax_6(self.ATRPeriod1, self.ATRPeriod2) + self.ATR_Period):
#             # iATR(): Calculates the Average True Range indicator and returns its value.
#             atr[i] = iATR(Symbol(),PERIOD_M15,self.ATR_Period,i)
#          
#         ATRPips(atr, atr_pips, self.MathMax_6(self.ATRPeriod1,self.ATRPeriod2)+self.ATR_Period, self.my_point)
         
        atr_p = atr_pips[DEFAULT_NUMBER]
        ATRPrePips1 = atr_pips[int(self.ATRPeriod1)]
        ATRPrePips2 = atr_pips[int(self.ATRPeriod2)]
         
        if ((((ATRPrePips1 >= self.ATRDnLimit1 and ATRPrePips1 <= self.ATRUpLimit1 and ATRPrePips2 >= self.ATRDnLimit1 and ATRPrePips2 <= self.ATRUpLimit1 and atr_p >= self.ATRDnLimit1 and atr_p <= self.ATRUpLimit1) 
              or (ATRPrePips1 >= self.ATRDnLimit2 and ATRPrePips1 <= self.ATRUpLimit2 and ATRPrePips2 >= self.ATRDnLimit2 and ATRPrePips2 <= self.ATRUpLimit2 and atr_p >= self.ATRDnLimit2 and atr_p <= self.ATRUpLimit2) 
              or (ATRPrePips1 >= self.ATRDnLimit3 and ATRPrePips1 <= self.ATRUpLimit3 and ATRPrePips2 >= self.ATRDnLimit3 and ATRPrePips2 <= self.ATRUpLimit3 and atr_p >= self.ATRDnLimit3 and atr_p <= self.ATRUpLimit3)) 
             and(FILTERING == True)) or (self.SellOrderExists == True) or (self.BuyOrderExists == True)):
     
            ATR = "Not filtering!"
            self.IfOrderDoesNotExist11_6()
            self.IfOrderDoesNotExist12_6()

        # TODO: For testing only 
        elif (ATRPrePips1 == float(DEFAULT_NUMBER) and ATRPrePips2 == float(DEFAULT_NUMBER)):
            ATR = "Not filtering!"
            self.IfOrderDoesNotExist11_6()
            self.IfOrderDoesNotExist12_6()
        
        else:
            ATR = "Filtering!"
            if((self.DeletePOATR == True) and (FILTERING == True)):
                self.DeletePendingOrder18_3()
                self.DeletePendingOrder19_3()
             
            if((self.DeleteOrderATR == True) and (FILTERING == True)):
                self.CloseOrder16_3()
                self.CloseOrder17_3()
        
            
        if (FILTERING == False):
            ATR = ""
            self.IfOrderDoesNotExist11_6()
            self.IfOrderDoesNotExist12_6()
        
    #===============================================================================
    def LimitOpenOrders28_4(self):
        ''' Count all the number in the Opened and Pending order pool. '''
    
        count = DEFAULT_NUMBER
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        
        # TODO: this one for testing only
        if (len(self.ORDER_OPENED_DICT) == DEFAULT_NUMBER):
            self.ATRFilter_5()
        else:
            for i in self.ORDER_OPENED_DICT.keys():
                count += DEFAULT_SECOND_NUMBER
                
                if (count < OPENORDERSLIMIT) or (OPENORDERSLIMIT == DEFAULT_NUMBER):
                    self.ATRFilter_5()
                           
                if (self.SellOrderExists == False) and (self.BuyOrderExists == False):
                    count = DEFAULT_NUMBER
                    self.OrderCounter = count
                else:
                    count = count - DEFAULT_SECOND_NUMBER
                    self.OrderCounter = count
                
            ''' 
            # SKIP from original EA
            if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
            {
                if (OrderSymbol() == Symbol())
                if (OrderMagicNumber() == Magic)
                {
                    count++;
                }
            }
            else
            {
                Print("OrderSend_9() error - ", ErrorDescription(GetLastError()));
            }
            '''
            
                
    #===============================================================================
    def CheckLastOrderType35_4(self):
        ''' Check the last order and delete the pending OP_BUYLIMIT order when the last order was OP_BUY. '''
        
        orderType = -1.00
        lastCloseTime = float(DEFAULT_NUMBER)

        ''' int cnt = OrdersHistoryTotal();  # SKIP from origin EA '''
        
        # get all Closed and Deleted orders in the pool
        # ORDER_CLOSED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_CLOSED_DICT.keys():
            '''  if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;  # SKIP from origin EA '''
            closed_order = self.ORDER_CLOSED_DICT[order_id]
            OrderCloseTime = closed_order[DATE_COL_INDEX]
            
#             order_time = str(closed_order[DATE_COL_INDEX] + "_" + closed_order[TIME_COL_INDEX])
#             OrderCloseTime = convert_string_datetime2float(order_time, MARKET_TIME_STANDARD, DATETIME_FORMAT)
            
            if (lastCloseTime < OrderCloseTime):
                lastCloseTime = OrderCloseTime
                orderType = self.OrderType_5(order_id, self.ORDER_CLOSED_DICT)
        
        # delete the opened OP_BUYLIMIT orders when the last order was OP_BUY
        if (orderType == OP_BUY or self.FirstTime35):
            self.FirstTime35 = False
            self.DeletePendingOrder18_3()
            
    #===============================================================================
    def NewsTime_4(self):
        ''' NewsTime_4. '''
        
        News = False
        PrevMinute = -1
        
        # set default values
        minutesSincePrevEvent = minutesUntilNextEvent = impactOfNextEvent = DEFAULT_NUMBER
        
        ''' && !IsTesting()  # SKIP from original EA'''
        if (self.TimeMinute_3() != PrevMinute):     
            
            PrevMinute = self.TimeMinute_3()
            
#             # iCustom() : Calculates the specified custom indicator and returns its value.
#             # TODO: WORK OUT THE FUNCTION iCustom() for FFCal indicator in Python
#             minutesSincePrevEvent = iCustom(NULL, 0, "FFCal", True, True, False, True, True, 1, 0)
#             minutesUntilNextEvent = iCustom(NULL, 0, "FFCal", True, True, False, True, True, 1, 1)
            
            if ((minutesUntilNextEvent <= MINSBEFORENEWS) or (minutesSincePrevEvent <= MINSAFTERNEWS)):
#                 # TODO: WORK OUT THE FUNCTION iCustom() for FFCal indicator in Python
#                 impactOfNextEvent = iCustom(NULL, 0, "FFCal", True, True, False, True, True, 2, 1)
                
                if (impactOfNextEvent >= NEWSIMPACT): 
                    News = True
        
        return News
        
    #===============================================================================
    def HoursFilter22_3(self):
        ''' HoursFilter22_3. '''
    
        ''' int datetime800 = TimeLocal();    # SKIP from origin EA '''
    
    
        # get the Hour of local time/system time
        hour0 = self.TimeHour_4()
        
        if (self.NewsTime_4() == False 
            and (((self.Hour_of_trading_from < self.Hour_of_trading_to and hour0 >= self.Hour_of_trading_from and hour0 < self.Hour_of_trading_to) 
                  or (self.Hour_of_trading_from > self.Hour_of_trading_to and (hour0 < self.Hour_of_trading_to or hour0 >= self.Hour_of_trading_from))) and (TRADING_24H == False))):
             
            self.Trading = "Trading!"
            if (FILTERSPREAD and self.mode_spread > self.SpreadMax):
                print("Comment: Spread too high! Max spread: %s - Current spread: %s. Date: %s" % (self.SpreadMax, self.mode_spread, self.current_datetime))
                return
 
            self.CheckLastOrderType33_4()
            self.LimitOpenOrders28_4()
            self.CheckLastOrderType35_4()
        else:
            if (TRADING_24H == False) and (self.SellOrderExists == False) and (self.BuyOrderExists == False):
                self.Trading = "Not Trading!"
                self.DeletePendingOrder18_3()
                self.DeletePendingOrder19_3()
            else:
                self.Trading = "Override Hour/Day Filter"
                if  (FILTERSPREAD == True and self.mode_spread > self.SpreadMax):
                    print("Comment: Spread too high! Max spread: %s - Current spread: %s. Date: %s" % (self.SpreadMax, self.mode_spread, self.current_datetime))
                    return
                    
                self.CheckLastOrderType33_4()
                self.LimitOpenOrders28_4()
                self.CheckLastOrderType35_4()
                
        if (TRADING_24H == True):
            if (self.Overide == True):
                self.Trading = "Override Hour/Day Filter"
            else:
                self.Trading = "Trading 24h"
                 
                if (FILTERSPREAD == True) and (self.mode_spread > self.SpreadMax):
                    print("Comment: Spread too high! Max spread: %s - Current spread: %s. Date: %s" % (self.SpreadMax, self.mode_spread, self.current_datetime))
                    return
                 
                self.CheckLastOrderType33_4()
                self.LimitOpenOrders28_4()
                self.CheckLastOrderType35_4()
        
    
    #===============================================================================
    def WeekdayFilter23_2(self):
        ''' WeekdayFilter23_2  '''
    
            
        # (0 - Monday, 1, 2, 3, 4, 5, 6)
        if ((MONDAY and self.DayOfWeek_3() == 0) 
            or (TUESDAY and self.DayOfWeek_3() == 1) 
            or (WEDNESDAY and self.DayOfWeek_3() == 2) 
            or (THURSDAY and self.DayOfWeek_3() == 3) 
            or (FRIDAY and self.DayOfWeek_3() == 4) 
            or (SATURDAY and self.DayOfWeek_3() == 5) 
            or (SUNDAY and self.DayOfWeek_3() == 6)):
            
            self.Overide = False
            self.HoursFilter22_3()
        
        else:
            if (self.SellOrderExists == False) and (self.BuyOrderExists == False):
                self.Trading = "Not Trading!"
                self.DeletePendingOrder18_3()
                self.DeletePendingOrder19_3()
            else:
                self.Overide = True
                self.HoursFilter22_3()
        
#     #===============================================================================
#     def ArrayResize(self, origin_array, new_size):
#         '''  Sets a new size for the first dimension of the list. '''
#     
#         data_col = len(origin_array[DEFAULT_NUMBER])
#         data_row = new_size
#         new_array = [[DEFAULT_NUMBER for x in range(data_col)] for y in range(data_row)]
#         
#         # when new_array is SMALLER than origin_array
#         if new_size < len(origin_array):
#             for x in range(data_row):
#                 for y in range(data_col):
#                     new_array[x][y] = origin_array[x][y]
#         # when new_array is BIGGER than origin_array
#         elif new_size > len(origin_array):
#             
#             # adjust the scope for copy from origin_array to new_array to avoid "list index out of range"
#             data_row = len(origin_array)
#             
#             for x in range(data_row):
#                 for y in range(data_col):
#                     new_array[x][y] = origin_array[x][y]
#         else:
#             return origin_array
#         
#         return new_array
#         
#         
    #===============================================================================
    def CloseOrder17_3(self):
        ''' Close OP_BUY and delete OP_BUYLIMIT in Opened and Pending order pool. '''
    
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            ''' replace for: res = OrderClose_4(OrderTicket(), OrderLots(), OrderClosePrice(), Slippage, Blue);'''
            # when the order is OP_BUY
            order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
            if  (order_type == OP_BUY):
                # --> Close a specific old_opended_order in data by deleting this OP_BUY in the Opened and Pending orders pool 
                # and return new value of order from Opened position to Close position
                self.OrderClose_4(order_id, order_type)
        
        self.DeletePendingOrder18_3()         
        
    #===============================================================================
    def CloseOrder16_3(self):
        ''' Close OP_SELL and delete OP_SELLLIMIT in Opened and Pending order pool. '''
    
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            ''' replace for: res = OrderClose_4(OrderTicket(), OrderLots(), OrderClosePrice(), Slippage, Blue);'''
            # when the order is OP_SELL
            order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
            if  (order_type == OP_SELL):
                # --> Close a specific old_opended_order in data by deleting this OP_SELL in the Opened and Pending orders pool 
                # and return new value of order from Opened position to Close position
                self.OrderClose_4(order_id, order_type)
                
        self.DeletePendingOrder19_3()   
        
    #===============================================================================
    def CloseOrderIf21_2(self):
        ''' Close OP_SELL and delete OP_SELLLIMIT in Opened and Pending order pool. '''
        
        dblProfit = float(DEFAULT_NUMBER)
    
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            order = self.ORDER_OPENED_DICT[order_id]
            OrderProfit = float(order[PROFIT_COL_INDEX])
            dblProfit += OrderProfit
        
        
        if  ((PROFIT and dblProfit >= PROFIT_ALL_ORDERS) 
             or (dblProfit <= AMOUNT_OF_LOSS and SET_UP_OF_LOSS == True) 
             or CLOSING_OF_ALL_TRADES == True):
        
            for order_id in self.ORDER_OPENED_DICT.keys():
                ''' RefreshRates(); # SKIP from origin EA '''
                self.CloseOrder16_3
                self.CloseOrder17_3
                ''' Sleep(100);  # SKIP from origin EA '''
        
    #===============================================================================
    def AtCertainTime6_2(self):
        ''' Return  '''
    
        ''' int datetime800 = TimeLocal();    # SKIP from origin EA '''
    
        # get the Hour of local time/system time
        hour0 = self.TimeHour_4()
        minute0 = self.TimeMinute_3()
        
        if ((self.DayOfWeek_3() != self.Today6 and hour0 > self.Time_of_closing_in_hours and minute0 > self.Time_of_closing_in_minutes) 
            and (self.Time_closing_trades == True) 
            and  self.ProfitCheck_3() > float(DEFAULT_NUMBER)):

            ''' clear = true;    # SKIP from origin EA '''
            self.Today6 = self.DayOfWeek_3();
            self.CloseOrder17_3();
            self.CloseOrder16_3();
        
    #===============================================================================
    def OnEveryTick24_1(self):
        ''' Actions for every tick  '''
        
        self.WeekdayFilter23_2()
        self.AtCertainTime6_2()
        ''' PrintInfoToChart32() # SKIP from origin EA '''
        self.CloseOrderIf21_2()

        
                
    #===============================================================================
    def CloseDeleteAll_1(self):
        ''' Close all orders  '''
        
        flag_close_delete_all = True
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
            
            # when the order is OP_BUY or OP_SELL
            if  (order_type == OP_BUY or order_type == OP_SELL):
                # --> Close a specific old_opended_order in data by deleting this OP_BUY in the Opened and Pending orders pool 
                # and return new value of order from Opened position to Close position
                flag_close_delete_all = self.OrderClose_4(order_id, order_type)
                
                if (flag_close_delete_all == False):
                    return flag_close_delete_all
            
            # when the order is OP_BUYLIMIT or OP_SELLLIMIT
            if  (order_type == OP_BUYLIMIT or order_type == OP_SELLLIMIT):
                
                # --> delete this OP_BUYLIMIT or OP_SELLLIMIT oder in the Opened and Pending orders pool
                order = self.ORDER_OPENED_DICT[order_id]
                flag_close_delete_all = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
               
                # --> update date time and save this deleted OP_BUYLIMIT or OP_SELLLIMIT oder in the Closed and Deleted orders pool
                order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                flag_close_delete_all = self.OrderAdd_10(order_id, order, self.ORDER_CLOSED_DICT)
        
                if (flag_close_delete_all == False):
                    return flag_close_delete_all
        
        return flag_close_delete_all
            
    #===============================================================================
    def UpdateProfit_1(self):
        ''' Update Profit for each Open orders in Opened and Pending orders pool.'''
        
        # get all Opened and Pending orders in the pool
        # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
        for order_id in self.ORDER_OPENED_DICT.keys():
            
            # when the order is OP_BUY or OP_SELL update Profit for each Open orders
            order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
            if  (order_type == OP_BUY or order_type == OP_SELL):
                
                new_closed_order = self.ORDER_OPENED_DICT[order_id]
                entry_price = new_closed_order[PRICE_COL_INDEX]
                exit_price = float(DEFAULT_NUMBER)
                
                # delete this order in the Opened and Pending orders pool
                flag_deleted = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
               
                if (flag_deleted):
                    '''When you go long, you enter the market at the ASK price and exit the market at BID price.
                    When you go short, you enter the market at the BID price and exit at the ASK price.'''
                    # ORDER_OPENED_DICT[] = ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']
                    # update the new values for this order 
                    
                    if  (order_type == OP_BUY):
                        exit_price = self.bid_price
                    
                    elif  (order_type == OP_SELL):
                        exit_price = self.ask_price
                    
                    profit = self.CalculateProfit_5(entry_price, exit_price, order_type)
                    
                    new_closed_order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    new_closed_order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                    new_closed_order[PROFIT_COL_INDEX] = profit
                    new_closed_order[PRICE_COL_INDEX] = exit_price
                            
                    # save back this deleted order in the Opened and Pending orders pool with updated values
                    self.OrderAdd_10(order_id, new_closed_order, self.ORDER_OPENED_DICT)
        
        # update total profit
        self.CurrentProfit = self.ProfitCheck_3()
        
    #===============================================================================
    def CheckEnoughMoney_2(self, order):
        ''' Check if there are enough money in the account for open an order by calculating Equity. '''
    
        # EQUITY = BALANCE + PROFIT
        equity = self.balance + self.CurrentProfit
            
        # MARGIN = ENTRY PRICE * SIZE /LEVERAGE 
        margin = order[PRICE_COL_INDEX] * order[LOTS_COL_INDEX] * ONE_LOT_VALUE / LEVERAGE
        
        # FREE MARGIN = EQUITY - MARGIN
        free_magin = equity - margin
        
        if (free_magin >= margin):
            return True
        else:
            print("There are not enough money in account to open order %s" % order[ORDER_ID_COL_INDEX])
            return False
        
    #===============================================================================
    def ModifyPendingOrder_1(self):
        ''' If there are enough money on the account for opening a pending order, it will be modified into a market one 
        (opened). If not, it will be deleted. '''
        
        flag_added = False
        
        if (self.ords_in_a_day >= OPENORDERSLIMITDAY):
            pass
#             print("Cannot modify this Pending order due to reaching maximum %s orders per day %s." % (OPENORDERSLIMITDAY, self.current_datetime))
        else:
            # get all Opened and Pending orders in the pool
            # ORDER_OPENED_DICT = {order_id: ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']}
            for order_id in self.ORDER_OPENED_DICT.keys():
                
                order_type = self.OrderType_5(order_id, self.ORDER_OPENED_DICT)
               
                # when this order is OP_BUYLIMIT or OP_BUYLIMIT, check if it can be modified to be Open order or not
                if  (order_type == OP_BUYLIMIT or order_type == OP_SELLLIMIT):
                    
                    order = self.ORDER_OPENED_DICT[order_id]
                    entry_price = order[PRICE_COL_INDEX]
                    exit_price = float(DEFAULT_NUMBER)
                    flag_modified = False
                    
                    if (order_type == OP_BUYLIMIT):
                        exit_price = self.bid_price
                        
                        if (entry_price <= exit_price):
                            flag_modified = True
                        else:
                            print("Cannot modify order OP_BUYLIMIT %s." % order_id)
                        
                    elif (order_type == OP_SELLLIMIT):
                        exit_price = self.ask_price
                        
                        if (entry_price >= exit_price):
                            flag_modified = True
                        else:
                            print("Cannot modify order OP_SELLLIMIT %s." % order_id)
                    
                    # this Pending order can be modified
                    if (flag_modified):
                      
                        # check if there is not enough money to open a new order or not
                        flag_enough_money = self.CheckEnoughMoney_2(order)
                        
                        # modified this Pending order to become Open order when having enough money
                        if (flag_enough_money):  
                            
                            # delete this order in the Opened and Pending orders pool
                            flag_deleted = self.OrderDelete_4(order_id, self.ORDER_OPENED_DICT)
                           
                            if (flag_deleted):
                                '''When you go long, you enter the market at the ASK price and exit the market at BID price.
                                When you go short, you enter the market at the BID price and exit at the ASK price.'''
                                # ORDER_OPENED_DICT[] = ['Date', 'Time', 'Type', 'OrderID', 'Size', 'Price', 'SL', 'TP', 'Profit', 'Balance']
                                
                                # update the new type for this Pending order 
                                new_order_type = order_type
                                if (order_type == OP_BUYLIMIT):
                                    new_order_type = OP_BUY
                                    
                                elif (order_type == OP_SELLLIMIT):
                                    new_order_type = OP_SELL
                                    
                                # calculate the new profit   
                                profit = self.CalculateProfit_5(entry_price, exit_price, new_order_type)
                                
                                order[DATE_COL_INDEX] = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                                order[TIME_COL_INDEX] = convert_string_time2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
                                order[ORDER_TYPE_COL_INDEX] = new_order_type
                                order[PRICE_COL_INDEX] = exit_price
                                order[PROFIT_COL_INDEX] = profit
                                        
                                # save back this deleted order in the Opened and Pending orders pool with updated values
                                flag_added = self.OrderAdd_10(order_id, order, self.ORDER_OPENED_DICT)
                                
                                # update the numbers of Open orders per day
                                if (flag_added):
                                    self.ords_in_a_day += DEFAULT_SECOND_NUMBER
                                    if (new_order_type == OP_BUY):
                                        print("Modified the Pending order OP_BUYLIMIT %s to Open order OP_BUY." % order_id)
                                        
                                    elif (new_order_type == OP_SELL):
                                        print("Modified the Pending order OP_SELLLIMIT %s to Open order OP_SELL." % order_id)
                                    
            
    #===============================================================================
    def run(self):
        ''' EA running '''
        
        # save the first day 
        first_day = HISTORY_DATA[DEFAULT_NUMBER][DATE_COL_INDEX] + '_' + HISTORY_DATA[DEFAULT_NUMBER][TIME_COL_INDEX]
        fprevious_date = convert_string_day2float(first_day, MARKET_TIME_STANDARD, DATETIME_FORMAT)
        self.DATE_DATA_DICT[fprevious_date] = HISTORY_DATA[DEFAULT_NUMBER][DATE_COL_INDEX]
        
        for row_index in range(len(HISTORY_DATA)):
#             if (row_index == 10 or row_index == 100 or row_index == 1000 or row_index % 10000 == DEFAULT_NUMBER):
#                     print("==> row_index: %s" % row_index)
                    
            self.current_date = HISTORY_DATA[row_index][DATE_COL_INDEX]
            self.current_time = HISTORY_DATA[row_index][TIME_COL_INDEX]
            self.current_datetime = self.current_date + '_' + self.current_time
            
            self.bid_price = float(HISTORY_DATA[row_index][BID_COL_INDEX])
            self.ask_price = float(HISTORY_DATA[row_index][ASK_COL_INDEX])
            self.mode_spread = self.MODE_SPREAD_1(row_index)
            
            fcurrent_date = convert_string_day2float(self.current_datetime, MARKET_TIME_STANDARD, DATETIME_FORMAT)
            
            # save the previous date when going to a new date 
            if (fprevious_date != fcurrent_date):
                
                # save the old date
                fprevious_date = fcurrent_date
                self.DATE_DATA_DICT[fcurrent_date] = self.current_date
                
                # reset the Maximum open orders per day
                self.ords_in_a_day = DEFAULT_NUMBER
                
                # write out the order history
                write_dict2csv_no_header(happyforex_EA_instance.ORDER_CLOSED_DICT, FOLDER_DATA_OUTPUT + FILENAME_ORDER_CLOSED_HISTORY)
                write_dict2csv_no_header(happyforex_EA_instance.ORDER_OPENED_DICT, FOLDER_DATA_OUTPUT + FILENAME_ORDER_OPENED_HISTORY)
                write_dict2csv_no_header(self.DATE_DATA_DICT, FOLDER_DATA_OUTPUT + "data_date_dict.csv")
                
                print("==> checking date %s" % self.current_date)
                print("==> row_index: %s" % row_index)
                
            # check if reaching maximum orders and delete the pending orders            
            self.MaxOrders_9(OPENORDERSLIMITDAY)
            
    
            if (self.clear):                       
                if (self.CloseDeleteAll_1()):
                    self.clear = False
                else:
                    return
                        
            # check total profit at the moment
            self.CurrentProfit = self.ProfitCheck_3()
            
            # check total balance at the moment
            self.balance = self.AccountBalance_1()  # uzavrete obchody
                
                
            # --> SAFEEQUITYSTOPOUT and AUTOEQUITYMANAGER
            if (SAFEEQUITYSTOPOUT 
                and (SAFEEQUITYRISK / float(100)) * self.balance < self.CurrentProfit * float(-1) 
                and self.CloseDeleteAll_1() == False):
                        self.clear = True
                        return 
            
            if (AUTOEQUITYMANAGER 
                and (EQUITYGAINPERCENT / float(100)) * self.balance < self.CurrentProfit 
                and self.CloseDeleteAll_1() == False):
                        self.clear = True
                        return
            
           
            # TODO: Extra Functions for BackTest: 
            self.UpdateProfit_1()
            self.ModifyPendingOrder_1()
            
            
            self.OnEveryTick24_1()
        
            '''
            # SKIP from original EA
            if (Bars < 10)
            {
                Comment("Not enough bars");
                return (0);
            }
            '''
            
        print("==> Completed!!!")    
                    
        return (self.CurrentProfit)

    #===============================================================================
    def run_nothing(self):
        ''' Randomly create values for NetProfit and TotalWin for testing only '''
    
        self.net_profit = random.randint(DEFAULT_NUMBER, NET_PROFIT)
        
        return (self.CurrentProfit)
    
    
#===============================================================================
happyforex_EA_instance = HappyForexEA()

happyforex_EA_instance.run()
  
# Write out other data for reference
write_array2csv_with_delimiter_no_header(OPTIMIZED_PARAMETERS_DATA, FOLDER_DATA_OUTPUT + FILENAME_OPTIMIZE_PARAMETER, '=')
write_dict2csv_no_header(happyforex_EA_instance.ORDER_CLOSED_DICT, FOLDER_DATA_OUTPUT + FILENAME_ORDER_CLOSED_HISTORY)
write_dict2csv_no_header(happyforex_EA_instance.ORDER_OPENED_DICT, FOLDER_DATA_OUTPUT + FILENAME_ORDER_OPENED_HISTORY)


        
