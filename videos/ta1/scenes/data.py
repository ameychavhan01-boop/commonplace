"""Real market data (TradingView exports in ../data)."""
import json, glob, os, datetime as dt
HERE = os.path.join(os.path.dirname(__file__), '..', 'data')
_cache = {}
def load(prefix, tz=0.0):
    if prefix in _cache: return _cache[prefix]
    fn = sorted(glob.glob(os.path.join(HERE, prefix + '*.json')))[0]
    d = json.load(open(fn))
    d['date'] = [dt.datetime.utcfromtimestamp(t) + dt.timedelta(hours=tz) for t in d['t']]
    d['ds'] = [x.strftime('%Y-%m-%d') for x in d['date']]
    _cache[prefix] = d
    return d
def nifty_d20(): return load('NSE_NIFTY_1D_1577850300', 5.5)
def nifty_d24(): return load('NSE_NIFTY_1D_1714621500', 5.5)
def nifty_w(): return load('NSE_NIFTY_1W', 5.5)
def nifty_m(): return load('NSE_NIFTY_M', 5.5)
def btc_m(): return load('BITSTAMP_BTCUSD_M')
def btc_w(): return load('BITSTAMP_BTCUSD_1W')
def btc_d(): return load('BITSTAMP_BTCUSD_1D')
def idx(d, ds):
    """index of first bar on/after date string"""
    for i, s in enumerate(d['ds']):
        if s >= ds: return i
    return len(d['ds']) - 1
