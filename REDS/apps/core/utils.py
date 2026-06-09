from decimal import Decimal, ROUND_HALF_UP

# ─────────────────────────────────────────
# AMOUNT IN WORDS — ENGLISH
# ─────────────────────────────────────────

ONES = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
    'Seventeen', 'Eighteen', 'Nineteen'
]

TENS = [
    '', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
    'Sixty', 'Seventy', 'Eighty', 'Ninety'
]


def _below_thousand(n):
    if n == 0:
        return ''
    elif n < 20:
        return ONES[n]
    elif n < 100:
        return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    else:
        rest = _below_thousand(n % 100)
        return ONES[n // 100] + ' Hundred' + (' ' + rest if rest else '')


def amount_in_words(amount):
    try:
        amount = Decimal(str(amount)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        amount = int(amount)
    except (ValueError, TypeError, ArithmeticError):
        return ''

    if amount == 0:
        return 'Zero Rupees Only'

    parts = []

    crore = amount // 10000000
    amount %= 10000000

    lakh = amount // 100000
    amount %= 100000

    thousand = amount // 1000
    amount %= 1000

    hundred = amount

    if crore:
        parts.append(_below_thousand(crore) + ' Crore')
    if lakh:
        parts.append(_below_thousand(lakh) + ' Lakh')
    if thousand:
        parts.append(_below_thousand(thousand) + ' Thousand')
    if hundred:
        parts.append(_below_thousand(hundred))

    return ' '.join(parts) + ' Rupees Only'


# ─────────────────────────────────────────
# AMOUNT IN WORDS — URDU
# ─────────────────────────────────────────

ONES_UR = [
    '', 'ایک', 'دو', 'تین', 'چار', 'پانچ', 'چھ', 'سات', 'آٹھ', 'نو',
    'دس', 'گیارہ', 'بارہ', 'تیرہ', 'چودہ', 'پندرہ', 'سولہ',
    'سترہ', 'اٹھارہ', 'انیس'
]

TENS_UR = [
    '', '', 'بیس', 'تیس', 'چالیس', 'پچاس',
    'ساٹھ', 'ستر', 'اسی', 'نوے'
]


def _below_thousand_ur(n):
    if n == 0:
        return ''
    elif n < 20:
        return ONES_UR[n]
    elif n < 100:
        return TENS_UR[n // 10] + (' ' + ONES_UR[n % 10] if n % 10 != 0 else '')
    else:
        rest = _below_thousand_ur(n % 100)
        return ONES_UR[n // 100] + ' سو' + (' ' + rest if rest else '')


def amount_in_words_urdu(amount):
    try:
        amount = Decimal(str(amount)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        amount = int(amount)
    except (ValueError, TypeError, ArithmeticError):
        return ''

    if amount == 0:
        return 'صفر روپے'

    parts = []

    crore = amount // 10000000
    amount %= 10000000

    lakh = amount // 100000
    amount %= 100000

    thousand = amount // 1000
    amount %= 1000

    hundred = amount

    if crore:
        parts.append(_below_thousand_ur(crore) + ' کروڑ')
    if lakh:
        parts.append(_below_thousand_ur(lakh) + ' لاکھ')
    if thousand:
        parts.append(_below_thousand_ur(thousand) + ' ہزار')
    if hundred:
        parts.append(_below_thousand_ur(hundred))

    return ' '.join(parts) + ' روپے صرف'