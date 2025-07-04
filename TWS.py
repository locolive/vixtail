from ib_insync import *
import pandas as pd

# Conecta ao TWS ou IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Altere se necessário

# Define o contrato subjacente VIX
underlying = Index(symbol='VIX', exchange='CBOE')

# Consulta os parâmetros das opções
sec_def_params = ib.reqSecDefOptParams(underlying.symbol, '', underlying.secType, 13455763)

# Seleciona o primeiro conjunto de parâmetros disponíveis
params = sec_def_params[0]

# Cria uma lista com os dados combinando cada strike com cada vencimento
rows = []
for expiration in sorted(params.expirations):
    for strike in sorted(params.strikes):
        rows.append({
            'expiration': expiration,
            'strike': strike,
            'exchange': params.exchange,
            'tradingClass': params.tradingClass,
            'multiplier': params.multiplier
        })

# Converte em DataFrame
df = pd.DataFrame(rows)

# Salva como CSV local
df.to_csv('E:/GitHub/vixtail/vix_option_universe.csv', index=False)
print("Arquivo salvo com sucesso em E:/GitHub/vixtail/vix_option_universe.csv")
