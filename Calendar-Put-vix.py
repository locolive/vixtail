import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# ---------- CONFIG ---------- #
symbol = "^VIX"
strike_range = range(14, 22)
limite_final = "2026-02-28"
# ---------------------------- #

# Retorna a 3ª quarta-feira do mês
def terceira_quarta(data_str):
    y, m = int(data_str[:4]), int(data_str[5:7])
    count = 0
    for d in range(1, 32):
        try:
            dia = datetime(y, m, d)
            if dia.weekday() == 2:  # 0 = segunda ... 2 = quarta
                count += 1
                if count == 3:
                    return dia.strftime('%Y-%m-%d')
        except:
            continue
    return None

# Função para buscar dados de PUT
def fetch_option_data(ticker, expiration, strike):
    try:
        chain = ticker.option_chain(expiration)
        df = chain.puts
        row = df[df['strike'] == strike]
        if not row.empty:
            bid = row.iloc[0]['bid'] or 0
            ask = row.iloc[0]['ask'] or 0
            last = row.iloc[0]['lastPrice'] or 0
            mid = (bid + ask) / 2 if bid > 0 and ask > 0 else last
            return round(mid, 3), round(last, 3)
    except:
        pass
    return None, None

# Coleta todos os vencimentos e filtra apenas os mensais
vix = yf.Ticker(symbol)
all_expirations = vix.options
valid_expirations = [
    d for d in all_expirations
    if d <= limite_final and d == terceira_quarta(d)
]

# Monta os spreads de calendário (MID)
spread_mid_data = []

for strike in strike_range:
    row = {}
    for i in range(len(valid_expirations) - 1):
        exp1 = valid_expirations[i]
        exp2 = valid_expirations[i + 1]
        mid1, _ = fetch_option_data(vix, exp1, strike)
        mid2, _ = fetch_option_data(vix, exp2, strike)
        col = f'{exp1[-5:]}→{exp2[-5:]}'
        if None not in (mid1, mid2):
            row[col] = round(mid2 - mid1, 3)
        else:
            row[col] = None
    spread_mid_data.append(row)

# Gera DataFrame com strikes como índice
df_heatmap = pd.DataFrame(spread_mid_data, index=[f'Strike {s}' for s in strike_range])

# Plota Heatmap
plt.figure(figsize=(14, 6))
sns.heatmap(df_heatmap, annot=True, cmap="coolwarm", center=0, linewidths=0.5, fmt=".2f")
plt.title("Calendários VIX (PUTs MID) — Vencimentos Mensais", fontsize=14)
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
