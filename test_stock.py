#!/usr/bin/env python3

import random
import sys
import unittest

import stock


class TestStockFactory(unittest.TestCase):

    def test_factory(self):
        with self.assertRaises(Exception) as context:
            o = stock.StockFactory(
                '_',
                '_', last_dividend=8, fixed_dividend=2, par_value=10)
        self.assertTrue('is not a valid StockType' in str(context.exception))

        o = stock.StockFactory(
            'Common',
            'POP', last_dividend=8, par_value=100)

        self.assertIsInstance(o, stock.CommonStock)

        o = stock.StockFactory(
            stock.StockType.COMMON,
            'TEA', last_dividend=0, par_value=100)

        self.assertIsInstance(o, stock.CommonStock)

        o = stock.StockFactory(
            stock.StockType.PREFERRED,
            'GIN', last_dividend=8, fixed_dividend=2, par_value=10)

        self.assertIsInstance(o, stock.PreferredStock)

        o = stock.StockFactory(
            'Preferred',
            'GIN', last_dividend=8, fixed_dividend=2, par_value=10)

        self.assertIsInstance(o, stock.PreferredStock)


class TestStockMethods(unittest.TestCase):

    def test_common_stock_dividend_yield(self):
        o = stock.CommonStock(
            'TEST',
            last_dividend=0,
            par_value=0)
        self.assertEqual(o.dividend_yield(0), 0)
        self.assertEqual(o.dividend_yield(1), 0)
        self.assertEqual(o.dividend_yield(-1), 0)
        self.assertEqual(o.dividend_yield(sys.maxsize), 0)
        self.assertEqual(o.dividend_yield(-sys.maxsize), 0)

        x = random.randint(0, sys.maxsize)
        self.assertEqual(o.dividend_yield(x), 0)

        x = random.randint(-sys.maxsize, 0)
        self.assertEqual(o.dividend_yield(x), 0)

        x = random.randint(-sys.maxsize, sys.maxsize)
        self.assertEqual(o.dividend_yield(x), 0)

        o = stock.CommonStock(
            'TEST',
            last_dividend=120,
            par_value=0)

        self.assertEqual(o.dividend_yield(0), 0)
        self.assertEqual(o.dividend_yield(1), 120)  # 120 / 120
        self.assertEqual(o.dividend_yield(2), 60)  # 120 / 2
        self.assertEqual(o.dividend_yield(3), 40)  # 120 / 2
        self.assertEqual(o.dividend_yield(120), 1)  # 120 / 120

    def test_preferred_stock_dividend_yield(self):
        o = stock.PreferredStock(
            'TEST',
            last_dividend=8,
            fixed_dividend=2,
            par_value=100)

        self.assertEqual(o.dividend_yield(0), 0)
        self.assertEqual(o.dividend_yield(1), 2)  # 2% * 100 / 1
        self.assertEqual(o.dividend_yield(2), 1)  # 2% * 100 / 2

    def test_pe_ratio(self):
        o = stock.CommonStock(
            'TEST',
            last_dividend=120,
            par_value=0)

        self.assertEqual(o.pe_ratio(0), 0)
        self.assertEqual(o.pe_ratio(1), 1 / 120)  # 120 / 1 = 120; 1 / 120
        self.assertAlmostEqual(o.pe_ratio(2), 2 / 60)  # 120 / 2 = 60; 2 / 60
        self.assertEqual(o.pe_ratio(60), 30)  # 120 / 60 = 2; 60 / 2 = 30
        self.assertEqual(o.pe_ratio(120), 120)  # 120 / 120 = 1; 120 / 1 = 120


if __name__ == '__main__':
    unittest.main()
