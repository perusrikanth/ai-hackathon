#!/bin/bash
uvicorn src.api.server:app --reload &
streamlit run src/ui/app.py