# github-coding-agent-demo\n\n## NBA Player Directory (Streamlit)\n\nThis project now uses a Streamlit app (`app.py`) as the entrypoint to explore a mock NBA players dataset with filtering, sorting, pagination, and inline player cards with images.\n\n### Run locally\n\n```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```\n\n### Data\nPlayer data CSV and images live in `nba-mock-data/`. Images are expected at `nba-mock-data/img/<playerid>.png`.\n\n### Features\n- Text search across name, position, school, country
- Multi-select filters (position, country)
- Draft year range slider
- Sortable by several fields
- Pagination + adjustable page size
- Card layout with fallback placeholder when an image is missing
- Expandable raw DataFrame view\n\n### Next ideas
- Add caching/invalidation controls
- Add team filter if data available
- Add download (CSV) of filtered subset
- Add basic tests for data loading utilities
\n---\nGenerated with help from GitHub Copilot Coding Agent.
