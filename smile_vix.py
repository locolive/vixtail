import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Obter o objeto do VIX
vix = yf.Ticker("^VIX")

# Selecionar os 3 próximos vencimentos
vencimentos = vix.options[:3]

# Criar o gráfico
plt.figure(figsize=(14, 6))

for venc in vencimentos:
    opt_chain = vix.option_chain(venc)
    calls = opt_chain.calls
    calls = calls[(calls['impliedVolatility'].notna()) & (calls['strike'] < 60)]
    calls_sorted = calls.sort_values('strike')
    strikes = calls_sorted['strike']
    ivs = calls_sorted['impliedVolatility'] * 100  # converter para %

    plt.plot(strikes, ivs, marker='o', label=f'{venc}')

# Configuração do gráfico
plt.title("Smile de Volatilidade Implícita - VIX (Próximos 3 Vencimentos)")
plt.xlabel("Strike")
plt.ylabel("Volatilidade Implícita (%)")
plt.legend(title="Vencimento")
plt.grid(True)
plt.tight_layout()
plt.show()
