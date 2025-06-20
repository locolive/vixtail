import yfinance as yf
import pandas as pd

# Configurações
symbol = "^VIX"
output_csv = r"E:\GitHub\vixtail\vix_options_dump.csv"

# Inicializa o ticker
vix = yf.Ticker(symbol)
expirations = vix.options

# Lista para armazenar os dados
all_data = []

# Loop por vencimento
for exp in expirations:
    try:
        chain = vix.option_chain(exp)
        for opt_type, df in {'call': chain.calls, 'put': chain.puts}.items():
            for _, row in df.iterrows():
                all_data.append({
                    'expiration': exp,
                    'strike': row['strike'],
                    'option_type': opt_type,
                    'bid': row['bid'],
                    'ask': row['ask'],
                    'last': row['lastPrice'],
                    'volume': row['volume']
                })
    except Exception as e:
        print(f"Erro em {exp}: {e}")

# Salva em CSV
df = pd.DataFrame(all_data)
df.to_csv(output_csv, index=False)
print(f"Arquivo salvo: {output_csv}")
