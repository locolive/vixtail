import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import math
import calendar

# ---------- CONFIGURAÇÕES PERSONALIZADAS PELO USUÁRIO ---------- #
symbol = "^VIX"
strike_range = range(16, 20)  # Altere aqui o range de strikes
valor_tipo = 3  # 1 = MID, 2 = LAST, 3 = BID (vendido) - ASK (comprado)
tipo_opcao = 'put'  # 'put' ou 'call'
limite_final = "2026-02-28"
# ---------------------------------------------------------------- #

# Função para obter a terceira quarta-feira do mês


def terceira_quarta(data_str):
    """Retorna a data da terceira quarta-feira do mês no formato yyyy-mm-dd."""
    y, m = int(data_str[:4]), int(data_str[5:7])
    cal = calendar.Calendar()
    wednesdays = [day for day in cal.itermonthdays2(y, m) if day[0] != 0 and day[1] == 2]
    if len(wednesdays) >= 3:
        dia = wednesdays[2][0]
        return f"{y}-{m:02d}-{dia:02d}"
    return None


# ---------- CACHE de dados ----------
option_data_cache = {}

# Função otimizada com cache de option_chain
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

# Coleta vencimentos mensais válidos
vix = yf.Ticker(symbol)
all_expirations = vix.options
valid_expirations = [
    d for d in all_expirations
    if d <= limite_final
]

labels = [datetime.strptime(d, '%Y-%m-%d').strftime('%b') for d in valid_expirations]

# Gera matriz para cada strike: vendida (linha), comprada (coluna)
matrizes = {}
for strike in strike_range:
    matriz = pd.DataFrame(index=labels[:-1], columns=labels[1:])
    for i in range(len(valid_expirations) - 1):  # linha = vencimento vendido
        for j in range(i + 1, len(valid_expirations)):  # coluna = vencimento comprado
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

# Plotagem dos heatmaps
num_strikes = len(strike_range)
cols = math.ceil(math.sqrt(num_strikes))
rows = math.ceil(num_strikes / cols)

fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.5, rows * 3.5))
axes = axes.flatten()

for idx, (strike, df) in enumerate(matrizes.items()):
    sns.heatmap(df, annot=True, cmap="coolwarm", center=0, linewidths=0.5, fmt=".2f", ax=axes[idx])
    axes[idx].set_title(f'Strike {strike}')
    axes[idx].tick_params(axis='x', rotation=45)
    axes[idx].tick_params(axis='y', rotation=0)

# Esconde subplots vazios
for i in range(len(matrizes), len(axes)):
    fig.delaxes(axes[i])

fig.suptitle(f'Calendários VIX — {tipo_opcao.upper()} — Spread Tipo {valor_tipo}', fontsize=16)
plt.tight_layout()
plt.show()
