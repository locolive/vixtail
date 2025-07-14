from ib_insync import *
import pandas as pd
import seaborn as sns
import math
import os
from datetime import datetime
import logging
from functools import lru_cache
import matplotlib.pyplot as plt

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Conectar à TWS (somente leitura)
ib = IB()
try:
    ib.connect('127.0.0.1', 7497, clientId=999, readonly=True)
except Exception as e:
    logging.error(f"Falha na conexão com TWS: {e}")
    exit(1)

# Configurações
strike_range = range(15, 21)
expirations = [
    '20250715', '20250819', '20250916', '20251021',
    '20251118', '20251216', '20260120',
    '20260217', '20260317'
]
exp_labels = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez', 'Jan', 'Fev', 'Mar']
right = 'P'
exchange = 'CBOE'
output_img_dir = r"E:\GitHub\vixtail\Imagens"
csv_path = r"E:\GitHub\vixtail\vix_spreads_data.csv"

# Garantir que o diretório existe
os.makedirs(output_img_dir, exist_ok=True)

# Cache local para a sessão
@lru_cache(maxsize=128)
def get_bid_ask(strike, expiry):
    try:
        contract = Option('VIX', expiry, strike, right, exchange)
        details = ib.reqContractDetails(contract)
        if not details:
            logging.warning(f"Contrato não encontrado: Strike {strike}, Expiry {expiry}")
            return None, None
        ticker = ib.reqMktData(details[0].contract, '', False, False)
        ib.waitOnUpdate(timeout=2)  # Ajuste dinâmico de espera
        if ticker.bid is None or ticker.ask is None:
            logging.warning(f"Dados ausentes para: Strike {strike}, Expiry {expiry}")
            return None, None
        return ticker.bid, ticker.ask
    except Exception as e:
        logging.error(f"Erro ao buscar cotações para {strike}, {expiry}: {e}")
        return None, None

# Construção das matrizes
matrizes = {}
spread_rows = []
timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                spread_rows.append({
                    'timestamp': timestamp_now,
                    'strike': strike,
                    'venc1': venc1,
                    'venc2': venc2,
                    'bid1': bid1,
                    'ask2': ask2,
                    'spread': spread
                })
    matrizes[strike] = matriz.astype(float)

# Atualizar/gerar o CSV incremental
spread_df = pd.DataFrame(spread_rows)
if os.path.exists(csv_path):
    spread_df.to_csv(csv_path, mode='a', index=False, header=False)
else:
    spread_df.to_csv(csv_path, mode='w', index=False, header=True)

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

# Salvar imagem com data/hora
now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
img_path = os.path.join(output_img_dir, f"TWS-Heatmap_{now_str}.png")
fig.suptitle('Calendários VIX — PUT — Spread (ASK - BID)', fontsize=14)
plt.tight_layout()
plt.savefig(img_path)
print(f"\n✅ Imagem salva em: {img_path}")
plt.show()

# Desconectar
ib.disconnect()