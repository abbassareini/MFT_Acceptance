# MFT Acceptance

Geometrical acceptance / pseudo-efficiency (Peff) study of the **Muon Forward Tracker (MFT)** of the ALICE experiment at CERN, developed as part of an M2 internship in the MFT team.

## What it does

The MFT has 10 detection layers (5 disks x 2 faces). For every valid layer configuration (5 to 10 layers, with the track-seeding constraint that the last layers lie on disks 3-4), the pipeline:

1. Computes a per-chip **pseudo-efficiency**: the fraction of straight tracks from the interaction point through a reference chip that land on active silicon on every required layer (dead/decommissioned chips are subtracted).
2. Aggregates the geometry into per-**Readout-Unit (RU) weights**: each RU zone's share of the tracks seeded on the configuration's last layer.
3. Plots the RU weights versus azimuthal angle (phi) for each disk (`Acceptance_Results/z_0/Weights_D*.png`).

## Repository layout

| Path | Content |
|---|---|
| `Acceptance_Computation_abbas.ipynb` | Main pipeline, cells documented, run top to bottom |
| `Library/` | Helper notebooks loaded via `%run` |
| `chipPositionsnew.txt` | Chip geometry (ID, half/disk/layer/zone, x/y/z) |
| `Acceptance_Dataframes/` | Generated per-configuration acceptance data and RU weights |
| `RU_Weights_GroundTruth/` | Inherited reference weight files used for validation (disks 0-1) |
| `Acceptance_Results/` | Output plots |

## Requirements

Python 3 with `numpy`, `pandas`, `matplotlib`. Runs in Jupyter Notebook (tested on Windows/Anaconda).

## Notes

- The core Peff computation was validated against inherited reference outputs (byte-identical).
- The RU-weight generator reconstructs a lost aggregation step; it is validated to ~1-2% against the surviving reference files (disks 0-1), which are overlaid bit-exactly where they exist.
- This project builds on earlier work by a previous MFT intern; see the thesis/report for full attribution.

## Contact

abbassareinii@gmail.com
