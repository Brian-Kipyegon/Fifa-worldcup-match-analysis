# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pathlib

def get_pandas_data(csv_filename: str) -> pd.DataFrame:
   '''
   Load data from /data directory as a pandas DataFrame
   using relative paths. Relative paths are necessary for
   data loading to work in Heroku.
   '''
   PATH = pathlib.Path(__file__).parent
   DATA_PATH = PATH.joinpath("data").resolve()
   return pd.read_csv(DATA_PATH.joinpath(csv_filename))

# Incorporate data
df = get_pandas_data("Fifa_world_cup_matches.csv")

# Initialize the app
app = Dash(__name__, external_stylesheets=["./assets/app.css"])
server = app.server

# App layout
app.layout = html.Div(
    [
        html.H1(
            children="Fifa World Cup Match Analysis",
            style={"textAlign": "center", "margin": "10px"},
        ),
        html.Div(
            [
                html.H3("Select a match: "),
                dcc.Dropdown(
                    id="dropdown",
                    options=[
                        {
                            "label": html.Span(
                                children=f"{row['team1']} vs {row['team2']}",
                                style={
                                    "color": "white",
                                    "background-color": "rgb(6, 6, 41)",
                                    "width": "230px",
                                },
                            ),
                            "value": index,
                        }
                        for index, row in df.iterrows()
                    ],
                    value=0,
                    style={
                        "width": "230px",
                        "background-color": "rgb(6, 6, 41)",
                    },
                ),
            ],
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
            },
        ),
        html.Div(
            [
                html.Div(children=[html.H5(id="card1")]),
                html.Div(
                    children=[html.P(id="score-card1"), html.P(id="score-card2")],
                    style={"display": "flex"},
                ),
                html.Div(children=[html.H5(id="card2")]),
            ],
            style={
                "display": "flex",
                "justify-content": "space-around",
                "margin": "10px",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    id="pie-card",
                    children=[dcc.Graph(id="pie-chart", figure={})],
                    style={
                        "display": "flex",
                        "flex-direction": "column",
                        "justify-content": "center",
                        "align-items": "center",
                    },
                ),
                html.Div(
                    id="bar-card",
                    children=[
                        dcc.Graph(id="bar-chart", figure={}),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                    },
                ),
            ],
            className="graph-row",
            style={
                "display": "flex",
                "justify-content": "space-around",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    id="possession-card",
                    children=[dcc.Graph(id="possession-chart", figure={})],
                ),
                html.Div(
                    id="fouls-card",
                    children=[dcc.Graph(id="fouls-chart", figure={})],
                ),
            ],
            className="graph-row",
            style={
                "display": "flex",
                "justify-content": "space-around",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    id="freekick-card",
                    children=[dcc.Graph(id="freekick-chart", figure={})],
                ),
                html.Div(
                    id="goalsprevented-card",
                    children=[dcc.Graph(id="goalsprevented-chart", figure={})],
                ),
            ],
            className="graph-row",
            style={
                "display": "flex",
                "justify-content": "space-around",
            },
        ),
    ],
    style={
        "padding-left": "10px",
        "padding-right": "10px",
    },
)


# Callbacks
@callback(
    Output("card2", "children"),
    Output("card1", "children"),
    Input("dropdown", "value"),
)
def update_card(value):
    data = df.iloc[value]

    return (
        f"{data['team2']}",
        f"{data['team1']}",
    )


@callback(
    Output("score-card2", "children"),
    Output("score-card1", "children"),
    Input("dropdown", "value"),
)
def update_score(value):
    data = df.iloc[value]

    return (
        f"{data['number of goals team2']}",
        f"{data['number of goals team1']} : ",
    )


@callback(
    Output("pie-chart", "figure"),
    Input("dropdown", "value"),
)
def pie_chart(value):
    data = df.iloc[value]
    data_list = [
        data["total attempts team1"],
        data["total attempts team2"],
    ]
    team1attempts = data["total attempts team1"]
    team2attempts = data["total attempts team2"]

    fig = px.pie(
        values=data_list,
        names=[data["team1"], data["team2"]],
        title="Goal Attempts",
        color=["white", "#0bfcf8"],
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.5,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title_x=0.5,
        plot_bgcolor="rgb(6, 6, 41)",
        paper_bgcolor="rgb(6, 6, 41)",
        font_color="white",
        width=400,
        height=400,
    )

    return fig


@callback(
    Output("bar-chart", "figure"),
    Input("dropdown", "value"),
)
def pie_chart(value):
    data = df.iloc[value]

    passes_team1 = data["passes team1"] - data["passes completed team1"]
    passes_team2 = data["passes team2"] - data["passes completed team2"]
    passes_completed_team1 = data["passes completed team1"]
    passes_completed_team2 = data["passes completed team2"]

    # Create the trace for total passes
    trace_passes = go.Bar(
        x=[data["team1"], data["team2"]],
        y=[passes_team1, passes_team2],
        name="Incomplete Passes",
    )

    # Create the trace for completed passes
    trace_completed_passes = go.Bar(
        x=[data["team1"], data["team2"]],
        y=[passes_completed_team1, passes_completed_team2],
        name="Completed Passes",
    )

    # Create the data list
    data = [trace_completed_passes, trace_passes]

    # Define the layout
    layout = go.Layout(
        title="Passes",
        xaxis=dict(title="Teams"),
        yaxis=dict(title="Passes"),
        barmode="stack",
        plot_bgcolor="rgb(6, 6, 41)",
        paper_bgcolor="rgb(6, 6, 41)",
        font_color="white",
        width=400,
        height=400,
    )

    # Create the figure
    fig = go.Figure(
        data=data,
        layout=layout,
    )

    return fig


def create_pie_chart(data_list, labels, title):
    fig = px.pie(
        values=data_list,
        names=labels,
        title=title,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.5,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title_x=0.5,
        plot_bgcolor="rgb(6, 6, 41)",
        paper_bgcolor="rgb(6, 6, 41)",
        font_color="white",
        width=400,
        height=400,
    )

    return fig


@callback(
    Output("possession-chart", "figure"),
    Input("dropdown", "value"),
)
def possession_chart(value):
    data = df.iloc[value]

    def stringify(value):
        string_number = value.replace("%", "")
        integer_number = int(string_number)

        return integer_number

    data_list = [
        stringify(data["possession team1"]),
        stringify(data["possession team2"]),
        stringify(data["possession in contest"]),
    ]

    fig = create_pie_chart(
        data_list=data_list,
        labels=[data["team1"], data["team2"], "In Contest"],
        title="Possession",
    )

    return fig


@callback(
    Output("fouls-chart", "figure"),
    Input("dropdown", "value"),
)
def possession_chart(value):
    data = df.iloc[value]

    data_list = [
        data["fouls against team1"],
        data["fouls against team2"],
    ]

    fig = create_pie_chart(
        data_list=data_list,
        labels=[data["team1"], data["team2"]],
        title="Fouls",
    )

    return fig


@callback(
    Output("freekick-chart", "figure"),
    Input("dropdown", "value"),
)
def possession_chart(value):
    data = df.iloc[value]

    data_list = [
        data["free kicks team1"],
        data["free kicks team1"],
    ]

    fig = create_pie_chart(
        data_list=data_list,
        labels=[data["team1"], data["team2"]],
        title="Free kicks",
    )

    return fig


@callback(
    Output("goalsprevented-chart", "figure"),
    Input("dropdown", "value"),
)
def possession_chart(value):
    data = df.iloc[value]

    data_list = [
        data["goal preventions team1"],
        data["goal preventions team2"],
    ]

    fig = create_pie_chart(
        data_list=data_list,
        labels=[data["team1"], data["team2"]],
        title="Goal Preventions",
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
