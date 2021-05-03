
import backtrader as bt

# Create a Stratey
class BasicSMATestStrategy(bt.Strategy):

    def log(self, message, dt=None):
        '''
        Log messages
        '''
        timestamp = dt or self.datas[0].datetime.datetime(0)
        print(f'{timestamp}: {message}')


    def __init__(self):
        '''
        Invoked at instatiation. indicators is typically created here
        '''
        #self.data = self.datas[0]
        # To keep track of pending orders
        self.order = None
        self.sma20 = bt.indicators.SMA(self.data.close, period=20)
        self.sma50 = bt.indicators.SMA(self.data.close, period=50)
        

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price}')
            
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        # Write down: no pending order
        self.order = None


    def next(self):
        '''
        Iteration through each data point in the data feed
        '''

        self.log(f' Close: {self.data.close[0]},  SMA20: {self.sma20[0]},  SMA50: {self.sma50[0]}')

        if self.order:
            return

        if not self.position:
            if self.sma20[0] > self.sma50[0] and self.sma20[-1] <= self.sma50[-1]:
                self.log(f'BUY CREATED, {self.data.close[0]}')
                self.order = self.buy()
        
        else:
            if self.sma20[0] < self.sma50[0] and self.sma20[-1] >= self.sma50[-1]:
                self.log(f'SELL CREATED, {self.data.close[0]}')
                self.order = self.sell()
