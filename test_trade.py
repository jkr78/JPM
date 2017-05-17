#!/usr/bin/env python3

import datetime
import unittest
from datetime import timedelta

import stock
import trade


class TestTradeMethods(unittest.TestCase):

    def test_trade(self):
        stock1 = stock.StockFactory(
            'Common',
            'TEST1', last_dividend=8, par_value=100)

        o = trade.Trade(
            stock1,
            datetime.datetime.now(),
            1,
            'Buy',
            2)

        self.assertIsInstance(o, trade.Trade)

        o = trade.Trade(
            stock1,
            datetime.datetime.now(),
            1,
            'Sell',
            2)

        self.assertIsInstance(o, trade.Trade)

        o = trade.Trade(
            stock1,
            datetime.datetime.now(),
            1,
            trade.TradeIndicator.BUY,
            2)

        self.assertIsInstance(o, trade.Trade)

        with self.assertRaises(Exception) as context:
            o = trade.Trade(
                stock1,
                datetime.datetime.now(),
                1,
                '__BAD_INDICATOR__',
                2)
        self.assertTrue(
            'is not a valid TradeIndicator' in str(context.exception))


class TestSimpleTradeListMethods(unittest.TestCase):
    def setUp(self):
        self.stock1 = stock.StockFactory(
            'Common',
            'TEST1', last_dividend=8, par_value=100)

        self.stock2 = stock.PreferredStock(
            'TEST2',
            last_dividend=8,
            fixed_dividend=2,
            par_value=100)

        self.stock3 = stock.CommonStock(
            'TEST3', last_dividend=0, par_value=100)

    def test_volume_weighted_stock_price(self):
        now = datetime.datetime.now()

        stl1 = trade.SimpleTradeList()
        trade1 = trade.Trade(self.stock1, now - timedelta(minutes=3),
                             1, 'Buy', 2)
        stl1.record_trade(trade1)
        trade2 = trade.Trade(self.stock1, now - timedelta(minutes=2),
                             1, 'Buy', 3)
        stl1.record_trade(trade2)
        trade3 = trade.Trade(self.stock1, now - timedelta(minutes=1),
                             1, 'Buy', 4)
        stl1.record_trade(trade3)
        self.assertEqual(
            stl1.volume_weighted_stock_price(self.stock1.symbol, now=now),
            3)

        stl2 = trade.SimpleTradeList()
        trade1 = trade.Trade(self.stock1, now - timedelta(minutes=3),
                             2, 'Buy', 2)
        stl2.record_trade(trade1)
        trade2 = trade.Trade(self.stock1, now - timedelta(minutes=2),
                             3, 'Buy', 5)
        stl2.record_trade(trade2)
        trade3 = trade.Trade(self.stock1, now - timedelta(minutes=1),
                             4, 'Buy', 6)
        stl2.record_trade(trade3)
        self.assertAlmostEqual(
            stl2.volume_weighted_stock_price(self.stock1.symbol, now=now),
            4.77,
            places=1)

        # by default we check last 15 minutes, so stock with price 10
        # must not be calculated in
        stl3 = trade.SimpleTradeList()
        trade1 = trade.Trade(self.stock1, now - timedelta(minutes=20),
                             1, 'Buy', 10)
        stl3.record_trade(trade1)
        trade2 = trade.Trade(self.stock1, now - timedelta(minutes=10),
                             1, 'Buy', 20)
        stl3.record_trade(trade2)
        trade3 = trade.Trade(self.stock1, now - timedelta(minutes=5),
                             1, 'Buy', 30)
        stl3.record_trade(trade3)
        self.assertEqual(
            stl3.volume_weighted_stock_price(self.stock1.symbol, now=now),
            25)

    def test_geometric_mean(self):
        now = datetime.datetime.now()

        stl1 = trade.SimpleTradeList()
        trade1 = trade.Trade(self.stock1, now - timedelta(minutes=2),
                             1, 'Buy', 2)
        stl1.record_trade(trade1)
        trade2 = trade.Trade(self.stock2, now - timedelta(minutes=1),
                             1, 'Buy', 8)
        stl1.record_trade(trade2)
        self.assertEqual(stl1.geometric_mean(), 4)  # 2, 8 = 4

        stl2 = trade.SimpleTradeList()
        trade1 = trade.Trade(self.stock1, now - timedelta(minutes=3),
                             1, 'Buy', 4)
        stl2.record_trade(trade1)
        trade2 = trade.Trade(self.stock2, now - timedelta(minutes=2),
                             1, 'Buy', 1)
        stl2.record_trade(trade2)
        trade3 = trade.Trade(self.stock3, now - timedelta(minutes=1),
                             1, 'Buy', 1 / 32)
        stl2.record_trade(trade3)

        # 4, 1, 1/32 = 1/2
        self.assertAlmostEqual(stl2.geometric_mean(), 1 / 2)


if __name__ == '__main__':
    unittest.main()
