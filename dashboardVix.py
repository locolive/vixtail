import dash
from dash import dcc, html, dash_table
import pandas as pd

# Suponha que df já tenha as colunas: Strike, Type, Expiration, MID, IV, Theta, Spread
df = pd.read_csv(r'E:\GitHub\vixtail\opcoes_vix.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Oportunidades VIX"),
    
    dcc.Dropdown(
        id='tipo_dropdown',
        options=[{'label': i, 'value': i} for i in df['Type'].unique()],
        value='PUT',
        multi=False
    ),

    dcc.Slider(
        id='spread_slider',
        min=0, max=0.5, step=0.01, value=0.10,
        marks={0.1: '0.10', 0.2: '0.20', 0.3: '0.30'}
    ),

    dash_table.DataTable(
        id='tabela_opcoes',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        page_size=10
    )
])

@app.callback(
    dash.Output('tabela_opcoes', 'data'),
    dash.Input('tipo_dropdown', 'value'),
    dash.Input('spread_slider', 'value')
)
def update_table(tipo, spread):
    df_filtrado = df[(df['Type'] == tipo) & (df['Spread'] <= spread)]
    return df_filtrado.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)

