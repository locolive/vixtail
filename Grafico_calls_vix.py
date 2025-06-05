import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Parâmetros
ticker = "^VIX"
strikes = list(range(20, 31)) + [35, 40, 45]
end_date = datetime.date(2026, 2, 28)

# Objeto do ativo
vix = yf.Ticker(ticker)

# Vencimentos disponíveis
expiration_dates = vix.options
expiration_dates = [date for date in expiration_dates if datetime.datetime.strptime(date, '%Y-%m-%d').date() <= end_date]

# Coleta dos dados
options_data = []

for exp in expiration_dates:
    opt = vix.option_chain(exp)
    calls = opt.calls
    calls_filtered = calls[calls['strike'].isin(strikes)]
    for _, row in calls_filtered.iterrows():
        options_data.append({
            'expiration': exp,
            'strike': row['strike'],
            'lastPrice': row['lastPrice']
        })

df = pd.DataFrame(options_data)
df['expiration'] = pd.to_datetime(df['expiration'])

# Pivotar os dados para o gráfico
pivot_df = df.pivot(index='expiration', columns='strike', values='lastPrice')

# Plotar
pivot_df.plot(marker='o', figsize=(14, 6))
plt.title("Preços das Calls do VIX por Strike e Vencimento")
plt.xlabel("Vencimento")
plt.ylabel("Preço da Call")
plt.grid(True)
plt.legend(title="Strike")
plt.tight_layout()
plt.show()
