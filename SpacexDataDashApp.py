# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
minner = min_payload
maxor = max_payload

# Create a dash application
app = dash.Dash(__name__)
sitesnp = spacex_df["Launch Site"].unique()
sites = sitesnp.tolist()
sites.append("All Sites")
Ddoptions = [{"label":s, "value":s} for s in sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=Ddoptions, value = 'All Sites', placeholder = "placeholder", searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000',
                                                       7500: '7500', 10000: '10000'},
                                                value=[minner, maxor]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        successful_launches = spacex_df[spacex_df['class'] == 1]
        site_success_counts = successful_launches['Launch Site'].value_counts().reset_index()
        site_success_counts.columns = ['Launch Site', 'count']
        fig = px.pie(site_success_counts,
                     values='count',
                     names='Launch Site', # Now names are launch sites
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(success_counts,
                     values='count',
                     names='class',
                     title=f'Success vs. Failure for {entered_site}')
        fig.update_traces(labels=['Failure', 'Success'], marker=dict(colors=['#EF553B', '#636EFA']))
    return fig

# TASK 4:
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df_payload = spacex_df[(spacex_df['Payload Mass (kg)'].between(low, high))]

    if entered_site == 'All Sites':
        current_df = filtered_df_payload
        title_text = 'Correlation between Payload and Success for All Sites'
    else:
        current_df = filtered_df_payload[filtered_df_payload['Launch Site'] == entered_site]
        title_text = f'Correlation between Payload and Success for {entered_site}'
    
    if current_df.empty:
        import plotly.graph_objects as go
        fig = go.Figure().add_annotation(x=2.5, y=2.5, text="No data selected for this range and site",
                                         showarrow=False, font=dict(size=20))
        fig.update_layout(title_text=title_text)
    else:
        fig = px.scatter(current_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=title_text)
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
