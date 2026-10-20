"""
Visualizer Module
Generates interactive Plotly visualizations:
- Bar Chart (grouped, stacked, aggregated)
- Line Chart
- Pie / Donut Chart
- Histogram & Density Plot
- Scatter Plot (with trendlines)
- Box Plot / Violin Plot
- Correlation Heatmap
- Missing Value Map
- Data Quality Gauge Meter
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List

def plot_quality_gauge(score: float) -> go.Figure:
    """Generate a Plotly Gauge chart for Data Quality Score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Data Quality Index", 'font': {'size': 20, 'color': '#1E293B'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': '#0F172A', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#0EA5E9"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#CBD5E1",
            'steps': [
                {'range': [0, 50], 'color': '#FEE2E2'},
                {'range': [50, 75], 'color': '#FEF3C7'},
                {'range': [75, 100], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': "#10B981", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: Optional[str] = None,
    color_col: Optional[str] = None,
    aggregation: str = "count",
    barmode: str = "group",
    title: Optional[str] = None,
    color_scale: str = "Viridis"
) -> go.Figure:
    """Generate an interactive Plotly Bar Chart."""
    if df.empty or x_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Bar Chart", showarrow=False)
        return fig

    if aggregation == "count" or y_col is None:
        if color_col:
            df_plot = df.groupby([x_col, color_col]).size().reset_index(name='Count')
            fig = px.bar(df_plot, x=x_col, y='Count', color=color_col, barmode=barmode,
                         title=title or f"Count of Records by {x_col}", color_discrete_sequence=px.colors.qualitative.Set2)
        else:
            df_plot = df[x_col].value_counts().reset_index()
            df_plot.columns = [x_col, 'Count']
            fig = px.bar(df_plot, x=x_col, y='Count', color='Count',
                         title=title or f"Count of Records by {x_col}", color_continuous_scale=color_scale)
    else:
        # Aggregation (sum, mean, median)
        agg_func = aggregation.lower()
        if color_col:
            df_plot = df.groupby([x_col, color_col])[y_col].agg(agg_func).reset_index()
            fig = px.bar(df_plot, x=x_col, y=y_col, color=color_col, barmode=barmode,
                         title=title or f"{aggregation.title()} of {y_col} by {x_col}", color_discrete_sequence=px.colors.qualitative.Set2)
        else:
            df_plot = df.groupby(x_col)[y_col].agg(agg_func).reset_index()
            fig = px.bar(df_plot, x=x_col, y=y_col, color=y_col,
                         title=title or f"{aggregation.title()} of {y_col} by {x_col}", color_continuous_scale=color_scale)

    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: Optional[str] = None
) -> go.Figure:
    """Generate an interactive Plotly Line Chart."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Line Chart", showarrow=False)
        return fig

    # Sort by X for proper continuous line plotting
    df_sorted = df.sort_values(by=x_col)

    fig = px.line(
        df_sorted,
        x=x_col,
        y=y_col,
        color=color_col,
        markers=True,
        title=title or f"Trend of {y_col} over {x_col}",
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_pie_chart(
    df: pd.DataFrame,
    names_col: str,
    values_col: Optional[str] = None,
    hole: float = 0.4,
    title: Optional[str] = None
) -> go.Figure:
    """Generate an interactive Donut / Pie Chart."""
    if df.empty or names_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Pie Chart", showarrow=False)
        return fig

    if values_col and values_col in df.columns and pd.api.types.is_numeric_dtype(df[values_col]):
        df_plot = df.groupby(names_col)[values_col].sum().reset_index()
        fig = px.pie(df_plot, names=names_col, values=values_col, hole=hole,
                     title=title or f"Distribution of {values_col} by {names_col}",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    else:
        df_plot = df[names_col].value_counts().reset_index()
        df_plot.columns = [names_col, 'Count']
        fig = px.pie(df_plot, names=names_col, values='Count', hole=hole,
                     title=title or f"Distribution of Categories in {names_col}",
                     color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_histogram(
    df: pd.DataFrame,
    x_col: str,
    color_col: Optional[str] = None,
    nbins: int = 30,
    title: Optional[str] = None,
    color_scale: str = "Viridis"
) -> go.Figure:
    """Generate an interactive Histogram / Density plot."""
    if df.empty or x_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Histogram", showarrow=False)
        return fig

    fig = px.histogram(
        df,
        x=x_col,
        color=color_col,
        nbins=nbins,
        marginal="rug",
        title=title or f"Distribution of {x_col}",
        color_discrete_sequence=px.colors.qualitative.Set1,
        opacity=0.75
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    add_trendline: bool = False,
    title: Optional[str] = None
) -> go.Figure:
    """Generate an interactive Scatter Plot."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Scatter Plot", showarrow=False)
        return fig

    trend = "ols" if add_trendline else None

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col if (size_col and size_col in df.columns and (df[size_col] > 0).all()) else None,
        trendline=trend,
        title=title or f"Scatter Plot: {x_col} vs {y_col}",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data=[c for c in df.columns[:5] if c not in [x_col, y_col]]
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_box_plot(
    df: pd.DataFrame,
    y_col: str,
    x_col: Optional[str] = None,
    color_col: Optional[str] = None,
    title: Optional[str] = None
) -> go.Figure:
    """Generate an interactive Box Plot for outlier inspection."""
    if df.empty or y_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available for Box Plot", showarrow=False)
        return fig

    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color=color_col or x_col,
        points="outliers",
        title=title or f"Box Plot of {y_col}" + (f" grouped by {x_col}" if x_col else ""),
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_correlation_heatmap(corr_df: pd.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
    """Generate an annotated correlation heatmap."""
    if corr_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="At least 2 numerical columns required for Correlation Heatmap", showarrow=False)
        return fig

    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=title
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig

def plot_missing_matrix(df: pd.DataFrame) -> go.Figure:
    """Generate an interactive matrix map showing missing cell positions."""
    if df.empty:
        fig = go.Figure()
        return fig

    missing_mask = df.isna().astype(int)
    fig = px.imshow(
        missing_mask.T,
        labels=dict(x="Row Index", y="Column Name", color="Is Missing"),
        color_continuous_scale=[[0, "#E2E8F0"], [1, "#EF4444"]],
        title="Missing Values Heatmap Matrix (Red = Missing Cell)",
        aspect="auto"
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        coloraxis_showscale=False
    )
    return fig
