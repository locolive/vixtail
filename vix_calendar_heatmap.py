import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import math
import calendar

# ---------- CONFIGURAÇÕES PERSONALIZADAS PELO USUÁRIO ---------- #
symbol = "^VIX"
strike_range = range(17, 23)  # Altere aqui o range de strikes
valor_tipo = 3  # 1 = MID, 2 = LAST, 3 = BID (vendido) - ASK (comprado)
tipo_opcao = 'put'  # 'put' ou 'call'
limite_final = "2026-02-28"
# ---------------------------------------------------------------- #

# Função para obter a terceira quarta-feira do mês
def terceira_quarta(data_str):
    y, m = int(data_str[:4]), int(data_str[5:7])
    cal = calendar.Calendar()
    wednesdays = [day for day in cal.itermonthdays2(y, m) if day[0] != 0 and day[1] == 2]
    if len(wednesdays) >= 3:
        dia = wednesdays[2][0]
        return f"{y}-{m:02d}-{dia:02d}"
    return None

# Cache de dados
option_data_cache = {}

# Função otimizada com cache
def fetch_option_data(ticker, expiration, strike, tipo='put'):
    if expiration not in option_data_cache:
        try:
            option_data_cache[expiration] = ticker.option_chain(expiration)
        except:
            return None
    chain = option_data_cache[expiration]
    df = chain.puts if tipo == 'put' else chain.calls
    row = df[df['strike'] == strike]
    if not row.empty:
        bid = row.iloc[0]['bid'] or 0
        ask = row.iloc[0]['ask'] or 0
        last = row.iloc[0]['lastPrice'] or 0
        mid = (bid + ask) / 2 if bid > 0 and ask > 0 else last
        return {'mid': mid, 'last': last, 'bid': bid, 'ask': ask}
    return None

# Coleta vencimentos válidos
vix = yf.Ticker(symbol)
all_expirations = vix.options
hoje = datetime.today()

valid_expirations = [
    d for d in all_expirations
    if d <= limite_final and (datetime.strptime(d, "%Y-%m-%d") - hoje).days >= 30
]

labels = [datetime.strptime(d, '%Y-%m-%d').strftime('%b') for d in valid_expirations]

# Valor do VIX spot
vix_spot = round(yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1], 2)

# Gera matrizes para cada strike
matrizes = {}
for strike in strike_range:
    matriz = pd.DataFrame(index=labels[:-1], columns=labels[1:])
    for i in range(len(valid_expirations) - 1):
        for j in range(i + 1, len(valid_expirations)):
            venc_venda = valid_expirations[i]
            venc_compra = valid_expirations[j]
            dados_venda = fetch_option_data(vix, venc_venda, strike, tipo_opcao)
            dados_compra = fetch_option_data(vix, venc_compra, strike, tipo_opcao)
            if dados_venda and dados_compra:
                if valor_tipo == 1:
                    spread = round(dados_compra['mid'] - dados_venda['mid'], 3)
                elif valor_tipo == 2:
                    spread = round(dados_compra['last'] - dados_venda['last'], 3)
                elif valor_tipo == 3:
                    spread = round(dados_compra['ask'] - dados_venda['bid'], 3)
                else:
                    spread = None
                matriz.iloc[i, j - 1] = spread
            else:
                matriz.iloc[i, j - 1] = None
    matrizes[strike] = matriz.astype(float)

# Plot
num_strikes = len(strike_range)
cols = math.ceil(math.sqrt(num_strikes))
rows = math.ceil(num_strikes / cols)

fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
axes = axes.flatten()

for idx, (strike, df) in enumerate(matrizes.items()):
    sns.heatmap(df, annot=True, cmap=sns.diverging_palette(240, 10, as_cmap=True), center=0, linewidths=0.5, fmt=".2f",
                annot_kws={"size": 8}, ax=axes[idx])
    axes[idx].set_title(f'Strike {strike}', fontsize=10)
    axes[idx].tick_params(axis='x', rotation=45, labelsize=8)
    axes[idx].tick_params(axis='y', rotation=0, labelsize=8)

# Remove subplots extras
for i in range(len(matrizes), len(axes)):
    fig.delaxes(axes[i])

# Título geral com VIX e tipo de spread
spread_label = {1: "MID", 2: "LAST", 3: "ASK - BID"}[valor_tipo]
fig.suptitle(f'Calendários VIX — {tipo_opcao.upper()} — Spread ({spread_label}) — VIX Spot: {vix_spot}', fontsize=14)
plt.tight_layout()
plt.show()
