# pages/explore.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

df = pd.read_csv('data/combined_data.csv')

def get_numeric_columns(df):
    """Get all numeric columns for dropdown options."""
    return [
        {'label': col, 'value': col}
        for col in df.select_dtypes(include=[np.number]).columns
    ]

def calculate_correlation(df, x_col, y_col):
    """Calculate correlation between two columns."""
    corr, p_value = pearsonr(df[x_col], df[y_col])
    return corr, p_value

def create_visualization(df, chart_type, x_col, y_col, color_by, size_by=None, agg_func='mean'):
    """Create visualization based on user selections."""
    
    if chart_type == 'scatter':
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_by,
            size=size_by if size_by else None,
            trendline="ols",
            hover_data=['Country'],
            title=f'{x_col} vs {y_col}',
            height=600
        )
        
        # Add correlation information
        corr, p_value = calculate_correlation(df, x_col, y_col)
        fig.add_annotation(
            text=f'Correlation: {corr:.2f}<br>p-value: {p_value:.3f}',
            xref='paper', yref='paper',
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        )
        
    elif chart_type == 'box':
        fig = px.box(
            df,
            x=color_by,
            y=y_col,
            color=color_by,
            title=f'{y_col} Distribution by {color_by}',
            height=600
        )
        
    elif chart_type == 'bar':
        agg_data = df.groupby(color_by)[y_col].agg(agg_func).reset_index()
        fig = px.bar(
            agg_data,
            x=color_by,
            y=y_col,
            color=color_by,
            title=f'Average {y_col} by {color_by}',
            height=600
        )
        
    elif chart_type == 'line':
        agg_data = df.groupby(x_col)[y_col].agg(agg_func).reset_index()
        fig = px.line(
            agg_data,
            x=x_col,
            y=y_col,
            title=f'Trend of {y_col} over {x_col}',
            height=600
        )
    
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def create_layout(df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Interactive Data Exploration", className="mb-4"),
                html.P(
                    "Create custom visualizations to explore relationships between different variables in the dataset.",
                    className="lead mb-4"
                )
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-chart-line me-2"),
                            html.H4("Visualization Studio", className="d-inline m-0"),
                            dbc.Button(
                                html.I(className="fas fa-question-circle"),
                                id="help-button",
                                color="link",
                                size="sm",
                                className="float-end"
                            )
                        ])
                    ]),
                    dbc.CardBody([
                        # Chart Type Selection with Icons
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dbc.RadioItems(
                                        id='chart-type',
                                        options=[
                                            {
                                                'label': html.Div([
                                                    html.I(className="fas fa-chart-scatter me-2"),
                                                    "Scatter Plot"
                                                ], className="d-flex align-items-center"),
                                                'value': 'scatter'
                                            },
                                            {
                                                'label': html.Div([
                                                    html.I(className="fas fa-box me-2"),
                                                    "Box Plot"
                                                ], className="d-flex align-items-center"),
                                                'value': 'box'
                                            },
                                            {
                                                'label': html.Div([
                                                    html.I(className="fas fa-chart-bar me-2"),
                                                    "Bar Chart"
                                                ], className="d-flex align-items-center"),
                                                'value': 'bar'
                                            },
                                            {
                                                'label': html.Div([
                                                    html.I(className="fas fa-chart-line me-2"),
                                                    "Line Chart"
                                                ], className="d-flex align-items-center"),
                                                'value': 'line'
                                            }
                                        ],
                                        value='scatter',
                                        inline=True,
                                        className="chart-type-selector"
                                    )
                                ], className="p-3 bg-light rounded mb-4")
                            ], width=12)
                        ]),
                        
                        # Tabbed interface for different control groups
                        dbc.Tabs([
                            dbc.Tab(
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div([
                                                html.Label("Select Variable", className="fw-bold mb-2"),
                                                dcc.Dropdown(
                                                    id='x-axis',
                                                    options=get_numeric_columns(df),
                                                    value='valence',
                                                    clearable=False,
                                                    className="mb-3"
                                                ),
                                                html.Div([
                                                    html.I(className="fas fa-info-circle me-2 info-icon"),
                                                    "Select the variable for the X-axis"
                                                ], className="help-text")
                                            ], className="control-panel")
                                        ], width=12)
                                    ])
                                ],
                                label="X-Axis",
                                tab_id="tab-x-axis",
                                label_style={"padding": "0.75rem 1.5rem"}
                            ),
                            
                            dbc.Tab(
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div([
                                                html.Label("Select Variable", className="fw-bold mb-2"),
                                                dcc.Dropdown(
                                                    id='y-axis',
                                                    options=get_numeric_columns(df),
                                                    value='Life Ladder',
                                                    clearable=False,
                                                    className="mb-3"
                                                ),
                                                html.Div([
                                                    html.I(className="fas fa-info-circle me-2 info-icon"),
                                                    "Select the variable for the Y-axis"
                                                ], className="help-text")
                                            ], className="control-panel")
                                        ], width=12)
                                    ])
                                ],
                                label="Y-Axis",
                                tab_id="tab-y-axis",
                                label_style={"padding": "0.75rem 1.5rem"}
                            ),
                            
                            dbc.Tab(
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div([
                                                html.Label("Group By", className="fw-bold mb-2"),
                                                dcc.Dropdown(
                                                    id='color-by',
                                                    options=[
                                                        {'label': 'Region', 'value': 'region'},
                                                        {'label': 'Genre', 'value': 'track_genre'}
                                                    ],
                                                    value='region',
                                                    clearable=False,
                                                    className="mb-3"
                                                ),
                                                html.Div([
                                                    html.I(className="fas fa-paint-brush me-2 info-icon"),
                                                    "Color code your data points"
                                                ], className="help-text")
                                            ], className="control-panel")
                                        ], width=12)
                                    ])
                                ],
                                label="Color",
                                tab_id="tab-color",
                                label_style={"padding": "0.75rem 1.5rem"}
                            ),
                            
                            dbc.Tab(
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div([
                                                html.Label("Chart Options", className="fw-bold mb-2"),
                                                dbc.Checklist(
                                                    id='plot-options',
                                                    options=[
                                                        {'label': 'Show Trend Line', 'value': 'trend'},
                                                        {'label': 'Show Data Points', 'value': 'points'},
                                                        {'label': 'Show Legend', 'value': 'legend'}
                                                    ],
                                                    value=['trend', 'points', 'legend'],
                                                    switch=True,
                                                    className="mb-3"
                                                )
                                            ], className="control-panel")
                                        ], width=12)
                                    ])
                                ],
                                label="Options",
                                tab_id="tab-options",
                                label_style={"padding": "0.75rem 1.5rem"}
                            )
                        ], id="control-tabs", active_tab="tab-x-axis", className="mb-4")
                    ])
                ], className="mb-4 shadow-sm")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visualization"),
                    dbc.CardBody([
                        dcc.Graph(id='exploration-plot')
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Summary"),
                    dbc.CardBody([
                        html.Div(id='data-summary')
                    ])
                ])
            ], width=12)
        ]),
        
        # Help Modal
        dbc.Modal([
            dbc.ModalHeader("How to Use the Explorer"),
            dbc.ModalBody([
                html.H5("Chart Types"),
                html.P([
                    html.Strong("Scatter Plot: "), 
                    "Shows relationship between two numeric variables"
                ]),
                html.P([
                    html.Strong("Box Plot: "), 
                    "Shows distribution of values across categories"
                ]),
                html.P([
                    html.Strong("Bar Chart: "), 
                    "Shows average values across categories"
                ]),
                html.P([
                    html.Strong("Line Chart: "), 
                    "Shows trends over a continuous variable"
                ]),
                html.H5("Tips"),
                html.Ul([
                    html.Li("Use the dropdowns to select different variables"),
                    html.Li("Hover over points to see detailed information"),
                    html.Li("Click and drag to zoom into specific areas"),
                    html.Li("Double click to reset the view")
                ])
            ])
        ], id="help-modal", is_open=False)
    ])

@callback(
    Output('exploration-plot', 'figure'),
    Output('data-summary', 'children'),
    Input('chart-type', 'value'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value'),
    Input('color-by', 'value'),
    Input('plot-options', 'value')
)
def update_exploration_plot(chart_type, x_col, y_col, color_by, options):
    # Create visualization
    fig = create_visualization(
        df,
        chart_type,
        x_col,
        y_col,
        color_by,
        size_by='Average MHQ Score' if 'points' in options else None
    )
    
    # Create data summary
    if chart_type == 'scatter':
        corr, p_value = calculate_correlation(df, x_col, y_col)
        summary = [
            html.H5("Statistical Summary"),
            html.P([
                f"Correlation coefficient: ",
                html.Strong(f"{corr:.3f}"),
                f" (p-value: {p_value:.3f})"
            ]),
            html.P([
                f"Number of observations: ",
                html.Strong(f"{len(df)}")
            ])
        ]
    else:
        summary = [
            html.H5("Summary Statistics"),
            dbc.Table.from_dataframe(
                df.groupby(color_by)[y_col].agg(['mean', 'std', 'count'])
                .round(2)
                .reset_index(),
                striped=True,
                bordered=True,
                hover=True
            )
        ]
    
    return fig, summary

@callback(
    Output("help-modal", "is_open"),
    Input("help-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_help_modal(n_clicks):
    return True