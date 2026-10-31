# Live dashboard and Video 5 replay

The Streamlit dashboard connects the camera liquid finder, the live vial
tracker, and the existing Phase 2 scorer. Automatic tracking detects vial
arrival and visible fill progress. The operator supplies the recipe queue in
production order because recipe identity is not inferred from color. A manual
recipe/progress mode remains available as a fallback.

## Install and launch

From the repository root, activate the project environment and install both
dependency sets:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dashboard.txt
python -m streamlit run app.py
```

Grant browser camera access for a live stream. The automatic tracker defaults
to the Dataset 2 Video 5 queue (`5x3,...,14x3`); edit it to match the actual
run before using the dashboard. Clear the field if the recipe sequence is
unknown. With a blank queue, the dashboard still detects/tracks vials and
shows RGB/HSV readings, but assigns no recipes, produces no anomaly scores,
and does not estimate recipe-based fill percentages. If the filling start is
not observed, it displays **Fill start not observed** and does not score that
vial. Provide the recipe that ran before the queue when known. “Skip missed
vial” and “Undo queue step” correct queue alignment after a missed or
double-counted vial.
Automatic mode uses the review boundary saved in the active model; changing the
sidebar's manual display threshold does not alter the automatic tracker.

If the browser camera view differs from Dataset 2's fixed view, calibrate that
camera with `vialsense.live_cli calibrate`, inspect its preview, then upload
the resulting calibration JSON in the dashboard. Do not trust detection until
the preview places the holder in the reference position.

For a repeatable non-camera replay of the integrated automatic pipeline:

```bash
PYTHONPATH=src python -m vialsense.live_cli run \
  --video /path/to/vial_fill_video_5.mp4 \
  --recipes "5x3,6x3,7x3,8x3,9x3,10x3,11x3,12x3,13x3,14x3" \
  --fps 5 --no-window --output-dir /tmp/vialsense-video5-replay
```

For Windows PowerShell, replace `PYTHONPATH=src` with `$env:PYTHONPATH = "src"`
on a separate line before running Python. Live replay outputs include
`frames.csv`, `vials.csv`, `events.log`, and `run_summary.json`.

## Video 5 validation

The local Video 5 replay found and assigned all 30 vials in queue order. The
for the 29 vials with an observed fill start, estimated fill-window starts
differed from corrected CSV labels by a mean absolute 0.84 s (maximum 4.06 s);
estimated ends differed by 0.72 s on average (maximum 3.03 s). The latest
replay produced 20 `PASS`, 9 `FLAG`, and 1
`NO DATA` verdict. Vial 1 is unscored because it arrived with liquid already
visible. This is one fewer `FLAG` than the previously saved replay: the
updated logic no longer creates an end-anchored score when fill start was not
observed. These remain provisional model outputs, not accuracy or
contamination evidence.

Video 5 starts with liquid already visible in Vial 1. The tracker labels that
start as unobserved and withholds progress and anomaly scoring instead of
mistaking a later rise or an end-anchored estimate for the true start. That
vial can still be detected and its color recorded, but its final status is
`NO DATA`. Start the dashboard before the first empty vial arrives for normal
live use.

The supplied CSI recording was also replayed through the same detector and
dashboard tracker adapter with an empty recipe queue. At 5 sampled frames per
second, it yielded 1,848 vial detections, 1,780 liquid detections, 1,627
high-confidence liquid readings, and eight tracked segments. No recipe or
anomaly scores were assigned. Each segment began with liquid already visible,
so the tracker displayed **Fill start not observed**. This confirms the
recorded-file processing path; it is not a live browser-camera test at CSI,
and the recording has no labels to verify vial counts or recipe identity.

## Limits to keep in mind

- Automatic recipe assignment is an operator-provided queue; an incorrect
  queue or uncorrected missed vial shifts every later recipe assignment.
- Fill progress is inferred from detected liquid height and average Dataset 2
  recipe fill times. It is not a machine dispense signal or liquid-volume
  sensor.
- Progress and scoring are withheld if a clear liquid column is already
  present when a vial first arrives; the camera run missed observing the fill
  start.
- The liquid finder uses fixed image geometry. Calibrate or align the CSI view
  to the reference view before relying on detection.
- The color references and anomaly status are provisional. A FLAG asks for
  review; it does not confirm carryover or contamination.

Run the complete local test suite with:

```bash
PYTHONPATH=src python -m pytest -q
```
