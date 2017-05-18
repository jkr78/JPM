#!/usr/bin/env python3

import datetime
import math
from datetime import timedelta
from enum import Enum

from stock import StockABC


class TradeIndicator(Enum):
    BUY = 'Buy'
    SELL = 'Sell'


class Trade(object):
    def __init__(self, stock, timestamp, quantity, indicator, traded_price):
        """Initialise Trade object

        Contains information about stock purchase/sale denoted by indicator
        (Buy/Sell) at specified timestamp. Each purchase/sale contains quantity
        and traded price also.

        Args:
            stock: Stock. Must be an instance of StockABC.
            timestamp: The timestamp of purchase/sale. Must be an instance of
                time, date or datetime.
            quantity: The quantity.
            indicator: purchase/sale idicator as TradeIndicator.
            traded_price: The traded price.
        """

        assert isinstance(stock, StockABC), \
            'stock is not an instance of StockABC'
        assert isinstance(timestamp, (datetime.date, datetime.time)), \
            'timestamp is not an instance of date, time or datetime'

        self.stock = stock
        self.timestamp = timestamp
        self.quantity = quantity
        self.indicator = TradeIndicator(indicator)
        self.traded_price = traded_price

    def __repr__(self):
        return 'Trade({stock!r}, {timestamp!r}, {quantity!r}, ' \
               '{indicator!r}, {traded_price!r})'.format(
                   stock=self.stock,
                   timestamp=self.timestamp,
                   quantity=self.quantity,
                   indicator=self.indicator,
                   traded_price=self.traded_price)


class SimpleTradeList(object):
    """This is the simple Trade record list

    This trade list expects that all records are added in
    already sorted order (by timestamp). Though more than one
    trade symbol is allowed per same timestamp.

    I have implemented this List in very simple way. Though it contains some
    performance enhancments it is far from good.
    For real trade app Red-Black/AVL (depending on the needs) or other
    specialised data structure may be used.
    """

    def __init__(self):
        """Initialise Empty Simple Trade List

        The trade is stored as dict, where key is trade symbol and value is
        list of trades in sorted order. Empty Simple Trade List does not
        sort or in other way change the order on appended trades. User must
        make sure to add trades in correct order (though I could use bisect to
        this, but it would require another list or implement comparision in
        Trade on timestamp).

        traded_price_count contains number of total trades per all symbols it
        total_traded_price_log contains precompiled log for all traded prices
            I will use first sum(log()), then exp(1/n) to make sure not
            overflow then multiplying prices
        """

        self.records = {}

        self.traded_price_count = 0
        self.total_traded_price = 0
        self.total_traded_price_log = 0
        self.last_timestamp = None

    def record_trade(self, trade):
        assert isinstance(trade, Trade), \
            'trade is not an instance of Trade: {}'.format(trade)

        stock_symbol = trade.stock.symbol
        trade_list = self.records.setdefault(stock_symbol, [])

        assert (len(trade_list) == 0 or
                trade_list[-1].timestamp <= trade.timestamp), \
            'trade.timestamp is not in order for {}: {}'.format(
                stock_symbol, trade)

        trade_list.append(trade)

        self.traded_price_count += 1
        self.total_traded_price += trade.traded_price
        self.total_traded_price_log += math.log(trade.traded_price)

        if self.last_timestamp is None:
            self.last_timestamp = trade.timestamp
        else:
            self.last_timestamp = max(self.last_timestamp, trade.timestamp)

    def get_last_timestamp(self, stock_symbol=None):
        """Last stored timestamp

        Args:
            stock_symbol: if specified returns last timestamp for this stock
        """
        if stock_symbol is None:
            return self.last_timestamp

        trades = self.records.get(stock_symbol)
        if not trades:
            return None

        return trades[-1].timestamp

    def geometric_mean(self):
        """Calculate Geometric Mean for all stocks

        Returns:
            Geometric mean of all stock traded prices
        """

        if self.traded_price_count < 1:
            return 0

        # idea based on: http://stackoverflow.com/a/43099751
        # but i am not using numpy and precalculating log(traded_price)
        r = math.exp(self.total_traded_price_log / self.traded_price_count)
        return r

    def volume_weighted_stock_price(self, stock_symbol,
                                    now=None,
                                    trade_timedelta=timedelta(minutes=15)):
        """Calculate Volume Weighted Stock Price based on trades

        Args:
            stock_symbol: Stock Symbol to calculate for.
            now: timestamp to start calculation from.
            trade_timedelta: timedelta denoting how much trades to calc.

        Returns:
            Volume Weighted Stock Price

        If now is not specified (or is None) we will use current PC timestamp.
        To get last stored timestamp use get_last_timestamp() function
        """

        trades = self.records.get(stock_symbol)
        if not trades:
            return 0  # not found

        total_traded = 0
        total_quantity = 0

        if now is None:
            # for the last timestamp in records use: now = trades[-1].timestamp
            now = datetime.datetime.now()

        for i in range(len(trades) - 1, -1, -1):  # lets go back in time
            if now - trade_timedelta > trades[i].timestamp:
                break
            total_traded += (trades[i].traded_price * trades[i].quantity)
            total_quantity += trades[i].quantity

        if total_quantity == 0:
            return 0

        return total_traded / total_quantity


if __name__ == "__main__":
    # no requirements for cui or gui, just run doctests if exist
    import doctest
    doctest.testmod()    
