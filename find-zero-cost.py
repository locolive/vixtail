import yfinance as yf
import pandas as pd
from datetime import datetime

def buscar_zero_cost_vix_formatado(strike_range=range(15, 50), limite_debito=0.15, dias_minimos=30, dias_min_venda=30):
    vix = yf.Ticker("^VIX")
    expirations = vix.options
    hoje = datetime.today()

    # Converter vencimentos para datetime
    datas = [datetime.strptime(v, "%Y-%m-%d") for v in expirations]
    datas_validas = [d for d in datas if (d - hoje).days >= dias_min_venda]

    # Criar pares com pelo menos 'dias_minimos' entre si
    venc_pairs = []
    for i, venc1 in enumerate(datas_validas):
        for venc2 in datas[i+1:]:
            if (venc2 - venc1).days >= dias_minimos:
                venc_pairs.append((venc1.strftime("%Y-%m-%d"), venc2.strftime("%Y-%m-%d")))

    resultados = []

    for tipo in ['put', 'call']:
        for venc_curto, venc_longo in venc_pairs:
            chain_curta = vix.option_chain(venc_curto)
            chain_longa = vix.option_chain(venc_longo)

            df_curta = chain_curta.puts if tipo == 'put' else chain_curta.calls
            df_longa = chain_longa.puts if tipo == 'put' else chain_longa.calls

            for strike in strike_range:
                linha_curta = df_curta[df_curta['strike'] == strike]
                linha_longa = df_longa[df_longa['strike'] == strike]

                if linha_curta.empty or linha_longa.empty:
                    continue

                c = linha_curta.iloc[0]
                l = linha_longa.iloc[0]

                mid_curta = (c['bid'] + c['ask']) / 2 if c['bid'] > 0 and c['ask'] > 0 else None
                mid_longa = (l['bid'] + l['ask']) / 2 if l['bid'] > 0 and l['ask'] > 0 else None

                if mid_curta is None or mid_longa is None:
                    continue

                custo = round(mid_longa - mid_curta, 3)
                if abs(custo) <= limite_debito:
                    resultados.append({
                        'Strike': strike,
                        'Venc. Curto': venc_curto,
                        'Venc. Longo': venc_longo,
                        'Dias Dif.': (datetime.strptime(venc_longo, "%Y-%m-%d") - datetime.strptime(venc_curto, "%Y-%m-%d")).days,
                        'Mid Curta': round(mid_curta, 3),
                        'Mid Longa': round(mid_longa, 3),
                        'Custo Líquido': round(custo, 3),
                        'Tipo': tipo.upper()
                    })

    col_order = ['Strike', 'Venc. Curto', 'Venc. Longo', 'Dias Dif.', 'Mid Curta', 'Mid Longa', 'Custo Líquido', 'Tipo']
    df = pd.DataFrame(resultados)[col_order]
    return df.sort_values(by=['Strike', 'Dias Dif.'], ascending=[False, True])

# Exemplo de uso
resultado = buscar_zero_cost_vix_formatado(strike_range=range(15, 35), limite_debito=0.01)
print(resultado)
