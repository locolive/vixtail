import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Parâmetros
vix = yf.Ticker("^VIX")
vencimentos = vix.options
strikes = list(range(15, 25)) #+ [35, 40, 45]

# Inicializa DataFrame
df = pd.DataFrame(index=strikes, columns=vencimentos)

# Preenche com valores MID das CALLs
for venc in vencimentos:
    try:
        calls = vix.option_chain(venc).calls
        for strike in strikes:
            row = calls[calls['strike'] == strike]
            if not row.empty:
                bid, ask = row['bid'].values[0], row['ask'].values[0]
                if bid > 0 and ask > 0:
                    df.at[strike, venc] = round((bid + ask) / 2, 2)
    except Exception as e:
        print(f"Erro ao processar {venc}: {e}")

# Limpa colunas vazias
df.dropna(axis=1, how='all', inplace=True)

# Converte para float
df = df.astype(float)

# Plota estilo heatmap
plt.figure(figsize=(16, 8))
sns.heatmap(df, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=0.5, linecolor='gray')
plt.title("Dashboard de Preços MID - CALLs do VIX (Strikes x Vencimentos)", fontsize=14)
plt.xlabel("Vencimento")
plt.ylabel("Strike")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
