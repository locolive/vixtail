from ib_insync import *
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

# Conectar à TWS (somente leitura)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=999, readonly=True)

# Configurações
strike_range = range(17, 21)
expirations = [
    '20250819', '20250916', '20251021',
    '20251118', '20251216', '20260120',
    '20260217', '20260317'
]
exp_labels = ['Ago', 'Set', 'Out', 'Nov', 'Dez', 'Jan', 'Fev', 'Mar']
right = 'P'
exchange = 'CBOE'

# Função auxiliar para buscar bid/ask
def get_bid_ask(strike, expiry):
    contract = Option('VIX', expiry, strike, right, exchange)
    details = ib.reqContractDetails(contract)
    if not details:
        return None, None
    ticker = ib.reqMktData(details[0].contract, '', False, False)
    ib.sleep(1)
    return ticker.bid, ticker.ask

# Construção das matrizes
matrizes = {}
total_strikes = len(strike_range)
for idx_strike, strike in enumerate(strike_range, start=1):
    print(f"\n⏳ Processando Strike {strike} ({idx_strike}/{total_strikes})...")
    matriz = pd.DataFrame(index=exp_labels[:-1], columns=exp_labels[1:])
    for i in range(len(expirations) - 1):
        for j in range(i + 1, len(expirations)):
            venc1 = expirations[i]
            venc2 = expirations[j]
            print(f"  - Comparando {venc1} com {venc2}")
            bid1, ask1 = get_bid_ask(strike, venc1)
            bid2, ask2 = get_bid_ask(strike, venc2)
            if bid1 is not None and ask2 is not None:
                spread = round(ask2 - bid1, 2)
                matriz.iloc[i, j - 1] = spread
    matrizes[strike] = matriz.astype(float)

# Plot
cols = math.ceil(math.sqrt(len(matrizes)))
rows = math.ceil(len(matrizes) / cols)
fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
axes = axes.flatten()

for idx, (strike, df) in enumerate(matrizes.items()):
    sns.heatmap(df, annot=True, cmap=sns.diverging_palette(240, 10, as_cmap=True),
                center=0, linewidths=0.5, fmt=".2f", annot_kws={"size": 8}, ax=axes[idx])
    axes[idx].set_title(f'Strike {strike}', fontsize=10)
    axes[idx].tick_params(axis='x', rotation=45, labelsize=8)
    axes[idx].tick_params(axis='y', rotation=0, labelsize=8)

for i in range(len(matrizes), len(axes)):
    fig.delaxes(axes[i])

fig.suptitle('Calendários VIX — PUT — Spread (ASK - BID)', fontsize=14)
plt.tight_layout()
plt.show()

ib.disconnect()
