import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

def mercado_aberto():
    agora = datetime.now(pytz.timezone("US/Eastern"))
    return agora.weekday() < 5 and agora.hour >= 9 and (agora.hour < 16 or (agora.hour == 16 and agora.minute == 0))

vix = yf.Ticker("^VIX")
strikes = list(range(20, 31)) + [35, 40, 45]
vencimentos = [d for d in vix.options if '2026-03' not in d]
market_open = mercado_aberto()

def coletar_opcoes(tipo='call'):
    dados = []
    for venc in vencimentos:
        opt_chain = vix.option_chain(venc)
        opcoes = opt_chain.calls if tipo == 'call' else opt_chain.puts
        for _, row in opcoes.iterrows():
            if int(row['strike']) in strikes:
                if market_open and row['bid'] > 0 and row['ask'] > 0:
                    preco = (row['bid'] + row['ask']) / 2
                else:
                    preco = row['lastPrice']
                dados.append({
                    'vencimento': venc,
                    'strike': int(row['strike']),
                    'preco': preco
                })
    return pd.DataFrame(dados)

# Gráficos
def plotar(df, tipo='CALL'):
    plt.figure(figsize=(14, 6))
    for strike in sorted(df['strike'].unique()):
        sub = df[df['strike'] == strike]
        plt.plot(sub['vencimento'], sub['preco'], marker='o', label=f'Strike {strike}')
    plt.xticks(rotation=45)
    plt.title(f'VIX - Curva de Volatilidade - {tipo}s')
    plt.xlabel('Vencimento')
    plt.ylabel('Preço da Opção')
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

df_calls = coletar_opcoes('call')
plotar(df_calls, 'CALL')

df_puts = coletar_opcoes('put')
plotar(df_puts, 'PUT')
