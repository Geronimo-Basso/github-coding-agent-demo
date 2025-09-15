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
    for col in ("fname", "lname", "position", "country", "school"):
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

def height_to_inches(height_str: str) -> int:
    """Convert height string like '6-8' to total inches (80)"""
    try:
        if pd.isna(height_str) or not height_str:
            return 0
        parts = str(height_str).split('-')
        if len(parts) == 2:
            feet = int(parts[0])
            inches = int(parts[1])
            return feet * 12 + inches
        return 0
    except Exception:
        return 0

def inches_to_height_str(inches: int) -> str:
    """Convert inches back to feet-inches format like 80 -> '6-8'"""
    if inches <= 0:
        return "0-0"
    feet = inches // 12
    remaining_inches = inches % 12
    return f"{feet}-{remaining_inches}"

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
    
    # Height filter
    st.subheader("Height Filter")
    # Convert all heights to inches for filtering
    height_inches = df["height"].apply(height_to_inches)
    min_height_inches = int(height_inches[height_inches > 0].min()) if len(height_inches[height_inches > 0]) > 0 else 60
    max_height_inches = int(height_inches.max()) if len(height_inches) > 0 else 90
    
    col1, col2 = st.columns(2)
    with col1:
        min_height = st.number_input(
            f"Min Height (in)",
            min_value=min_height_inches,
            max_value=max_height_inches,
            value=min_height_inches,
            help=f"Range: {inches_to_height_str(min_height_inches)} to {inches_to_height_str(max_height_inches)}"
        )
    with col2:
        max_height = st.number_input(
            f"Max Height (in)",
            min_value=min_height_inches,
            max_value=max_height_inches,
            value=max_height_inches,
            help=f"Range: {inches_to_height_str(min_height_inches)} to {inches_to_height_str(max_height_inches)}"
        )
    
    # Show height range in feet-inches format
    st.caption(f"Selected range: {inches_to_height_str(min_height)} to {inches_to_height_str(max_height)}")
    
    # Weight filter
    st.subheader("Weight Filter")
    weight_min = int(df["weight"].min()) if "weight" in df else 160
    weight_max = int(df["weight"].max()) if "weight" in df else 290
    
    col3, col4 = st.columns(2)
    with col3:
        min_weight = st.number_input(
            "Min Weight (lbs)",
            min_value=weight_min,
            max_value=weight_max,
            value=weight_min
        )
    with col4:
        max_weight = st.number_input(
            "Max Weight (lbs)",
            min_value=weight_min,
            max_value=weight_max,
            value=weight_max
        )

# Filtering
fdf = df.copy()

if q:
    ql = q.lower()
    def row_match(r):
        hay = " ".join([
            r.get("fname",""), r.get("lname",""), r.get("position",""),
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

# Height filtering
if "height" in fdf.columns:
    # Add validation for min/max height
    if min_height > max_height:
        st.error("Minimum height cannot be greater than maximum height")
    else:
        fdf_height_inches = fdf["height"].apply(height_to_inches)
        fdf = fdf[(fdf_height_inches >= min_height) & (fdf_height_inches <= max_height)]

# Weight filtering
if "weight" in fdf.columns:
    # Add validation for min/max weight
    if min_weight > max_weight:
        st.error("Minimum weight cannot be greater than maximum weight")
    else:
        fdf = fdf[(fdf["weight"] >= min_weight) & (fdf["weight"] <= max_weight)]

st.write(f"Showing **{len(fdf)}** of {len(df)} players")

# Sort options
sort_col = st.selectbox(
    "Sort by",
    ["lname", "fname", "position", "country", "draft_year", "height", "weight", "birthday"],
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
        name = f"{row['fname']} {row['lname']}".strip()
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
