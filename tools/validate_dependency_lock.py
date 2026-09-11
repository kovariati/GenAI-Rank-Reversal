#!/usr/bin/env python3
"""Fail-closed check for the fully pinned direct + transitive runtime lock."""
from __future__ import annotations
from pathlib import Path
import importlib.metadata as im
import re
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT=Path(__file__).resolve().parents[1]

def parse_lock(path: Path) -> dict[str,str]:
    pins={}
    for raw in path.read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if not line or line.startswith('#'): continue
        m=re.fullmatch(r'([A-Za-z0-9_.-]+)==([^;\s]+)',line)
        if not m: raise AssertionError(f'Lock entry must be exact package==version: {line}')
        pins[canonicalize_name(m.group(1))]=m.group(2)
    return pins

def direct_names(path: Path) -> list[str]:
    out=[]
    for raw in path.read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if not line or line.startswith('#'): continue
        out.append(canonicalize_name(Requirement(line).name))
    return out

pins=parse_lock(ROOT/'requirements-lock.txt')
direct=direct_names(ROOT/'requirements.txt')
missing_direct=[n for n in direct if n not in pins]
assert not missing_direct, f'Direct dependencies missing from lock: {missing_direct}'

# Verify the installed environment exactly matches each lock pin. In CI this runs
# immediately after installing requirements-lock.txt.
for name,expected in pins.items():
    actual=im.version(name)
    assert actual==expected, f'{name}: installed {actual}, lock {expected}'

# Traverse runtime dependency metadata from direct requirements. Requirements
# guarded by extras are ignored unless they also apply without an extra.
seen=set(); stack=list(direct); missing=[]; incompatible=[]
while stack:
    name=canonicalize_name(stack.pop())
    if name in seen: continue
    seen.add(name)
    dist=im.distribution(name)
    for raw in dist.requires or []:
        req=Requirement(raw)
        if req.marker and not req.marker.evaluate({'extra':''}):
            continue
        dep=canonicalize_name(req.name)
        if dep not in pins:
            missing.append((name,dep,raw))
            continue
        installed=im.version(dep)
        if req.specifier and installed not in req.specifier:
            incompatible.append((name,dep,installed,str(req.specifier)))
        if dep not in seen: stack.append(dep)
assert not missing, f'Transitive dependencies missing from lock: {missing}'
assert not incompatible, f'Locked versions violate dependency metadata: {incompatible}'

# Prevent irrelevant environment packages from silently turning the file into a
# machine-specific pip freeze. Every pin must be reachable from a direct runtime dependency.
extra=sorted(set(pins)-seen)
assert not extra, f'Lock contains packages outside the runtime dependency closure: {extra}'
print(f'dependency_lock: PASS ({len(direct)} direct; {len(seen)} direct+transitive pins)')
