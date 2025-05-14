import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("📊 Regional Sales Dashboard")

# Load CSV data
df = pd.read_csv("data.csv", parse_dates=["Date"])

# Sidebar filter
region = st.sidebar.multiselect(
    "Select Region(s):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Filtered data
filtered_df = df[df["Region"].isin(region)]

# Show data table
st.subheader("Filtered Data")
st.dataframe(filtered_df)

# Summary stats
st.subheader("Summary Statistics")
st.write(filtered_df.describe()[["Sales", "Profit"]])

# Line chart
st.subheader("📈 Sales Over Time")
fig_line, ax_line = plt.subplots()
for r in region:
    df_region = filtered_df[filtered_df["Region"] == r]
    ax_line.plot(df_region["Date"], df_region["Sales"], label=r)
ax_line.set_xlabel("Date")
ax_line.set_ylabel("Sales")
ax_line.legend()
st.pyplot(fig_line)

# Pie chart
st.subheader("🥧 Sales Distribution by Region")
sales_by_region = filtered_df.groupby("Region")["Sales"].sum()
fig_pie, ax_pie = plt.subplots()
ax_pie.pie(sales_by_region, labels=sales_by_region.index, autopct="%1.1f%%", startangle=90)
ax_pie.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig_pie)


df_init = pd.DataFrame({
    "Region": ["North", "South", "East", "West"],
    "Sales": [1000, 1500, 1200, 1800],
    "Profit": [200, 300, 250, 400]
})

# Editable table
st.subheader("✏️ Edit Data")
edited_df = st.data_editor(df_init, num_rows="dynamic")

# Live pie chart based on edited data
st.subheader("🥧 Live Sales Distribution")
fig, ax = plt.subplots()
ax.pie(edited_df["Sales"], labels=edited_df["Region"], autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)