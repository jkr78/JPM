#!/usr/bin/env python3

from abc import ABC, abstractmethod
from enum import Enum


class StockType(Enum):
    COMMON = 'Common'
    PREFERRED = 'Preferred'


class StockABC(ABC):
    def __init__(self, symbol, last_dividend, fixed_dividend, par_value):
        """Initialise StockABC

        Interface for all Stock objects

        Args:
            symbol: Stock Symbol.
            last_dividend: Last Dividend.
            fixed_dividend: Fixed Dividend.
            par_value: Par Value.
        """
        self.symbol = symbol
        self.last_dividend = last_dividend
        self.fixed_dividend = fixed_dividend
        self.par_value = par_value

    @abstractmethod
    def dividend_yield(self, price):
        pass

    def pe_ratio(self, price):
        """Calculate P/E Ratio for a given Price

        No information is given about rounding rules. So no rounding,
        ceiling or flooring is applied.

        I do not use Decimal for precision since pennies are used as
        currency. And no information is given about precision requirements.

        Args:
            price: Price in pennies

        Returns:
            P/E Ratio or 0 using formula:

            Price / Dividend

            If Dividend happens to be 0 - return 0
        """

        dividend_yield = self.dividend_yield(price)
        if dividend_yield == 0:
            return 0

        return price / dividend_yield


class CommonStock(StockABC):
    def __init__(self, symbol, last_dividend, par_value):
        """Initialise CommonStock

        Args:
            symbol: Stock Symbol.
            last_dividend: Last Dividend.
            par_value: Par Value.
        """

        super().__init__(
            symbol,
            last_dividend=last_dividend,
            fixed_dividend=None,
            par_value=par_value)

    def dividend_yield(self, price):
        """Calculate Dividend Yield for a given Price

        No information is given about rounding rules. So no rounding,
        ceiling or flooring is applied.

        I do not use Decimal for precision since pennies are used as
        currency. And no information is given about precision requirements.

        Args:
            price: Price in pennies

        Returns:
            Dividend Yield using formula:

            Last Dividend / Price

            If price is 0 - dividend yield is 0.
        """

        if price == 0:
            return 0

        return self.last_dividend / price

    def __repr__(self):
        return 'CommonStock({symbol!r}, {last_dividend!r}, ' \
               '{par_value!r})'.format(
                   symbol=self.symbol,
                   last_dividend=self.last_dividend,
                   par_value=self.par_value)


class PreferredStock(StockABC):
    def __init__(self, symbol, last_dividend, fixed_dividend, par_value):
        """Initialise PreferredStock

        Args:
            symbol: Stock Symbol.
            last_dividend: Last dividend
            fixed_dividend: Fixed Dividend.
            par_value: Par Value.
        """

        super().__init__(
            symbol,
            last_dividend=last_dividend,
            fixed_dividend=fixed_dividend,
            par_value=par_value)

    def dividend_yield(self, price):
        """Calculate Dividend Yield for a given Price

        No information is given about rounding rules. So no rounding,
        ceiling or flooring is applied.

        I do not use Decimal for precision since pennies are used as
        currency. And no information is given about precision requirements.

        Args:
            price: Price in pennies

        Returns:
            Dividend Yield using formula:

            (Fixed Dividend * Par Value) / Price

            If Price is 0 - Dividend Yield is 0.
        """

        if price == 0:
            return 0

        # fixed_dividend is in percents, we have to divide by 100
        return (self.fixed_dividend * self.par_value) / (price * 100)

    def __repr__(self):
        return 'PreferredStock({symbol!r}, {last_dividend!r}, ' \
               '{fixed_dividend!r}, {par_value!r})'.format(
                   symbol=self.symbol,
                   last_dividend=self.last_dividend,
                   fixed_dividend=self.fixed_dividend,
                   par_value=self.par_value)


class StockFactory(object):
    """Returns stock object depending on type

    >>> StockFactory(StockType.COMMON, 'TEA', last_dividend=0, par_value=100)
    CommonStock('TEA', 0, 100)

    >>> StockFactory(StockType.PREFERRED, 'GIN', last_dividend=8, fixed_dividend=2, par_value=100)
    PreferredStock('GIN', 8, 2, 100)

    >>> StockFactory('Common', 'POP', last_dividend=8, par_value=100)
    CommonStock('POP', 8, 100)
    """

    stock_types = {
        StockType.COMMON: CommonStock,
        StockType.PREFERRED: PreferredStock,
    }

    def __new__(self, stock_type, *args, **kwargs):
        stock = self.stock_types[StockType(stock_type)](*args, **kwargs)
        return stock


if __name__ == "__main__":
    # no requirements for cui or gui, just run doctests if exist
    import doctest
    doctest.testmod()
