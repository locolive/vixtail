import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Ticker do VIX
vix = yf.Ticker("^VIX")

# Strikes desejados
strikes = list(range(15, 31)) #+ [35, 40, 45]

# Vencimentos disponíveis (filtrar para datas mais próximas, se quiser limitar)
vencimentos = vix.options[:12]  # Exemplo: próximos 12 vencimentos

# Inicializa DataFrame
puts_mid_table = pd.DataFrame(index=strikes, columns=vencimentos)

# Preencher tabela com valores MID
for venc in vencimentos:
    try:
        chain = vix.option_chain(venc).puts
        for strike in strikes:
            row = chain[chain['strike'] == strike]
            if not row.empty:
                bid = row['bid'].values[0]
                ask = row['ask'].values[0]
                if bid > 0 and ask > 0:
                    mid = round((bid + ask) / 2, 2)
                    puts_mid_table.loc[strike, venc] = mid
    except Exception as e:
        print(f"Erro em {venc}: {e}")

# Remove colunas e linhas sem dados
puts_mid_table.dropna(axis=1, how='all', inplace=True)
puts_mid_table.dropna(axis=0, how='all', inplace=True)

# Conversão para float (necessário para heatmap)
puts_mid_table = puts_mid_table.astype(float)

# Gera o heatmap
plt.figure(figsize=(14, 8))
sns.heatmap(puts_mid_table, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=0.5, linecolor='gray')
plt.title("Heatmap - Preço MID das PUTs do VIX")
plt.xlabel("Vencimento")
plt.ylabel("Strike")
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
