import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Netflix Content Strategy Dashboard", layout="wide")

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_content_2023.csv")
    df['Hours Viewed'] = df['Hours Viewed'].replace(',', '', regex=True).astype(float)
    df['Release Date'] = pd.to_datetime(df['Release Date'])
    df['Release Month'] = df['Release Date'].dt.month
    df['Release Day'] = df['Release Date'].dt.day_name()

    def get_season(month):
        return (
            'Winter' if month in [12, 1, 2]
            else 'Spring' if month in [3, 4, 5]
            else 'Summer' if month in [6, 7, 8]
            else 'Fall'
        )
    df['Release Season'] = df['Release Month'].apply(get_season)
    return df

df = load_data()

st.title("🎬 Netflix 2023 Content Strategy Dashboard")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Overview", "Language & Genre", "Time Trends", "Top Content", "Weekly Patterns", "Monthly Pattern", "Viewership by Release Season", "Weekly Releases by Viewing Hours", "Releases Near Major Holidays"
])

# 1. Overview Tab
with tab1:
    st.header("Content Type Comparison")
    view_by_type = df.groupby('Content Type')['Hours Viewed'].sum()

    fig = go.Figure(data=[
        go.Bar(x=view_by_type.index, y=view_by_type.values, marker_color=['skyblue', 'salmon'])
    ])
    fig.update_layout(title="Total Viewership by Content Type", xaxis_title="Content Type", yaxis_title="Hours Viewed")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Interpretation:** Shows significantly outperform movies in terms of hours viewed, suggesting Netflix’s strategic focus on serial content.")

# 2. Language Tab
with tab2:
    st.header("Language Distribution of Viewership")

    lang_view = df.groupby('Language Indicator')['Hours Viewed'].sum().sort_values(ascending=False)
    fig = go.Figure([go.Bar(x=lang_view.index, y=lang_view.values, marker_color='lightcoral')])
    fig.update_layout(title="Viewership by Language", xaxis_title="Language", yaxis_title="Hours Viewed")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Observation:** English dominates, but Korean and other languages show notable traction, highlighting Netflix’s global content diversification.")

# 3. Time Trends
with tab3:
    st.header("Monthly Viewership Trends")

    month_view = df.groupby('Release Month')['Hours Viewed'].sum()
    fig = go.Figure([
        go.Scatter(x=month_view.index, y=month_view.values, mode='lines+markers', marker_color='blue')
    ])
    fig.update_layout(
        title="Monthly Viewership Trend", xaxis_title="Month", yaxis_title="Hours Viewed",
        xaxis=dict(tickmode="array", tickvals=list(range(1,13)), ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    )
    st.plotly_chart(fig, use_container_width=True)

    season_view = df.groupby('Release Season')['Hours Viewed'].sum().reindex(['Winter', 'Spring', 'Summer', 'Fall'])
    fig2 = go.Figure([go.Bar(x=season_view.index, y=season_view.values, marker_color='orange')])
    fig2.update_layout(title="Seasonal Viewership", xaxis_title="Season", yaxis_title="Hours Viewed")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Insight:** December and Fall show peaks in viewership, indicating seasonal content strategy alignment.")

# 4. Top Content
with tab4:
    st.header("Top Performing Titles")

    top5 = df.nlargest(5, 'Hours Viewed')[['Title', 'Content Type', 'Language Indicator', 'Release Date', 'Hours Viewed']]
    st.dataframe(top5)

    st.markdown("**Note:** Most top titles are English-language shows, with Korean content also appearing—evidence of strategic international investments.")

# 5. Weekly Patterns
with tab5:
    st.header("Weekly Patterns in Releases and Engagement")

    day_releases = df['Release Day'].value_counts().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    day_views = df.groupby('Release Day')['Hours Viewed'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(x=day_releases.index, y=day_releases.values, name='Releases', marker_color='blue', opacity=0.6))
    fig.add_trace(go.Scatter(x=day_views.index, y=day_views.values, name='Hours Viewed', mode='lines+markers', marker=dict(color='red')))
    fig.update_layout(title="Content Released vs Viewership by Weekday", xaxis_title="Day of Week", yaxis_title="Count / Hours Viewed")
    st.plotly_chart(fig, use_container_width=True)

# 6. Monthly Patterns
with tab6:
    netflix_data = df
    # --- Viewership Trends by Content Type and Release Month ---
    st.header("Viewership Trends by Content Type and Release Month")

    monthly_viewership_by_type = netflix_data.pivot_table(index='Release Month',
                                                          columns='Content Type',
                                                          values='Hours Viewed',
                                                          aggfunc='sum')

    fig1 = go.Figure()
    for content_type in monthly_viewership_by_type.columns:
        fig1.add_trace(go.Scatter(
            x=monthly_viewership_by_type.index,
            y=monthly_viewership_by_type[content_type],
            mode='lines+markers',
            name=content_type
        ))

    fig1.update_layout(
        title='Viewership Trends by Content Type and Release Month (2023)',
        xaxis_title='Month',
        yaxis_title='Total Hours Viewed (in billions)',
        xaxis=dict(tickmode='array',
                   tickvals=list(range(1, 13)),
                   ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        height=600,
        width=1000,
        legend_title='Content Type'
    )

    st.plotly_chart(fig1)
    st.markdown("""
    **Insight:** Shows consistently outperform movies in viewership across 2023, peaking in December. Movie viewership is more variable, with spikes in June and October, suggesting strategic content drops.
    """)

# 7. Viewership by Release Season
with tab7:
    # --- Total Viewership by Release Season ---
    st.header("Total Viewership by Release Season")


    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        return 'Fall'


    netflix_data['Release Season'] = netflix_data['Release Month'].apply(get_season)
    seasonal_viewership = netflix_data.groupby('Release Season')['Hours Viewed'].sum()
    seasons_order = ['Winter', 'Spring', 'Summer', 'Fall']
    seasonal_viewership = seasonal_viewership.reindex(seasons_order)

    fig2 = go.Figure(data=[go.Bar(
        x=seasonal_viewership.index,
        y=seasonal_viewership.values,
        marker_color='orange'
    )])

    fig2.update_layout(
        title='Total Viewership Hours by Release Season (2023)',
        xaxis_title='Season',
        yaxis_title='Total Hours Viewed (in billions)',
        xaxis_tickangle=0,
        height=500,
        width=800,
        xaxis=dict(categoryorder='array', categoryarray=seasons_order)
    )

    st.plotly_chart(fig2)
    st.markdown("""
    **Insight:** Fall dominates viewership with over 80 billion hours, while the rest of the year is relatively even. This highlights the strategic concentration of high-performing content in the final quarter.
    """)

# 8. Monthly Releases by Viewing Hours
with tab8:
    # --- Monthly Releases vs Viewership Hours ---
    st.header("Monthly Release Patterns and Viewership Hours")

    monthly_releases = netflix_data['Release Month'].value_counts().sort_index()
    monthly_viewership = netflix_data.groupby('Release Month')['Hours Viewed'].sum()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=monthly_releases.index,
        y=monthly_releases.values,
        name='Number of Releases',
        marker_color='goldenrod',
        opacity=0.7,
        yaxis='y1'
    ))

    fig3.add_trace(go.Scatter(
        x=monthly_viewership.index,
        y=monthly_viewership.values,
        name='Viewership Hours',
        mode='lines+markers',
        marker=dict(color='red'),
        line=dict(color='red'),
        yaxis='y2'
    ))

    fig3.update_layout(
        title='Monthly Release Patterns and Viewership Hours (2023)',
        xaxis=dict(
            title='Month',
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        yaxis=dict(title='Number of Releases', side='left', showgrid=False),
        yaxis2=dict(title='Total Hours Viewed (in billions)', overlaying='y', side='right', showgrid=False),
        legend=dict(x=1.05, y=1),
        height=600,
        width=1000
    )

    st.plotly_chart(fig3)
    st.markdown("""
    **Insight:** Despite a consistent number of releases each month, viewership surges in June and December. This supports the notion that viewership is more influenced by release timing and content quality than by volume.
    """)

# 8. Weekly Releases by Viewing Hours
with tab8:
    # --- Weekly Release Patterns and Viewership ---
    st.header("Weekly Release Patterns and Viewership")

    netflix_data['Release Day'] = netflix_data['Release Date'].dt.day_name()
    weekday_releases = netflix_data['Release Day'].value_counts().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
    weekday_viewership = netflix_data.groupby('Release Day')['Hours Viewed'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=weekday_releases.index,
        y=weekday_releases.values,
        name='Number of Releases',
        marker_color='blue',
        opacity=0.6,
        yaxis='y1'
    ))
    fig4.add_trace(go.Scatter(
        x=weekday_viewership.index,
        y=weekday_viewership.values,
        name='Viewership Hours',
        mode='lines+markers',
        marker=dict(color='red'),
        line=dict(color='red'),
        yaxis='y2'
    ))

    fig4.update_layout(
        title='Weekly Release Patterns and Viewership Hours (2023)',
        xaxis=dict(title='Day of the Week',
                   categoryorder='array',
                   categoryarray=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
        yaxis=dict(title='Number of Releases', showgrid=False, side='left'),
        yaxis2=dict(title='Total Hours Viewed (in billions)', overlaying='y', side='right', showgrid=False),
        legend=dict(x=1.05, y=1),
        height=600,
        width=1000
    )

    st.plotly_chart(fig4)
    st.markdown("""
    **Insight:** Friday stands out with the highest number of releases and peak viewership, indicating Netflix's focus on weekend-ready drops. Viewership drops over the weekend suggests users consume new content immediately after release.
    """)

# 9. Releases Near Major Holidays
with tab9:
    # --- Releases Near Major Holidays ---
    st.header("Releases Around Key Holidays")
    st.markdown("""New Year's Day (Jan 1), Valentine's Day (Feb 14), Independence Day (Jul 4), Halloween (Oct 31), and Christmas Day (Dec 25)""")

    important_dates = pd.to_datetime([
        '2023-01-01', # new year's day
        '2023-02-14', # valentine's day
        '2023-07-04', # independence day (US)
        '2023-10-31', # halloween
        '2023-12-25'  # christmas day
    ])

    # convert to datetime
    important_dates = pd.to_datetime(important_dates)

    holiday_releases = netflix_data[netflix_data['Release Date'].apply(
        lambda x: any((x - date).days in range(-3, 4) for date in important_dates)
    )]

    holiday_viewership = holiday_releases.groupby('Release Date')['Hours Viewed'].sum()
    st.dataframe(
        holiday_releases[['Title', 'Release Date', 'Hours Viewed']])

    st.markdown("""
    The data reveals that Netflix has strategically released content around key holidays and events. Some of the significant releases include:

    - New Year’s Period: The Glory: Season 1, La Reina del Sur: Season 3, and Kaleidoscope: Limited Series were released close to New Year’s Day, resulting in high viewership.
    - Valentine’s Day: Perfect Match: Season 1 and The Romantics: Limited Series were released on February 14th, which align with a romantic theme and capitalize on the holiday’s sentiment.
    """)