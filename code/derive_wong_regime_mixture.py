#!/usr/bin/env python3
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "results").exists() else HERE.parent
source = ROOT / "results" / "wong_raw_group_means.csv"
out = ROOT / "results" / "wong_regime_mixture_threshold.csv"
rows = list(csv.DictReader(source.open(encoding="utf-8-sig")))
orig = {r["design"]: r for r in rows if r["outcome"] == "Originality"}
ua = float(orig["Unrestricted ChatGPT"]["assisted_task_mean"])
la = float(orig["Learner-first AI"]["assisted_task_mean"])
ui = float(orig["Unrestricted ChatGPT"]["independent_task_mean"])
li = float(orig["Learner-first AI"]["independent_task_mean"])
DA = ua - la
DI = ui - li
w = -DI / (DA - DI)
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["outcome","scale","intervention_A","intervention_B","assisted_A_mean","assisted_B_mean","independent_A_mean","independent_B_mean","D_A","D_I","w_star","interpretation"])
    writer.writerow(["Originality","raw Wong rating scale","Unrestricted ChatGPT","Learner-first AI",ua,la,ui,li,DA,DI,w,"Illustrative same-score-scale composition threshold; not a recommended pooled causal estimand."])
print(f"D_A={DA:.12f}; D_I={DI:.12f}; w_star={w:.12f}")
