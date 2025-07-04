from ib_insync import *

def safe_req_mkt_data(ib, contract):
    try:
        ticker = ib.reqMktData(contract, '', snapshot=False, regulatorySnapshot=False)
        ib.sleep(2)
        return ticker.bid, ticker.ask
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados: {e}")
        return None, None

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1, readonly=True)

contract = Option('VIX', '20250715', 20, 'P', 'CBOE')
details = ib.reqContractDetails(contract)
bid, ask = safe_req_mkt_data(ib, details[0].contract)

print(f"BID: {bid}, ASK: {ask}")
ib.disconnect()
