import yfinance as yf
import pandas as pd
from datetime import datetime

def buscar_calendarios_com_credito(strike_range=range(15, 25), tipo='put', metodo_preco='mid', dias_minimos=30, dias_min_venda=30):
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

            def pegar_preco(op):
                if metodo_preco == 'mid':
                    return (op['bid'] + op['ask']) / 2 if op['bid'] > 0 and op['ask'] > 0 else None
                elif metodo_preco == 'last':
                    return op['lastPrice'] if op['lastPrice'] > 0 else None
                return None

            preco_curta = pegar_preco(c)
            preco_longa = pegar_preco(l)

            if preco_curta is None or preco_longa is None:
                continue

            custo = round(preco_longa - preco_curta, 3)
            if custo > 0:
                continue  # só queremos crédito ou zero cost

            uts = (datetime.strptime(venc_longo, "%Y-%m-%d") - datetime.strptime(venc_curto, "%Y-%m-%d")).days // 7
            custo_por_UT = round(custo / uts, 3) if uts > 0 else None

            resultados.append({
                'Strike': strike,
                'Venc. Curto': venc_curto,
                'Venc. Longo': venc_longo,
                'UTs': uts,
                'Preço Curta': round(preco_curta, 3),
                'Preço Longa': round(preco_longa, 3),
                'Crédito Líquido': abs(custo),
                '$/UT': abs(custo_por_UT) if custo_por_UT is not None else None,
                'Tipo': tipo.upper()
            })

    col_order = ['Strike', 'Venc. Curto', 'Venc. Longo', 'UTs', 'Preço Curta', 'Preço Longa', 'Crédito Líquido', '$/UT', 'Tipo']
    df = pd.DataFrame(resultados)[col_order]
    return df.sort_values(by='Crédito Líquido', ascending=False)

# Exemplo de uso:
resultado = buscar_calendarios_com_credito(
    strike_range=range(15, 25),
    tipo='put',
    metodo_preco='last',  # ou 'last' ou 'mid'
    dias_minimos=30,
    dias_min_venda=30
)
print(resultado)
