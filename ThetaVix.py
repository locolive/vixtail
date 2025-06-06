import yfinance as yf
import pandas as pd
from datetime import datetime

def analisar_theta_extrinseco_realista(strike_alvo):
    vix = yf.Ticker("^VIX")
    spot = vix.info['regularMarketPrice']
    expirations = vix.options

    hoje = datetime.today()
    resultados = []

    for vencimento in expirations:
        opt_chain = vix.option_chain(vencimento)
        puts = opt_chain.puts
        linha_strike = puts[puts['strike'] == strike_alvo]
        if linha_strike.empty:
            continue

        data_venc = datetime.strptime(vencimento, "%Y-%m-%d")
        dias_para_expirar = (data_venc - hoje).days
        if dias_para_expirar <= 0:
            continue

        for _, linha in linha_strike.iterrows():
            preco = linha['lastPrice']
            valor_intrinseco = max(strike_alvo - spot, 0)
            valor_extrinseco = preco - valor_intrinseco
            if valor_extrinseco <= 0:
                continue
            theta_estimado = valor_extrinseco / dias_para_expirar
            resultados.append({
                "Vencimento": vencimento,
                "Dias": dias_para_expirar,
                "Spot": round(spot, 2),
                "Preço Opção": preco,
                "Valor Intrínseco": round(valor_intrinseco, 2),
                "Valor Extrínseco": round(valor_extrinseco, 2),
                "Theta Extrínseco (R$/dia)": round(theta_estimado, 4)
            })

    df = pd.DataFrame(resultados)
    return df.sort_values(by="Theta Extrínseco (R$/dia)", ascending=False)

# Exemplo de uso
strike = 18
df_resultado = analisar_theta_extrinseco_realista(strike)
print(df_resultado)
