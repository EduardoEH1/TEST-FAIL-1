# VialSense

VialSense is our hackathon prototype for helping manufacturing operators
notice unexpected liquid-color patterns during recipe changes. The goal is to
support quality inspection by measuring vial color during filling and
comparing it with the expected pattern for the active recipe. A review alert
is a signal for an operator to investigate; it is not an automatic line
control or a confirmed contamination diagnosis.

## How VialSense Works

VialSense connects four parts of the workflow:

1. **Phase 1 — RGB/HSV Color Analysis:** The liquid finder locates the vial
   and liquid region and measures RGB and OpenCV HSV. Phase 1 organizes those
   readings by recipe, vial, timestamp, and fill progress for comparison and
   visualization.
2. **Phase 2 — Anomaly Scoring:** The scoring module compares a reading
   with a provisional recipe profile for the corresponding filling stage. It
   returns a score and status, or abstains when the reading or context is not
   reliable enough to score.
3. **Live Mode:** Tracks vial arrival and liquid rise, estimates fill
   progress, and assigns the next recipe from an operator-provided queue. The
   recipe is not inferred from color. If the recipe sequence is unknown, it
   can still track vials and show RGB/HSV readings without recipe assignment
   or anomaly scores.
4. **Operator Dashboard:** Displays the live camera, measured color, fill progress,
   and anomaly status. Operators can use automatic tracking or provide recipe
   and progress manually when needed.

The project also supports saved-data analysis and replaying Dataset 2 Video 5.
For implementation details, see the [Phase 1 results and methodology](results/corrected/README.md),
[Phase 2 methodology](results/corrected/phase2/README.md),
[Live Mode guide](LIVE_MODE.md), and [dashboard setup](DASHBOARD_SETUP.md).

## Testing at CSI

On October 30, our team visited the UWM Connected Systems Institute (CSI) and
connected the fluid mixing station's camera to the dashboard. We observed live
vial detection, color measurements, and anomaly scores. The session gave us a
working end-to-end demonstration and helped us identify improvements to liquid
detection and fill-progress handling. We updated the integration afterward;
the updated version has not yet been retested on the physical CSI station.

## Results

Our Dataset 2 analysis covers 30 vials across Recipes 5–14 and 1,067 labeled
fill frames. The saved liquid-finder readings include 879 high-confidence
color measurements.

In a subsequent Video 5 replay, the integrated tracker assigned all 30 vials
in the supplied recipe order. For the 29 vials with an observed fill start,
estimated fill-window starts differed from the corrected labels by a mean
absolute 0.84 seconds; estimated ends differed by 0.72 seconds on average.
The latest replay produced 20 `PASS`, 9 `FLAG`, and 1 `NO DATA`: the first vial
arrived with liquid already visible, so it was not scored. All 38 automated
tests pass. We also replayed the supplied CSI recording through the detector
and tracker adapter. At about five sampled frames per second it produced
1,848 vial detections and 1,780 liquid detections. Since that clip has no
labels, these counts cannot establish
detection accuracy or confirm the vial count. The replay did verify that an
unknown recipe context produces color-only tracking with no anomaly scores.
These results demonstrate the
prototype's workflow on Dataset 2; they do not measure contamination-detection
accuracy.

See the [combined Phase 1 recipe summary](results/corrected/phase1/recipe_summary.csv),
[Phase 2 frame scores](results/corrected/phase2/frame_predictions.csv), and
[temporal comparison](results/temporal_analysis/consolidated/README.md).

## Limitations and Future Improvements

Our recipe profiles are provisional and use selected Dataset 2 vials; the
dataset has no confirmed contamination labels. Lighting, reflections, camera
alignment, liquid visibility, or a missed vial can affect measurements or
recipe/fill context. A new physical CSI station test, camera calibration, and
connections to machine-provided recipe and fill signals are useful next steps.
Detailed measurement, tracker, and scoring caveats are documented in the
[dashboard guide](DASHBOARD_SETUP.md), [Live Mode guide](LIVE_MODE.md), and
[runbook](RUNBOOK.md).

## Installation and Usage

Use Python 3.10 or newer from the project root:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dashboard.txt
```

Run the tests and rebuild Phase 1/Phase 2 outputs to a separate review folder:

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m vialsense.corrected_cli build --output-dir /tmp/vialsense-review
```

Start the dashboard:

```bash
python -m streamlit run app.py
```

To replay the original Video 5 through automatic tracking, provide a local
copy of the video and the recipe queue used in that run:

```bash
PYTHONPATH=src python -m vialsense.live_cli run \
  --video /path/to/vial_fill_video_5.mp4 \
  --recipes "5x3,6x3,7x3,8x3,9x3,10x3,11x3,12x3,13x3,14x3" \
  --fps 5 --no-window --output-dir /tmp/vialsense-live-review
```

The repository does not include raw videos or dataset archives. Saved
measurements and labels are under [`inputs/color_check/`](inputs/color_check/README.md).
The [runbook](RUNBOOK.md) contains PowerShell commands and additional workflow
instructions.

## Repository Guide

| Path | Contents |
|---|---|
| `src/vialsense/` | Reusable Phase 1, Phase 2, detector integration, and Live Mode code |
| `app.py` | Streamlit operator dashboard |
| `inputs/color_check/` | Saved Video 5 measurements and recipe/fill labels |
| `results/corrected/phase1/` | Current RGB/HSV timelines, summaries, and plots |
| `results/corrected/phase2/` | Provisional recipe profiles and anomaly scores |
| `results/integration/` | Saved detector-to-scoring examples and documentation |
| `results/temporal_analysis/` | Temporal recipe analysis and comparison |
| `results/recipe_5`–`results/recipe_14` | Earlier exploratory manual-ROI samples |
| `tests/` | Phase 2, integration, and live-tracker tests |
| `RUNBOOK.md` / `RUNBOOK.pdf` | Setup, replay, dashboard, and troubleshooting steps |
