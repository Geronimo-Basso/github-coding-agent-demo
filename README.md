# github-coding-agent-demo

## NBA Player Directory (Streamlit)

This project now uses a Streamlit app (`app.py`) as the entrypoint to explore a mock NBA players dataset with filtering, sorting, pagination, and inline player cards with images.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Data
Player data CSV and images live in `nba-mock-data/`. Images are expected at `nba-mock-data/img/<playerid>.png`.

### Features
- Text search across name, position, school, country
- Multi-select filters (position, country)
- Draft year range slider
- **Height filter** - Range slider in inches with feet-inches display
- **Weight filter** - Range slider in pounds  
- Sortable by several fields
- Pagination + adjustable page size
- Card layout with fallback placeholder when an image is missing
- Expandable raw DataFrame view

### Next ideas
- Add caching/invalidation controls
- Add team filter if data available
- Add download (CSV) of filtered subset
- Add basic tests for data loading utilities

---
Generated with help from GitHub Copilot Coding Agent.