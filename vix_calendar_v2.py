import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import math

# ---------- CONFIGURAÇÕES PERSONALIZADAS ---------- #
symbol = "^VIX"
strike_range = range(16, 20)  # Altere os strikes conforme necessário
limite_final = "2026-02-28"
spread_limite = 0.30  # Mínimo desejado para marcar verde
# -------------------------------------------------- #

# Inicializa o ticker
vix = yf.Ticker(symbol)

# Lista de vencimentos disponíveis até a data limite
all_expirations = vix.options
valid_expirations = [d for d in all_expirations if d <= limite_final]
labels = [datetime.strptime(d, '%Y-%m-%d').strftime('%b') for d in valid_expirations]

# Cache para evitar múltiplas chamadas
option_data_cache = {}

def fetch_option_data(ticker, expiration, strike, tipo='put'):
    if expiration not in option_data_cache:
        try:
            option_data_cache[expiration] = ticker.option_chain(expiration)
        except:
            return None
    chain = option_data_cache[expiration]
    df = chain.puts if tipo == 'put' else chain.calls
    row = df[df['strike'] == strike]
    if row.empty:
        return None
    bid = row.iloc[0]['bid'] or 0
    ask = row.iloc[0]['ask'] or 0
    last = row.iloc[0]['lastPrice'] or 0
    mid = (bid + ask) / 2 if bid > 0 and ask > 0 else last
    volume = row.iloc[0]['volume'] or 0
    return {'mid': mid, 'last': last, 'bid': bid, 'ask': ask, 'volume': volume}

# Gera a tabela com formatação de cor por célula
for strike in strike_range:
    cell_text = []
    cell_colors = []

    for i in range(len(valid_expirations) - 1):
        row_text = []
        row_colors = []
        venc_venda = valid_expirations[i]
        for j in range(i + 1, len(valid_expirations)):
            venc_compra = valid_expirations[j]

            dados_venda = fetch_option_data(vix, venc_venda, strike, 'put')
            dados_compra = fetch_option_data(vix, venc_compra, strike, 'put')

            if not dados_venda or not dados_compra:
                val = ""
                cor = "white"
            else:
                spread = round(dados_compra['bid'] - dados_venda['ask'], 3)
                val = f"{spread:.2f}"

                # Definindo cores personalizadas
                if spread >= spread_limite and dados_compra['volume'] > 0:
                    cor = "#a0e6a0"  # verde claro
                elif spread >= spread_limite and dados_compra['volume'] == 0:
                    cor = "#fff7a0"  # amarelo claro
                elif spread < 0:
                    cor = "#f5aaaa"  # vermelho claro
                else:
                    cor = "#ffffff"  # branco

            row_text.append(val)
            row_colors.append(cor)

        # Completa a linha com colunas em branco para manter a forma triangular
        padding = len(valid_expirations) - len(row_text) - 1
        row_text += [""] * padding
        row_colors += ["white"] * padding

        cell_text.append(row_text)
        cell_colors.append(row_colors)

    # Plotar como tabela visual
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis("off")
    table = ax.table(cellText=cell_text,
                     cellColours=cell_colors,
                     rowLabels=labels[:-1],
                     colLabels=labels[1:len(labels)],
                     loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    plt.title(f"Calendário VIX - Strike {strike} (BID - ASK Spread)", fontsize=14)
    plt.tight_layout()
    plt.show()
