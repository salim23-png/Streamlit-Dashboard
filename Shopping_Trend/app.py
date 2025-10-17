# import libraries required
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
import us
import os

# set page config
st.set_page_config(
    page_title="Shopping Trend Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# load data
@st.cache_data(ttl=3600)
def load_data():
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, "shopping_trends_updated.csv")
    data = pd.read_csv(csv_path)
    data = data.drop(columns="Frequency of Purchases", axis=1)                         # delete the frequency of purchases column because we don't use it, unless we need it for segmentation
    data["Difference Amount"] = data["Purchase Amount (USD)"] - data["Previous Purchases"]    # define difference amount column
    data["State Code"] = data["Location"].map(                                              # Make a column from state/location abbreviation 
        lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)
    return data

df = load_data()

# sidebar
with st.sidebar:
    st.title("🛍️ Shopping Trends Dashboard")
    st.header("Filters")
    category_options = sorted(df["Category"].unique())
    category = st.multiselect("Select category:",
                            options=category_options,
                            default=category_options)
    gender_options = sorted(df["Gender"].unique())
    gender= st.multiselect("Select gender:",
                           options=gender_options,
                           default=gender_options)
    color_options = sorted(df["Color"].unique())
    color = st.multiselect("Select color:",
                           options=color_options,
                           default=color_options)
    size_options = sorted(df["Size"].unique())
    size = st.multiselect("Select size:",
                          options=size_options,
                          default=size_options)
    subscription_options = sorted(df["Subscription Status"].unique())
    subscription = st.multiselect("Select subscription status:",
                          options=subscription_options,
                          default=subscription_options)
    discount_options = sorted(df["Discount Applied"].unique())
    discount = st.multiselect("Select discount applied:",
                          options=discount_options,
                          default=discount_options)
    promo_options = sorted(df["Promo Code Used"].unique())
    promo = st.multiselect("Select promo code used:",
                          options=promo_options,
                          default=promo_options)

# filtering, grouping, and summary
df_filtered = df[
    (df["Category"].isin(category)) &
    (df["Gender"].isin(gender)) &
    (df["Color"].isin(color)) &
    (df["Size"].isin(size)) &
    (df["Subscription Status"].isin(subscription)) &
    (df["Discount Applied"].isin(discount)) &
    (df["Promo Code Used"].isin(promo))
]

def format_thousand(value: float) -> str:
    if abs(value) >= 1_000:
        return f"{value /1_000:,.0f}K"
    elif value < 0:
        return f"-{value:,.0f}"
    else:
        return f"{value:,.0f}"
    
def format_percentage(value: float) -> str:
    return f"{value:.2f}%"

df_purchase_amount = df_filtered["Purchase Amount (USD)"].sum()
df_purchase_count = df_filtered["Customer ID"].count()
df_purchase_growth = (df_filtered["Purchase Amount (USD)"].sum() - df_filtered["Previous Purchases"].sum()) / df["Previous Purchases"].sum() * 100

df_state = df_filtered.groupby(["Location", "State Code"], as_index=False).agg({
    "Purchase Amount (USD)": "sum",
    "Age": "mean",
    "Customer ID": "count"
}).rename(columns={"Customer ID": "Purchase Count"})

df_rating = df_filtered["Review Rating"].value_counts().sort_index().reset_index()
df_rating.columns = ["Review Rating", "Count"]
avg_rating = df_filtered["Review Rating"].mean()
                
df_shipping = df_filtered["Shipping Type"].value_counts().sort_index().reset_index()
df_shipping.columns = ["Shipping Type", "Count"]

df_sum = df_filtered.groupby(["Age", "Gender"], as_index=False).agg({
    "Purchase Amount (USD)": "sum",
    "Previous Purchases": "sum"
    })

df_item = df_filtered.groupby(["Season", "Item Purchased"], as_index=False).agg({
    "Purchase Amount (USD)": "sum",
    "Age": "mean",
    "Customer ID": "count"
}).rename(columns={"Customer ID": "Purchase Count"})

df_season = df_filtered.groupby("Season", as_index=False).agg({
    "Purchase Amount (USD)": "sum",
    "Age": "mean",
    "Customer ID": "count"
}).rename(columns={"Customer ID": "Purchase Count"})
df_season["Item Purchased"] = None  # kosongkan kolom item untuk season-level

df_season["id"] = "Season__" + df_season["Season"].astype(str)
df_season["parent"] = "All_Seasons"   # nanti kita buat root "All_Seasons"

df_item["id"] = (
    "Season__" + df_item["Season"].astype(str) + "__Item__" + df_item["Item Purchased"].astype(str)
)
df_item["parent"] = "Season__" + df_item["Season"].astype(str)

root = pd.DataFrame({
    "Season": ["All"],
    "Item Purchased": [None],
    "Purchase Amount (USD)": [df["Purchase Amount (USD)"].sum()],
    "Age": [df_filtered["Age"].mean()],
    "Purchase Count": [df_filtered["Customer ID"].count()],
    "id": ["All_Seasons"],
    "parent": [""]
})

df_sunburst = pd.concat([root, df_season, df_item], ignore_index=True)

df_sunburst["label"] = df_sunburst["Item Purchased"].fillna(df_sunburst["Season"])

df_sunburst["id"] = df_sunburst["id"].astype(str)
df_sunburst["parent"] = df_sunburst["parent"].fillna("").astype(str)
df_sunburst.loc[df_sunburst["parent"] == "", "parent"] = ""  # root tetap ""

df_sunburst["Season_str"] = df_sunburst["Season"].fillna("").astype(str)
df_sunburst["Item_str"] = df_sunburst["Item Purchased"].fillna("").astype(str)
custom = df_sunburst[["Season_str", "Item_str", "Purchase Amount (USD)", "Age"]].values

df_payment = df_filtered["Payment Method"].value_counts().sort_index().reset_index()
df_payment.columns = ["Payment Method", "Count"]

# app layout
def layout_chart(fig, height=300, margin=dict(t=10,b=10,l=10,r=10)):
    fig.update_layout(
        margin=margin,
        height=height,
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor="black",
            font_size=11,
            font_color="white"
        ),
        legend=dict(font=dict(size=10))
        ).update_xaxes(title_font=dict(size=12)
            ).update_yaxes(title_font=dict(size=12))
    return fig

# chart 
fig_purchase = px.bar(
    df_sum,
    x="Age",
    y="Purchase Amount (USD)",
    color="Gender",
    color_discrete_sequence=pc.sequential.Viridis
    ).add_trace(go.Scatter(
        x=df_sum["Age"],
        y=df_sum["Previous Purchases"],
        name="Previous Purchases",
        mode="lines+markers",
        line=dict(color="orange", width=1),
        yaxis="y2")
        ).update_layout(
            template="plotly_white",
            xaxis=dict(title="Age"),
            yaxis=dict(title="Total Purchase Amount (USD)"),
            yaxis2=dict(
                title="Previous Purchase (USD)",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(
                title="Legend",
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.5))
        
fig_item = px.sunburst(
    df_sunburst,
    ids="id",
    parents="parent",
    names="label",          
    values="Purchase Count",
    color="Season",          # color by season
    hover_data={
        "Season": True,
        "Item Purchased": True,
        "Purchase Amount (USD)": ":.0f",
        "Purchase Count": True,
        "Age": ":.1f"},
    branchvalues="total",
    color_discrete_sequence=pc.sequential.Viridis
    ).update_traces(
        customdata=custom,
        hovertemplate=(
            "<b>%{label}</b><br>"                              # display label: item/season
            "Purchase Count: %{value}<br>"                     # always show count
            "Parent: %{parent}<br>"                            # parent id 
            "Season: %{customdata[0]}<br>"                     # season string 
            "Item: %{customdata[1]}<br>"                       # item string 
            "Purchase Amount (USD): %{customdata[2]:,.0f}<br>" 
            "Avg. Age: %{customdata[3]:.1f}<extra></extra>"))
    
fig_state = px.choropleth(
    data_frame=df_state,
    locations="State Code",
    color="Purchase Count",
    locationmode="USA-states",
    scope="usa",
    color_continuous_scale=pc.sequential.Viridis,
    range_color=[df_state["Purchase Count"].quantile(0.05), df_state["Purchase Count"].quantile(0.95)],
    hover_data={                                            # set the format to display
        "Location": True,
        "Purchase Amount (USD)": ":.0f",
        "Purchase Count": True,
        "Age": ":.1f"},
    labels={"Age": "Age (Avg)"}
    ).update_layout(
        coloraxis_colorbar=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5,
        title="Purchase Count"))

fig_payment = px.pie(
    data_frame=df_payment,
    names="Payment Method",
    values="Count",
    hole=0.4,
    color_discrete_sequence=pc.sequential.Viridis
    ).update_traces(
        textinfo="percent+label"
        ).update_layout(
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-1.5,
            xanchor="center",
            x=0.5,
            traceorder='normal',
            itemwidth=50))

fig_rating = px.bar(
    data_frame=df_rating,
    x="Review Rating",
    y="Count",
    text="Count",
    color_discrete_sequence=pc.sequential.Viridis
    ).add_shape(
        type="line",
        x0=avg_rating, x1=avg_rating,                  
        y0=0, y1=df_rating["Count"].max(),            
        line=dict(color="red", width=3, dash="dash"),
        name="Average Rating"
        ).add_annotation(
            x=avg_rating,
            y=df_rating["Count"].max(),
            text=f"Avg: {avg_rating:.2f}",
            showarrow=False,
            yshift=10,
            font=dict(color="red", size=12)
            ).update_traces(
                textposition="outside"
                ).update_layout(
                    xaxis=dict(tickmode="linear"))
                
fig_shipping = px.pie(
    data_frame=df_shipping,
    names="Shipping Type",
    values="Count",
    hole=0.4,
    color_discrete_sequence=pc.sequential.Viridis
    ).update_traces(
        textinfo="percent+label"
        ).update_layout(
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-1.5,
            xanchor="center",                
            x=0.5,
            traceorder='normal',
            itemwidth=50))   

# Row 1 (3 metrics)
with st.container():
    m1, m2, m3 = st.columns(3)
    m1.metric("💵 Total Amount", f"${format_thousand(df_purchase_amount)}")
    m2.metric("🧾 Purchase Count", format_thousand(df_purchase_count))
    m3.metric("📈 Growth", format_percentage(df_purchase_growth))

# Row 2 (3 charts)
with st.container():
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        st.markdown("##### Purchase By Age")
        st.plotly_chart(layout_chart(fig_purchase, height=200), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("##### Review Rating")
        st.plotly_chart(layout_chart(fig_rating, height=200), use_container_width=True, config={"displayModeBar": False})
    with c3:
        st.markdown("##### Item & Season")
        st.plotly_chart(layout_chart(fig_item, height=170), use_container_width=True, config={"displayModeBar": False})
# Row 3 (3 charts)
with st.container():
    c4, c5, c6 = st.columns([2,1,1])
    with c4:
        st.markdown("##### Purchase Distribution")
        st.plotly_chart(layout_chart(fig_state, height=300), use_container_width=True, config={"displayModeBar": False})
    with c5:
        st.markdown("##### Payment Method")
        st.plotly_chart(layout_chart(fig_payment, height=300), use_container_width=False, config={"displayModeBar": False})
    with c6:
        st.markdown("##### Shipping Type")
        st.plotly_chart(layout_chart(fig_shipping, height=300), use_container_width=False, config={"displayModeBar": False})
