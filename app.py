# added with GitHub Copilot
import os
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🏀 Players Directory", layout="wide")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"playerid": str})  # keep ids as strings for image paths
    # Basic normalization (helps if future CSVs tweak capitalization)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ("first_name", "last_name", "position", "country", "school"):
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df

def image_path_for(playerid: str) -> str:
    # Try png then jpg as a fallback
    png = os.path.join("nba-mock-data/img", f"{playerid}.png")
    return png if os.path.exists(png) else ""

def age_from_birthday(birthday: str) -> str:
    try:
        dt = datetime.strptime(birthday, "%Y-%m-%d").date()
        today = datetime.utcnow().date()
        years = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
        return str(years)
    except Exception:
        return "—"

df = load_data("nba-mock-data/players.csv")

st.title("🏀 NBA Player Directory (Local Demo)")
st.caption("Search and browse players. Images resolve from ./img/{playerid}.png")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    q = st.text_input("Search (name, team, school, country, position)", "")
    pos_options = sorted([p for p in df["position"].dropna().unique() if p])
    sel_positions = st.multiselect("Position", pos_options, default=[])
    countries = sorted([c for c in df["country"].dropna().unique() if c])
    sel_countries = st.multiselect("Country", countries, default=[])
    draft_year_min = int(df["draft_year"].min()) if "draft_year" in df else 1947
    draft_year_max = int(df["draft_year"].max()) if "draft_year" in df else 2025
    draft_range = st.slider("Draft year", draft_year_min, draft_year_max, (draft_year_min, draft_year_max))

# Filtering
fdf = df.copy()

if q:
    ql = q.lower()
    def row_match(r):
        hay = " ".join([
            r.get("first_name",""), r.get("last_name",""), r.get("position",""),
            r.get("country",""), r.get("school","")
        ]).lower()
        return ql in hay
    fdf = fdf[fdf.apply(row_match, axis=1)]

if sel_positions:
    fdf = fdf[fdf["position"].isin(sel_positions)]
if sel_countries:
    fdf = fdf[fdf["country"].isin(sel_countries)]
if "draft_year" in fdf:
    fdf = fdf[(fdf["draft_year"] >= draft_range[0]) & (fdf["draft_year"] <= draft_range[1])]

st.write(f"Showing **{len(fdf)}** of {len(df)} players")

# Sort options
sort_col = st.selectbox(
    "Sort by",
    ["last_name", "first_name", "position", "country", "draft_year", "height", "weight", "birthday"],
    index=0
)
ascending = st.toggle("Ascending", value=True)
if sort_col in fdf.columns:
    fdf = fdf.sort_values(by=sort_col, ascending=ascending, na_position="last")

# Card grid
def render_card(row):
    col1, col2 = st.columns([1, 3], gap="small")
    with col1:
        ipath = image_path_for(row["playerid"])
        if ipath:
            st.image(ipath, use_container_width=True)
        else:
            st.markdown(
                f"<div style='width:100%;height:0;padding-bottom:100%;background:#eee;"
                f"display:flex;align-items:center;justify-content:center;border-radius:8px;'>"
                f"<span style='color:#777;font-size:12px;'>No Image</span></div>",
                unsafe_allow_html=True
            )
    with col2:
        name = f"{row['first_name']} {row['last_name']}".strip()
        st.markdown(f"### {name}")
        meta = []
        if "position" in row and row["position"]:
            meta.append(f"**Position:** {row['position']}")
        if "height" in row and row["height"]:
            meta.append(f"**Height:** {row['height']}")
        if "weight" in row and str(row["weight"]).strip():
            meta.append(f"**Weight:** {row['weight']} lbs")
        if "birthday" in row and row["birthday"]:
            meta.append(f"**Age:** {age_from_birthday(row['birthday'])}")
        if "country" in row and row["country"]:
            meta.append(f"**Country:** {row['country']}")
        if "school" in row and row["school"]:
            meta.append(f"**School:** {row['school']}")
        st.markdown("  •  ".join(meta))
        if "draft_year" in row:
            st.caption(f"Draft: {int(row['draft_year'])} – Round {(row.get('draft_round', 0))}, Pick {(row.get('draft_number', 0))}")

# Paginate
page_size = st.selectbox("Players per page", [6, 9, 12, 24, 48], index=2)
page = st.number_input("Page", min_value=1, value=1, step=1)
start = (page - 1) * page_size
chunk = fdf.iloc[start:start+page_size]

# Render grid in rows of 3 cards
cards = list(chunk.to_dict(orient="records"))
for i in range(0, len(cards), 3):
    c1, c2, c3 = st.columns(3, gap="large")
    for idx, col in enumerate((c1, c2, c3)):
        if i + idx < len(cards):
            with col:
                st.container(border=True)
                render_card(cards[i + idx])

# Optional raw table toggle
with st.expander("Raw table"):
    st.dataframe(fdf, use_container_width=True, height=400)
