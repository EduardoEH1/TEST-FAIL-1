"""Small adapter used by the Streamlit camera processor for Salah's tracker."""

from pathlib import Path

import pandas as pd

from .anomaly import load_model
from .corrected_pipeline import score_salah_reading
from .live_tracker import VialTracker, parse_queue


def build_dashboard_tracker(recipe_queue: str, model_path: Path,
                            fill_table_path: Path, previous_recipe: int | None = None) -> VialTracker:
    """Build live tracking with optional recipe context.

    With no recipe queue, vial and fill-start tracking remain active, but no
    recipe duration or anomaly model is needed and no scores can be produced.
    """
    queue = parse_queue(recipe_queue) if recipe_queue.strip() else []
    if not queue:
        def score_fn(reading, recipe_id, fill_progress):
            raise RuntimeError("Phase 2 scoring is disabled when recipe is unknown")

        return VialTracker([], score_fn, {}, default_fill_s=None)

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
        queue, score_fn, fill_seconds,
        previous_recipe=previous_recipe,
    )


STATUS_TEXT = {
    "review_unusual": "Review needed",
    "within_provisional_pattern": "Within reference",
    "insufficient_reference": "No reference for this stage",
    "unreliable_measurement": "Unreliable measurement",
    "missing_measurement": "No color reading",
    "unknown_recipe": "Recipe has no profile",
    "invalid_input": "Waiting for recipe and fill context",
}


def readable_status(status: str | None, tracker_state: str | None = None) -> str:
    """Return operator-friendly scoring text or the current tracker state."""
    if status:
        return STATUS_TEXT.get(status, status)
    return (tracker_state or "Not scored").capitalize()


VERDICT_STYLE = {
    "FLAG": ("#b42318", "#fef3f2"),
    "PASS": ("#1a7f37", "#effaf2"),
    "NO DATA": ("#9a6700", "#fff8e5"),
    "NO RECIPE": ("#9a6700", "#fff8e5"),
}


def finished_vials_table(summaries: list[dict]) -> pd.DataFrame:
    """Return a newest-first table of completed vials and their verdicts."""
    columns = ["Vial", "Recipe", "Previous recipe", "Verdict", "Median score",
               "Flagged readings", "Explanation"]
    if not summaries:
        return pd.DataFrame(columns=columns)
    rows = []
    for summary in reversed(summaries):
        flagged_share = summary.get("flagged_share")
        rows.append({
            "Vial": summary.get("vial"),
            "Recipe": summary.get("recipe_id") if summary.get("recipe_id") is not None else "unknown",
            "Previous recipe": (summary.get("previous_recipe")
                                if summary.get("previous_recipe") is not None else "unknown"),
            "Verdict": summary.get("verdict"),
            "Median score": summary.get("median_score"),
            "Flagged readings": (f"{flagged_share * 100:.0f}%"
                                 if flagged_share is not None else ""),
            "Explanation": summary.get("explanation") or "",
        })
    return pd.DataFrame(rows, columns=columns)
