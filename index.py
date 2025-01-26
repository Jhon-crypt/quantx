from alpaca.trading.client import TradingClient # type: ignore
from alpaca.trading.requests import GetAssetsRequest # type: ignore
from alpaca.trading.enums import AssetClass # type: ignore

trading_client = TradingClient('PKGBYXFOJSX26SUYR9AE', 'eutl7qkvZc2fJjfqxMyCvKN8doB8A4rgfWrF2xFB')

# search for crypto assets
search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO)

assets = trading_client.get_all_assets(search_params)
print(assets)