from enum import Enum

DEFAULT_STAGE = 'development'
STAGES = [DEFAULT_STAGE, 'live']


class Locale(Enum):
    EN_US = 'en-US'
    EN_GB = 'en-GB'
    EN_AU = 'en-AU'
    EN_IN = 'en-IN'
    EN_CA = 'en-CA'
    DE_DE = 'de-DE'
    JA_JP = 'ja-JP'


class Country(Enum):
    US = 'US'
    GB = 'GB'
    DE = 'DE'
    JP = 'JP'


class Marketplace(Enum):
    US = 'amazon.com'
    UK = 'amazon.co.uk'


class Currency:
    USD = 'USD'
    GBP = 'GBP'
    EUR = 'EUR'
    JPY = 'JPY'


LOCALE_BY_COUNTRY = {
    Country.US: Locale.EN_US,
    Country.GB: Locale.EN_GB
}
MARKETPLACE_BY_LOCALE = {
    Locale.EN_US: Marketplace.US,
    Locale.EN_GB: Marketplace.UK,
}
CURRENCY_BY_COUNTRY = {
    Country.US: Currency.USD,
    Country.GB: Currency.GBP
}
ALL_LOCALES = [l for l in Locale]

ISP_ENABLED_LOCALES = [Locale.EN_US, Locale.EN_GB]
