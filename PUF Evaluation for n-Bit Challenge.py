import csv
import re
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

# Configuration
CSV_FILE = Path("mc200dis1_excel.csv")

# Change this value to the required response width.
# For example, use 8 for Q7-Q0, 4 for Q3-Q0, or 16 for Q15-Q0.
# The CSV headers must match the selected width.
RESPONSE_BITS = 8

OUT_DIR = Path(f"puf_{RESPONSE_BITS}bit_midpoint_results")

VTH = 0.9
CONTROL_LOW_MAX = 0.2

WINDOWS_NS = [
    (25.0, 50.0),
    (75.0, 100.0),
    (125.0, 150.0),
    (175.0, 200.0),
    (225.0, 250.0),
    (275.0, 300.0),
    (325.0, 350.0),
    (375.0, 385.0),
]

# Read and map the Cadence waveform headers.
if not CSV_FILE.exists():
    raise FileNotFoundError(f"CSV not found: {CSV_FILE.resolve()}")

with CSV_FILE.open("r", newline="", encoding="utf-8-sig") as f:
    headers = [h.strip() for h in next(csv.reader(f))]


def build_map(pattern):
    result = {}
    regex = re.compile(pattern, re.IGNORECASE)

    for i, header in enumerate(headers):
        match = regex.fullmatch(header)
        if match:
            if i == 0:
                raise ValueError(f"Missing time column before {header}")

            run = int(match.group(1))
            if run in result:
                raise ValueError(f"Duplicate matching column for MC{run}")

            result[run] = (i - 1, i)

    return result


clk_map = build_map(r"/clk mcparamset (\d+)\s+\(V\)")
puf_map = build_map(r"/puf mcparamset (\d+)\s+\(V\)")

q_map = {
    bit: build_map(
        rf"/Q<{RESPONSE_BITS - 1}:0> bit /Q<{bit}> mcparamset (\d+)\s+\(V\)"
    )
    for bit in range(RESPONSE_BITS)
}

runs = sorted(set(clk_map) & set(puf_map))

for bit in range(RESPONSE_BITS):
    runs = sorted(set(runs) & set(q_map[bit]))

if len(runs) != 200:
    raise ValueError(
        f"Expected 200 complete MC runs; found {len(runs)}. "
        "Check the CSV headers before continuing."
    )

print(f"Monte Carlo runs: {len(runs)}")
print(
    f"Response width: {RESPONSE_BITS} bits "
    f"(Q{RESPONSE_BITS - 1} to Q0)"
)

# Load the waveform samples required for evaluation.
required = set()

for run in runs:
    required.update(clk_map[run])
    required.update(puf_map[run])

    for bit in range(RESPONSE_BITS):
        required.update(q_map[bit][run])

required = sorted(required)

raw = pd.read_csv(
    CSV_FILE,
    usecols=required,
    low_memory=False,
    encoding="utf-8-sig",
).apply(pd.to_numeric, errors="coerce")

column_position = {
    original_index: position
    for position, original_index in enumerate(required)
}


def get_trace(run, pair):
    ti, vi = pair

    t = raw.iloc[:, column_position[ti]].to_numpy(dtype=float)
    v = raw.iloc[:, column_position[vi]].to_numpy(dtype=float)

    valid = np.isfinite(t) & np.isfinite(v)
    t, v = t[valid], v[valid]

    if len(t) == 0:
        raise ValueError(f"No valid samples for MC{run}")

    if np.any(np.diff(t) < 0):
        raise ValueError(
            f"Time decreases for MC{run}. Inspect the original CSV."
        )

    return t, v


def nearest_sample_index(t, target_s):
    """Find the nearest saved sample, choosing the later time for ties."""
    right = np.searchsorted(t, target_s, side="left")
    candidates = [i for i in (right - 1, right) if 0 <= i < len(t)]

    if not candidates:
        raise ValueError("Target is outside the saved waveform.")

    chosen = min(
        candidates,
        key=lambda i: (abs(t[i] - target_s), -t[i])
    )

    selected_time = t[chosen]
    return int(np.searchsorted(t, selected_time, side="right") - 1)


def make_response(q_voltages):
    # Construct the response from the most significant bit down to Q0.
    return "".join(
        "1" if q_voltages[bit] >= VTH else "0"
        for bit in range(RESPONSE_BITS - 1, -1, -1)
    )


# Extract one midpoint sample for every window and Monte Carlo run.
OUT_DIR.mkdir(parents=True, exist_ok=True)

all_voltage_rows = []
all_validation_rows = []
all_metric_rows = []
all_alias_rows = []
all_pair_rows = []

for window_number, (start_ns, end_ns) in enumerate(WINDOWS_NS, start=1):
    midpoint_ns = (start_ns + end_ns) / 2.0
    target_s = midpoint_ns * 1e-9

    print(
        f"\nWindow {start_ns:g}-{end_ns:g} ns; "
        f"sampling midpoint = {midpoint_ns:g} ns"
    )

    window_responses = {}
    window_valid = True

    for run in runs:
        t_clk, v_clk = get_trace(run, clk_map[run])
        t_puf, v_puf = get_trace(run, puf_map[run])

        q_traces = {
            bit: get_trace(run, q_map[bit][run])
            for bit in range(RESPONSE_BITS)
        }

        # Verify that all signals use the same time grid.
        same_grid = (
            len(t_clk) == len(t_puf)
            and np.allclose(t_clk, t_puf, rtol=0, atol=1e-18)
        )

        for bit in range(RESPONSE_BITS):
            tq, _ = q_traces[bit]

            if (
                len(tq) != len(t_clk)
                or not np.allclose(tq, t_clk, rtol=0, atol=1e-18)
            ):
                same_grid = False

        # Select the saved sample nearest to the window midpoint.
        idx_clk = nearest_sample_index(t_clk, target_s)
        actual_time_s = t_clk[idx_clk]
        actual_time_ns = actual_time_s * 1e9

        idx_puf = nearest_sample_index(t_puf, actual_time_s)
        clk_v = float(v_clk[idx_clk])
        puf_v = float(v_puf[idx_puf])

        q_voltages = {}

        for bit in range(RESPONSE_BITS):
            tq, vq = q_traces[bit]
            idx_q = nearest_sample_index(tq, actual_time_s)
            q_voltages[bit] = float(vq[idx_q])

        response = make_response(q_voltages)

        controls_low = (
            clk_v <= CONTROL_LOW_MAX
            and puf_v <= CONTROL_LOW_MAX
        )

        passed = same_grid and controls_low

        if not passed:
            window_valid = False

        validation = {
            "MC_run": run,
            "window_number": window_number,
            "window_start_ns": start_ns,
            "window_end_ns": end_ns,
            "target_midpoint_ns": midpoint_ns,
            "actual_saved_sample_ns": actual_time_ns,
            "CLK_V": clk_v,
            "PUF_V": puf_v,
            "CLK_PUF_both_low": controls_low,
            "same_time_grid": same_grid,
            "PASS": passed,
        }
        all_validation_rows.append(validation)

        voltage_row = {
            "MC_run": run,
            "window_number": window_number,
            "window_start_ns": start_ns,
            "window_end_ns": end_ns,
            "target_midpoint_ns": midpoint_ns,
            "actual_saved_sample_ns": actual_time_ns,
            "CLK_V": clk_v,
            "PUF_V": puf_v,
            **{
                f"Q{bit}_V": q_voltages[bit]
                for bit in range(RESPONSE_BITS - 1, -1, -1)
            },
            f"Response_Q{RESPONSE_BITS - 1}_to_Q0": response,
            "controls_low": controls_low,
            "same_time_grid": same_grid,
        }
        all_voltage_rows.append(voltage_row)

        if passed:
            window_responses[run] = response

    passing_count = sum(
        r["window_number"] == window_number and r["PASS"]
        for r in all_validation_rows
    )

    print(f"Control/time-grid checks passed: {passing_count}/200")

    # Calculate metrics only when all Monte Carlo runs pass validation.
    if not window_valid:
        all_metric_rows.append({
            "window_number": window_number,
            "window_start_ns": start_ns,
            "window_end_ns": end_ns,
            "midpoint_ns": midpoint_ns,
            "runs_passed": passing_count,
            "metrics_calculated": False,
            "uniformity_percent": np.nan,
            "mean_bit_aliasing_percent": np.nan,
            "uniqueness_percent": np.nan,
            "reason": "At least one MC run failed validation",
        })
        continue

    # Build the response matrix for the current window.
    responses = [window_responses[run] for run in runs]

    matrix = np.array(
        [[int(bit) for bit in response] for response in responses],
        dtype=int,
    )

    if matrix.shape != (200, RESPONSE_BITS):
        raise ValueError(f"Unexpected matrix shape: {matrix.shape}")

    response_df = pd.DataFrame({
        "MC_run": runs,
        f"Response_Q{RESPONSE_BITS - 1}_to_Q0": responses,
    })

    for column, bit in enumerate(range(RESPONSE_BITS - 1, -1, -1)):
        response_df[f"Q{bit}"] = matrix[:, column]

    response_df.to_csv(
        OUT_DIR / f"response_window_{window_number:02d}.csv",
        index=False,
    )

    # Calculate uniformity and bit-aliasing.
    uniformity_per_run = matrix.mean(axis=1) * 100
    uniformity = float(uniformity_per_run.mean())

    alias = matrix.mean(axis=0) * 100
    mean_alias = float(alias.mean())

    for column, bit in enumerate(range(RESPONSE_BITS - 1, -1, -1)):
        all_alias_rows.append({
            "window_number": window_number,
            "window_start_ns": start_ns,
            "window_end_ns": end_ns,
            "midpoint_ns": midpoint_ns,
            "bit": f"Q{bit}",
            "ones": int(matrix[:, column].sum()),
            "zeros": 200 - int(matrix[:, column].sum()),
            "bit_aliasing_percent": float(alias[column]),
        })

    # Calculate uniqueness using pairwise normalized Hamming distances.
    distances = []

    for i, j in itertools.combinations(range(200), 2):
        hd = int(np.count_nonzero(matrix[i] != matrix[j]))
        hd_percent = hd / RESPONSE_BITS * 100
        distances.append(hd_percent)

        all_pair_rows.append({
            "window_number": window_number,
            "window_start_ns": start_ns,
            "window_end_ns": end_ns,
            "midpoint_ns": midpoint_ns,
            "MC_i": runs[i],
            "MC_j": runs[j],
            "Hamming_distance_bits": hd,
            "normalized_Hamming_distance_percent": hd_percent,
        })

    uniqueness = float(np.mean(distances))

    all_metric_rows.append({
        "window_number": window_number,
        "window_start_ns": start_ns,
        "window_end_ns": end_ns,
        "midpoint_ns": midpoint_ns,
        "runs_passed": passing_count,
        "metrics_calculated": True,
        "uniformity_percent": uniformity,
        "mean_bit_aliasing_percent": mean_alias,
        "uniqueness_percent": uniqueness,
        "pair_count": len(distances),
        "reason": "All 200 runs passed control/time-grid checks",
    })

# Export the sampled data, validation checks, and calculated metrics.
pd.DataFrame(all_voltage_rows).to_csv(
    OUT_DIR / "sampled_voltages_all_windows.csv", index=False
)

pd.DataFrame(all_validation_rows).to_csv(
    OUT_DIR / "validation_all_runs_all_windows.csv", index=False
)

pd.DataFrame(all_metric_rows).to_csv(
    OUT_DIR / "metrics_per_window.csv", index=False
)

pd.DataFrame(all_alias_rows).to_csv(
    OUT_DIR / "bit_aliasing_per_window.csv", index=False
)

pd.DataFrame(all_pair_rows).to_csv(
    OUT_DIR / "pairwise_hamming_distances_per_window.csv", index=False
)

print("\nPUF results by window")
print(pd.DataFrame(all_metric_rows).to_string(index=False))
print(f"\nAll results saved to: {OUT_DIR.resolve()}")

# Print the final metrics for each window.
results = pd.DataFrame(all_metric_rows)

print(f"\nFinal {RESPONSE_BITS}-bit PUF parameter results")

for _, row in results.iterrows():
    print(
        f"\nWindow: {row['window_start_ns']:g}-"
        f"{row['window_end_ns']:g} ns"
    )
    print(f"Sampling midpoint       : {row['midpoint_ns']:g} ns")
    print(f"Monte Carlo runs passed : {row['runs_passed']}/200")

    if row["metrics_calculated"]:
        print(f"Uniformity              : {row['uniformity_percent']:.4f}%")
        print(
            f"Mean Bit-Aliasing       : "
            f"{row['mean_bit_aliasing_percent']:.4f}%"
        )
        print(f"Uniqueness              : {row['uniqueness_percent']:.4f}%")
        print(f"Pairwise comparisons    : {int(row['pair_count'])}")
    else:
        print("Metrics                 : NOT CALCULATED")
        print(f"Reason                  : {row['reason']}")

print("\nDetailed results are saved in metrics_per_window.csv")

# Calculate average metrics across all valid windows.
results = pd.DataFrame(all_metric_rows)
valid = results[results["metrics_calculated"] == True]

print("\nAverage PUF metrics across valid windows")

if len(valid) == 0:
    print("No valid windows; average not calculated.")
else:
    print(f"Valid windows: {len(valid)}")
    print(
        f"Average Uniformity: "
        f"{valid['uniformity_percent'].mean():.6f}%"
    )
    print(
        f"Average Mean Bit-Aliasing: "
        f"{valid['mean_bit_aliasing_percent'].mean():.6f}%"
    )
    print(
        f"Average Uniqueness: "
        f"{valid['uniqueness_percent'].mean():.6f}%"
    )
