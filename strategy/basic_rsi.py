
import backtrader as bt

# Create a Stratey
class BasicRSITestStrategy(bt.Strategy):

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
        self.comm = self.broker.getcommissioninfo(self.data).p.commission
        self.hold_size = 0
        self.rsi = bt.indicators.RSI(self.data.close)
        

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'[BUY EXECUTED]  Price: {order.executed.price},  Size: {order.executed.size},  Cost: {order.executed.value},  Comm: {order.executed.comm})')
                self.hold_size = order.executed.size
            elif order.issell():
                self.log(f'[SELL EXECUTED]  Price: {order.executed.price},  Size: {order.executed.size},  Cost: {order.executed.value},  Comm: {order.executed.comm})')
                self.hold_size = 0

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'* [OPERATION PROFIT]  GROSS: {trade.pnl},  NET: {trade.pnlcomm}')

    def next(self):
        '''
        Iteration through each data point in the data feed
        '''
        
        # self.log(f' Close: {self.data.close[0]},  RSI: {self.rsi[0]}')

        if self.order:
            return

        if not self.position:
            if self.rsi[0] < 30:
                size = (self.broker.getcash() - self.broker.getcash() * self.comm) / self.data.close[0]
                self.log(f'[BUY CREATED]  Price: {self.data.close[0]}')
                self.order = self.buy(size=size)
        
        else:
            if self.rsi[0] > 70:
                self.log(f'[SELL CREATED]  Price: {self.data.close[0]}')
                self.order = self.sell(size=self.hold_size)
