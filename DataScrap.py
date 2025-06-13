import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# Início da contagem de tempo
start = time.time()

# Ticker VIX
ticker = yf.Ticker("^VIX")

# Lista de vencimentos disponíveis
expirations = ticker.options

# Lista para armazenar os dados
all_data = []

for exp in expirations:
    try:
        chain = ticker.option_chain(exp)
    except Exception as e:
        print(f"Erro ao puxar vencimento {exp}: {e}")
        continue

    for opt_type, options in [('CALL', chain.calls), ('PUT', chain.puts)]:
        for _, row in options.iterrows():
            bid = row['bid']
            ask = row['ask']
            mid = (bid + ask) / 2 if pd.notna(bid) and pd.notna(ask) else None
            spread = (ask - bid) if pd.notna(bid) and pd.notna(ask) else None

            all_data.append({
                'Timestamp': datetime.now(),
                'Type': opt_type,
                'Strike': row['strike'],
                'Expiration': exp,
                'Bid': bid,
                'Ask': ask,
                'LastPrice': row['lastPrice'],
                'IV': row['impliedVolatility'],
                'Volume': row['volume'],
                'OpenInterest': row['openInterest'],
                'InTheMoney': row['inTheMoney'],
                'MID': mid,
                'Spread': spread
            })

# Converter para DataFrame
df = pd.DataFrame(all_data)

# Caminho de salvamento
output_path = r"E:\GitHub\vixtail\opcoes_vix.csv"
df.to_csv(output_path, index=False)

# Tempo total de execução
end = time.time()
print(f"\nTotal de opções coletadas: {len(df)}")
print(f"Tempo total de execução: {end - start:.2f} segundos")
print(f"Arquivo salvo em: {output_path}")
