#!/usr/bin/env bash
# Run the Streamlit app (use this if the app fails when started from IDE/background)
cd "$(dirname "$0")"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
exec streamlit run app.py --server.headless true
