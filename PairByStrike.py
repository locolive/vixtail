import yfinance as yf
import pandas as pd
from datetime import datetime

def buscar_pares_calendario(strike_alvo=30, tipo='call', dias_minimos=30, dias_min_venda=30):
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

    for venc_curto, venc_longo in pares_validos:
        chain_curta = vix.option_chain(venc_curto)
        chain_longa = vix.option_chain(venc_longo)

        df_curta = chain_curta.calls if tipo == 'call' else chain_curta.puts
        df_longa = chain_longa.calls if tipo == 'call' else chain_longa.puts

        linha_curta = df_curta[df_curta['strike'] == strike_alvo]
        linha_longa = df_longa[df_longa['strike'] == strike_alvo]

        if linha_curta.empty or linha_longa.empty:
            continue

        c = linha_curta.iloc[0]
        l = linha_longa.iloc[0]

        mid_curta = (c['bid'] + c['ask']) / 2 if c['bid'] > 0 and c['ask'] > 0 else None
        mid_longa = (l['bid'] + l['ask']) / 2 if l['bid'] > 0 and l['ask'] > 0 else None

        if mid_curta is None or mid_longa is None:
            continue

        custo = round(mid_longa - mid_curta, 3)
        uts = (datetime.strptime(venc_longo, "%Y-%m-%d") - datetime.strptime(venc_curto, "%Y-%m-%d")).days // 7
        custo_por_UT = round(custo / uts, 3) if uts > 0 else None

        resultados.append({
            'Strike': strike_alvo,
            'Venc. Curto': venc_curto,
            'Venc. Longo': venc_longo,
            'UTs': uts,
            'Mid Curta': round(mid_curta, 3),
            'Mid Longa': round(mid_longa, 3),
            'Custo Líquido': custo,
            '$/UT': custo_por_UT,
            'Tipo': tipo.upper()
        })

    col_order = ['Strike', 'Venc. Curto', 'Venc. Longo', 'UTs', 'Mid Curta', 'Mid Longa', 'Custo Líquido', '$/UT', 'Tipo']
    df = pd.DataFrame(resultados)[col_order]
    return df.sort_values(by='Custo Líquido')

# Exemplo de uso
resultado = buscar_pares_calendario(strike_alvo=15, tipo='put')
print(resultado)
