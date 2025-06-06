import yfinance as yf
import pandas as pd
import datetime

ticker = "^VIX"
strike = 19.0
dias_para_vencimento = 14

def get_target_expiration(expirations, days):
    hoje = datetime.datetime.now().date()
    expirations = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in expirations]
    expirations = sorted(expirations, key=lambda x: abs((x - hoje).days - days))
    return expirations[0].strftime("%Y-%m-%d")

vix = yf.Ticker(ticker)
expirations = vix.options
target_exp = get_target_expiration(expirations, dias_para_vencimento)
opt = vix.option_chain(target_exp)

# Filtro por strike
calls = opt.calls[opt.calls['strike'] == strike]
puts = opt.puts[opt.puts['strike'] == strike]

def extract_option_data(df, tipo):
    if df.empty:
        return { "Tipo": tipo, "MID": None, "lastPrice": None, "IV%": None }
    row = df.iloc[0]
    mid = (row['bid'] + row['ask']) / 2
    return {
        "Tipo": tipo,
        "MID": round(mid, 3),
        "lastPrice": round(row['lastPrice'], 3),
        "IV%": round(row['impliedVolatility'] * 100, 2)
    }

dados = [extract_option_data(calls, "CALL"), extract_option_data(puts, "PUT")]
df_resultado = pd.DataFrame(dados)

print(df_resultado)
