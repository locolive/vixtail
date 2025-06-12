import yfinance as yf
import pandas as pd
from datetime import datetime

def buscar_spreads_credito(strike_range=range(15, 25), tipo='put', dias_minimos=30, dias_min_venda=30):
    vix = yf.Ticker("^VIX")
    expirations = vix.options
    hoje = datetime.today()

    datas = [datetime.strptime(v, "%Y-%m-%d") for v in expirations]
    datas_validas = [d for d in datas if (d - hoje).days >= dias_min_venda]

    pares_validos = []
    for i, d1 in enumerate(datas_validas):
        for d2 in datas_validas[i+1:]:
            if (d2 - d1).days >= dias_minimos:
                pares_validos.append((d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")))

    resultados = []

    for strike in strike_range:
        for venc_curto, venc_longo in pares_validos:
            chain_curta = vix.option_chain(venc_curto)
            chain_longa = vix.option_chain(venc_longo)

            df_curta = chain_curta.calls if tipo == 'call' else chain_curta.puts
            df_longa = chain_longa.calls if tipo == 'call' else chain_longa.puts

            linha_curta = df_curta[df_curta['strike'] == strike]
            linha_longa = df_longa[df_longa['strike'] == strike]

            if linha_curta.empty or linha_longa.empty:
                continue

            c = linha_curta.iloc[0]
            l = linha_longa.iloc[0]

            bid_c, ask_c, last_c = c['bid'], c['ask'], c['lastPrice']
            bid_l, ask_l, last_l = l['bid'], l['ask'], l['lastPrice']

            mid_c = (bid_c + ask_c) / 2 if bid_c > 0 and ask_c > 0 else None
            mid_l = (bid_l + ask_l) / 2 if bid_l > 0 and ask_l > 0 else None

            valor_mid = round(mid_l - mid_c, 3) if mid_c and mid_l else None
            valor_last = round(last_l - last_c, 3) if last_l and last_c else None

            spread_c = ask_c - bid_c if ask_c > 0 and bid_c > 0 else None
            spread_l = ask_l - bid_l if ask_l > 0 and bid_l > 0 else None
            spread_medio = round((spread_c + spread_l) / 2, 3) if spread_c and spread_l else None

            if (valor_mid is not None and valor_mid <= 0) or (valor_last is not None and valor_last <= 0):
                resultados.append({
                    'Strike': strike,
                    'Venc. Curto': venc_curto,
                    'Venc. Longo': venc_longo,
                #    'Bid Curta': bid_c,
                #    'Ask Curta': ask_c,
                #    'Last Curta': last_c,
                #    'Bid Longa': bid_l,
                #    'Ask Longa': ask_l,
                #    'Last Longa': last_l,
                    'Valor (Mid)': valor_mid,
                    'Valor (Last)': valor_last,
                    'Spread Médio': spread_medio,
                    'Tipo': tipo.upper()
                })

    col_order = [
        'Strike', 'Venc. Curto', 'Venc. Longo',
    #    'Bid Curta', 'Ask Curta', 'Last Curta',
    #    'Bid Longa', 'Ask Longa', 'Last Longa',
        'Valor (Mid)', 'Valor (Last)', 'Spread Médio', 'Tipo'
    ]
    df = pd.DataFrame(resultados)[col_order]
    return df.sort_values(by='Valor (Mid)', ascending=True)

# Exemplo de uso
resultado = buscar_spreads_credito(strike_range=range(15, 21), tipo='put')
print(resultado)
