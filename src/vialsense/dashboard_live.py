"""Small adapter used by the Streamlit camera processor for Salah's tracker."""

from pathlib import Path

import pandas as pd

from .anomaly import load_model
from .corrected_pipeline import score_salah_reading
from .live_tracker import VialTracker, parse_queue


def build_dashboard_tracker(recipe_queue: str, model_path: Path,
                            fill_table_path: Path, previous_recipe: int | None = None) -> VialTracker:
    """Create the live tracker with the same Phase 2 scorer used by the app."""
    model = load_model(model_path)
    windows = pd.read_csv(fill_table_path)
    required = {"recipe_id", "duration_s"}
    if missing := required - set(windows.columns):
        raise ValueError("Fill-time table lacks columns: " + ", ".join(sorted(missing)))
    durations = pd.to_numeric(windows.duration_s, errors="coerce")
    recipes = pd.to_numeric(windows.recipe_id, errors="coerce")
    usable = pd.DataFrame({"recipe_id": recipes, "duration_s": durations}).dropna()
    fill_seconds = usable.groupby("recipe_id").duration_s.mean().to_dict()

    def score_fn(reading, recipe_id, fill_progress):
        return score_salah_reading(
            model, reading, recipe_id=recipe_id, fill_progress=fill_progress,
        )

    return VialTracker(
        parse_queue(recipe_queue), score_fn, fill_seconds,
        previous_recipe=previous_recipe,
    )
