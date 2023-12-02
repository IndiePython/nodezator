from math import floor
from re import match

REAL_NUM_REGEX = "^[+-]?(?:\d+\.?\d*|\d*\.\d+)$"


class Fraction:
    def __init__(self, numerator=0, denominator=1):
        def handleparams(param):
            p = None
            if isinstance(param, Fraction):
                p = param
            elif isinstance(param, int):
                p = Fraction(param)
            elif isinstance(param, str):
                p = Fraction._getfractionfromstr(param)
            elif isinstance(param, float):
                p = Fraction.fromdecimal(param)
            else:
                raise FractionException("{} is not compatible"
                                        "as a numerator or denominator"
                                        .format(param))
            return p

        x, y = None, None
        if isinstance(numerator, int):
            self.numerator = numerator
        else:
            x = handleparams(numerator)
        if isinstance(denominator, int):
            if denominator == 0:
                raise FractionException("Denominator cannot be 0")
            self.denominator = denominator
        else:
            y = handleparams(denominator)

        z = None
        if x is not None and y is not None:
            z = x / y
        elif y is not None:
            z = Fraction.reciprocal(y) * numerator
        elif x is not None:
            z = x / denominator

        if z is not None:
            self.numerator, self.denominator = z.numerator, z.denominator
        self.is_normal = False

    @staticmethod
    def _getfractionfromstr(num: str):
        f = None
        num = num.strip()
        slashcount = num.count('/')
        if slashcount > 1:
            raise FractionException("Invalid fraction")
        elif slashcount == 1:
            x, y = num.split('/')
            if [bool(match(REAL_NUM_REGEX, x1))
                    for x1 in [x, y]] == [True, True]:
                f = Fraction(x, y)
            else:
                raise FractionException(
                    "Numerator or Denominator is not a number")
        else:
            if bool(match(REAL_NUM_REGEX, num)):
                f = Fraction(float(num))
            else:
                raise FractionException("Invalid number")
        return f

    def _gcd(self, num1, num2):
        if num2 == 0:
            return num1
        return self._gcd(num2, num1 % num2)

    @staticmethod
    def reciprocal(fraction):
        return Fraction(fraction.denominator, fraction.numerator)

    @staticmethod
    def fromdecimal(num, rec=None):
        _snum = str(float(num))
        if rec is not None:
            if not isinstance(rec, str):
                raise FractionException('Recurring part should be a string')
            elif '.' in rec:
                raise FractionException(
                    'Recurring part should not contain decimal places')
            elif not str.isdigit(rec):
                raise FractionException(
                    "Recurring part should only be a number")
            elif rec not in _snum:
                raise FractionException(
                    'Recurring part not present in the number')
            elif not _snum.endswith(rec):
                raise FractionException(
                    "Number should end with the recurring part")

            _pow_tp = _snum.rfind(rec) - _snum.find('.') - 1
            _nummbpowtp = int(num * (10 ** _pow_tp))
            _nummbpowtpreclen = _nummbpowtp * (10 ** (len(rec))) + int(rec)
            return Fraction(_nummbpowtpreclen - _nummbpowtp,
                            10 ** (len(rec) + _pow_tp) - (10 ** _pow_tp))
        else:
            dec_places = len(_snum[_snum.find('.') + 1:])
            return Fraction(int(round(num * (10 ** dec_places))),
                            10 ** dec_places)

    def todecimal(self, decplaces=3):
        if decplaces < 0:
            raise Exception('Number of decimal places cannot be negative')
        elif int(decplaces) != int(floor(decplaces)):
            raise Exception(
                'Number of decimal places cannot be a decimal number')
        return format(self.numerator / self.denominator,
                      '.{}f'.format(decplaces))

    def __add__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        new_numerator = ((denom_lcm / a_d) * a_n) + ((denom_lcm / b_d) * b_n)
        reduced_frac_gcd = self._gcd(new_numerator, denom_lcm)
        return Fraction(new_numerator / reduced_frac_gcd,
                        denom_lcm / reduced_frac_gcd)

    def __sub__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        new_numerator = ((denom_lcm / a_d) * a_n) - ((denom_lcm / b_d) * b_n)
        reduced_frac_gcd = self._gcd(new_numerator, denom_lcm)
        return Fraction(new_numerator / reduced_frac_gcd,
                        denom_lcm / reduced_frac_gcd)

    def __mul__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = a_d * b_d
        new_numerator = a_n * b_n
        reduced_frac_gcd = self._gcd(new_numerator, denom_lcm)
        return Fraction(int(new_numerator / reduced_frac_gcd),
                        int(denom_lcm / reduced_frac_gcd))

    def __div__(self, other_fraction):
        return self.__mul__(Fraction.reciprocal(other_fraction))

    def __truediv__(self, other_fraction):
        return self.__div__(other_fraction)

    def __lt__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        return True if a_n * (denom_lcm / a_d) < b_n * \
            (denom_lcm / b_d) else False

    def __gt__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        return True if a_n * (denom_lcm / a_d) > b_n * \
            (denom_lcm / b_d) else False

    def __le__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        return True if a_n * (denom_lcm / a_d) <= b_n * \
            (denom_lcm / b_d) else False

    def __ge__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        return True if a_n * (denom_lcm / a_d) >= b_n * \
            (denom_lcm / b_d) else False

    def __eq__(self, other_fraction):
        a_n, a_d, b_n, b_d = self.numerator, self.denominator, \
            other_fraction.numerator, other_fraction.denominator
        denom_lcm = (a_d * b_d) / self._gcd(a_d, b_d)
        return True if a_n * (denom_lcm / a_d) == b_n * \
            (denom_lcm / b_d) else False

    def __ne__(self, other_fraction):
        return not self.__eq__(other_fraction)

    def _normalize(self):
        if not self.is_normal:
            g = self._gcd(self.numerator, self.denominator)
            self.numerator = self.numerator // g
            self.denominator = self.denominator // g
            self.is_normal = True

    def __str__(self):
        self._normalize()
        return '{}/{}'.format(self.numerator, self.denominator)

    def __repr__(self):
        self._normalize()
        return 'Fraction({}/{})'.format(self.numerator, self.denominator)


class FractionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
