# Design and Analysis of a D Flip-Flop Based Physically Unclonable Function (PUF) Circuit

A transistor-level study of D Flip-Flop-based Physical Unclonable Functions (PUFs) for hardware authentication, using Cadence Virtuoso, the SCL 180 nm PDK, and Python-based statistical analysis.

## Overview

A **Physically Unclonable Function (PUF)** uses small, inherent manufacturing variations in integrated circuits to produce device-specific responses. These responses can support hardware identification and authentication without requiring a permanently stored secret key.

This project studies conventional and symmetric D Flip-Flop PUF architectures, evaluates their responses under process variation and operating-condition changes, and explores a modified circuit architecture. The goal is to understand the trade-offs among response uniqueness, reliability, uniformity, and bit aliasing.

## Objectives

- Study conventional and symmetric DFF-PUF architectures.
- Implement and simulate transistor-level circuits in Cadence Virtuoso.
- Examine transient behaviour and the PUF start-up response.
- Evaluate process mismatch using Monte Carlo simulations.
- Assess response sensitivity across process, voltage, and temperature (PVT) conditions.
- Analyse exported simulation data using Python.
- Develop a full-custom layout and perform physical verification and parasitic-aware analysis.
- Compare the symmetric design with a modified DFF-PUF architecture.

## Design Approach

The project follows this workflow:

1. **Circuit study:** Review conventional and symmetric DFF-PUF architectures.
2. **Schematic implementation:** Build the transistor-level circuits using the SCL 180 nm PDK.
3. **Transient simulation:** Verify normal DFF operation and PUF-mode behaviour.
4. **Variation analysis:** Run Monte Carlo simulations to model chip-to-chip process mismatch.
5. **PVT analysis:** Evaluate response behaviour over process corners, supply-voltage changes, and temperature variations.
6. **Data export:** Export simulated responses to CSV files.
7. **Statistical evaluation:** Use Python to calculate PUF performance metrics.
8. **Physical implementation:** Create a full-custom layout, run DRC/LVS checks, extract parasitics, and conduct post-layout simulations.
9. **Architecture comparison:** Compare the symmetric DFF-PUF with the modified circuit.

## Tools and Technologies

| Tool / Technology | Purpose |
|---|---|
| Cadence Virtuoso | Transistor-level schematic design and circuit simulation |
| SCL 180 nm PDK | CMOS device models and process design rules |
| ADE XL | Monte Carlo and PVT simulation setup |
| Python | Statistical analysis of PUF responses |
| NumPy / pandas | Numerical and tabular data processing |
| CSV | Export and transfer of simulation data |
| Mentor Graphics Calibre | DRC, LVS, and parasitic extraction |

## Simulation Setup

The project report describes the following simulation setup:

| Parameter | Setup |
|---|---|
| Process technology | SCL 180 nm |
| Nominal supply voltage | 1.8 V |
| Temperature range | −40 °C to 125 °C |
| Monte Carlo runs | 200 |
| Pre-layout response widths | 1-bit and 8-bit |
| Post-layout response width | 128-bit |
| Statistical analysis | Python |
| Physical verification | Calibre DRC/LVS |

The report also describes PVT sweeps using supply voltages from 1.1 V to 1.65 V and process corners including FF, FS, SF, and SS.

## PUF Performance Metrics

The exported response data is evaluated using four key metrics:

- **Uniqueness:** Measures how different the responses of different simulated chip instances are for the same challenge. An ideal average inter-chip Hamming distance is approximately 50%.
- **Reliability:** Measures whether the same chip produces a consistent response under changed operating conditions. An ideal reliability is 100%.
- **Uniformity:** Measures the proportion of 1s in a response. An ideal value is approximately 50%.
- **Bit aliasing:** Measures how often a particular response-bit position is 1 across simulated chip instances. An ideal value is approximately 50%.

Python scripts process the CSV data exported from Cadence and calculate these metrics for the selected response width and operating conditions.

## Circuit Architectures Studied

### 1. Conventional DFF-PUF
Used as a baseline to understand how structural asymmetry in a conventional flip-flop can bias the start-up response.

### 2. Symmetric DFF-PUF
A symmetric architecture is studied in which balancing circuitry helps equalise the latch paths during PUF operation. The circuit supports normal DFF operation as well as PUF response generation.

### 3. Modified DFF-PUF
A modified circuit is explored and compared against the symmetric architecture. The comparison considers circuit structure, transistor count, and PUF performance metrics.

## Physical Design and Verification

The project extends beyond schematic simulation to full-custom layout:

- Layout created in Cadence Virtuoso using the SCL 180 nm PDK.
- Matched latch halves laid out with attention to device sizing, orientation, and routing symmetry.
- Design Rule Check (DRC) and Layout Versus Schematic (LVS) performed using Calibre.
- RC parasitic extraction used to prepare the design for post-layout simulation.
- Post-layout Monte Carlo responses analysed using the Python evaluation workflow.


