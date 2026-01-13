import plotly.graph_objects as go


def create_macro_pie_chart(totals):
    """
    Generate interactive pie chart of macro distribution by calories.

    Args:
        totals: dict with 'protein', 'carbs', 'fat' in grams

    Returns:
        Plotly figure object
    """
    # Calculate calories from each macro
    protein_cals = totals['protein'] * 4
    carbs_cals = totals['carbs'] * 4
    fat_cals = totals['fat'] * 9

    labels = ['Protein', 'Carbs', 'Fat']
    values = [protein_cals, carbs_cals, fat_cals]
    colors = ['#FF6B6B', '#4ECDC4', '#FFD93D']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.0f} calories<br>%{percent}<extra></extra>',
        hole=0.4
    )])

    fig.update_layout(
        title=dict(
            text='Calorie Distribution by Macro',
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=350,
        margin=dict(t=50, b=50, l=20, r=20)
    )

    return fig


def create_progress_gauge(value, max_value, title, color_thresholds=None):
    """
    Create a gauge chart for progress visualization.

    Args:
        value: Current value
        max_value: Goal value
        title: Chart title
        color_thresholds: Optional dict with 'green', 'yellow', 'red' thresholds

    Returns:
        Plotly figure object
    """
    if color_thresholds is None:
        color_thresholds = {'green': 0.8, 'yellow': 1.0}

    percentage = value / max_value if max_value > 0 else 0

    # Determine color based on percentage
    if percentage <= color_thresholds['green']:
        bar_color = '#2ECC71'  # Green
    elif percentage <= color_thresholds['yellow']:
        bar_color = '#FFD93D'  # Yellow
    else:
        bar_color = '#FF6B6B'  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': max_value, 'relative': False, 'position': 'bottom'},
        gauge={
            'axis': {'range': [0, max_value * 1.2], 'tickwidth': 1},
            'bar': {'color': bar_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.8], 'color': 'rgba(46, 204, 113, 0.2)'},
                {'range': [max_value * 0.8, max_value], 'color': 'rgba(255, 217, 61, 0.2)'},
                {'range': [max_value, max_value * 1.2], 'color': 'rgba(255, 107, 107, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "#333", 'width': 3},
                'thickness': 0.75,
                'value': max_value
            }
        }
    ))

    fig.update_layout(
        height=200,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig


def create_daily_bar_chart(meals):
    """
    Create a horizontal bar chart showing each meal's contribution.

    Args:
        meals: List of meal dictionaries

    Returns:
        Plotly figure object
    """
    if not meals:
        return None

    descriptions = [m['description'][:30] + '...' if len(m['description']) > 30 else m['description'] for m in meals]
    calories = [m['calories'] for m in meals]

    fig = go.Figure(go.Bar(
        x=calories,
        y=descriptions,
        orientation='h',
        marker_color='#4ECDC4',
        text=[f'{int(c)} cal' for c in calories],
        textposition='outside'
    ))

    fig.update_layout(
        title='Calories by Meal',
        xaxis_title='Calories',
        yaxis_title='',
        height=max(200, len(meals) * 50),
        margin=dict(t=50, b=30, l=150, r=50),
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig
