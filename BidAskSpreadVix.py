import yfinance as yf
import pandas as pd
from datetime import datetime

# Configurações
symbol = "^VIX"
strikes = list(range(14, 23))  # Strike 14 a 22
max_spread = 0.05  # tolerância para ZCC

vix = yf.Ticker(symbol)
expirations = vix.options

# Filtrar vencimentos com mais de 30 dias
valid_exps = []
for exp in expirations:
    exp_date = datetime.strptime(exp, "%Y-%m-%d")
    if (exp_date - datetime.now()).days > 30:
        valid_exps.append(exp)

if len(valid_exps) < 2:
    print("Não há vencimentos suficientes com mais de 30 dias.")
    exit()

# Pega o 1º e 2º vencimentos válidos
exp_curta, exp_longa = valid_exps[0], valid_exps[1]

# Obtem cadeias
chain_curta = vix.option_chain(exp_curta)
chain_longa = vix.option_chain(exp_longa)

resultados = []

for strike in strikes:
    put_curta = chain_curta.puts[chain_curta.puts['strike'] == strike]
    put_longa = chain_longa.puts[chain_longa.puts['strike'] == strike]

    if not put_curta.empty and not put_longa.empty:
        ask_curta = put_curta['ask'].values[0]
        bid_longa = put_longa['bid'].values[0]
        spread_zcc = round(ask_curta - bid_longa, 3)

        if abs(spread_zcc) <= max_spread:
            resultados.append({
                "Strike": strike,
                "Venc_Curta": exp_curta,
                "Ask_Curta": ask_curta,
                "Venc_Longa": exp_longa,
                "Bid_Longa": bid_longa,
                "Spread_ZCC": spread_zcc
            })

df = pd.DataFrame(resultados)

# Saída
print("\n=== Candidatos a ZCC (Zero Cost Calendar) ===")
if df.empty:
    print("Nenhum par com spread dentro do critério.")
else:
    print(df.sort_values(by="Spread_ZCC").to_string(index=False))
