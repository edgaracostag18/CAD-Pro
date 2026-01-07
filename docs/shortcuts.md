# CAD Pro — Keyboard Shortcuts & Modal Behavior Spec (Blender Add-on)

This document defines the default **CAD Pro** keyboard shortcut layout and the required behavior for **Precision Transform** and **Sketch Mode**. It is intended to be copied into the repository as a single source of truth for keymap + interaction design.

---

## 0) Design Goals

- **CAD-first**: minimal shortcuts, maximum capability.
- **Cycling** is used wherever there are many options.
- **Precision Transform** supports:
  - Default pivot = **Origin**
  - Optional pivot/reference = **picked point** (vertex/edge/face point)
  - Axis constraints can be **multi-axis** (X then Y = constrain to both)
  - Repeated axis key cycles **Global → Local → Custom → Global**
  - **Custom axis** is defined by selecting **two points**
  - **Vector entry** overrides axis constraints and directly places the point/object

---

## 1) Core Shortcuts (Global in 3D View)

### Tool Activation / Exit
- **Ctrl + M** — Activate **CAD Pro Precision Transform** environment (available in normal Blender context)
- **Ctrl + K** — Toggle **CAD Pro Sketch Mode**
- **Ctrl + Q** — Exit current CAD Pro tool immediately (hard exit)
  - If a modal operation is running: **cancel + return to normal Blender state**

### Confirm / Cancel (when CAD Pro tools are active)
- **Enter** — Confirm / Apply current operation
- **LMB** — Confirm (only when tool supports click-to-place)
- **Esc** — Cancel current operation and revert
- **RMB** — Cancel (optional Blender-like behavior)

### Help / Visuals
- **F1** — Contextual shortcut overlay for active tool (in-tool cheat sheet)
- **Alt + Q** — Toggle CAD Pro overlays (axes/pivot/custom axis hints)

---

## 2) Precision Transform (Ctrl + M)

Precision Transform is a modal environment. Inside it, the active operation is selected via **G/R/S**.

### 2.1 Operation Selection
- **G** — Move / Translate
- **R** — Rotate
- **S** — Scale

### 2.2 Default Pivot / Reference Behavior
- Default pivot/reference is **Origin**.
- User can optionally select a reference point to use as the transform pivot.

### 2.3 Reference Point (Pick Pivot)
- **P** — Pick reference point (next click sets pivot/reference point)
- **Shift + P** — Pick and **lock** reference point for subsequent transforms

### 2.4 Pivot Mode Cycling
- **O** — Cycle pivot mode:
  1. Object Origin
  2. Selection Center
  3. Active Element
  4. Picked Reference

### 2.5 Axis Constraints (Multi-axis + Cycling)
Axes can be combined (e.g., X then Y constrains to both).

- **X** — Toggle X axis in constraint set
  - Repeating **X** cycles axis space: **Global → Local → Custom → Global**
- **Y** — Toggle Y axis in constraint set
  - Repeating **Y** cycles: **Global → Local → Custom → Global**
- **Z** — Toggle Z axis in constraint set
  - Repeating **Z** cycles: **Global → Local → Custom → Global**

**Multi-axis example:**
- Press **X**, then **Y** → constrain to X+Y simultaneously.

### 2.6 Plane Constraints (Exclude Axis)
- **Shift + X** — Constrain to **YZ** plane (exclude X)
- **Shift + Y** — Constrain to **XZ** plane (exclude Y)
- **Shift + Z** — Constrain to **XY** plane (exclude Z)

### 2.7 Clear Constraints
- **C** — Clear all axis/plane constraints (free transform)

### 2.8 Custom Axis Definition (Two-Point Pick)
Custom axis is entered by cycling any axis to **Custom** using repeated X/Y/Z.

**Behavior:**
1. When an axis is set to **Custom**, prompt: “Pick custom axis: Point 1”
2. **LMB** selects Point 1
3. Prompt: “Pick custom axis: Point 2”
4. **LMB** selects Point 2
5. Custom axis vector is normalized **(P2 - P1)**

**Custom axis management:**
- **U** — Re-pick custom axis (Point 1, Point 2)
- **Alt + U** — Clear custom axis (falls back to current Global/Local state)

### 2.9 Numeric Input (Precision Entry)
- Typing numbers begins input immediately (no field focus).
- Supports expressions: `12/3`, `25.4*2`, etc.
- **Backspace** — Edit numeric buffer
- **Ctrl + Backspace** — Clear numeric buffer
- **-** — Toggle negative

**Input mode:**
- **Tab** — Cycle: **Delta → Absolute → Delta**
  - Delta = relative movement/rotation/scale
  - Absolute = set final value when meaningful; otherwise behaves as delta

### 2.10 Vector Entry Override (Ignores Axis Constraints)
- **V** — Vector entry mode; accepts `x,y,z` (also allow `[x,y,z]`)
- Behavior:
  - Places the origin/selected reference point at the specified vector position
  - **Axis constraints are ignored** when vector entry is used

### 2.11 Snapping / Fine Control
- **Ctrl (hold)** — Temporary snap using current snap targets/settings
- **Shift (hold)** — Fine adjustment (reduced sensitivity)
- **Ctrl + Shift (hold)** — Snap + fine

Snap mode cycling (CAD Pro override):
- **N** — Cycle snap behavior:
  - Off → Increment → Vertex → Edge → Face → Off

### 2.12 Duplicate While Transforming
- **D** — Toggle “duplicate while transforming”
  - When enabled, creates a duplicate and continues the transform

### 2.13 Apply / Exit Within Environment
- **A** — Apply/commit (explicit apply; equivalent to Enter)
- **Q** — Return to idle inside CAD Pro (no active G/R/S modal), keep CAD Pro environment active
- **Ctrl + Q** — Hard exit CAD Pro immediately (cancel if modal)

### 2.14 Required Axis Cycling UX Examples
- **X (Global X)** → **X (Local X)** → **X (Custom X)** → **X (Global X)**
- Multi-axis + numeric:
  - `G` → `X` → `X` (Local X) → `Y` (add Y) → `12` → `Enter`
  - Moves 12mm along both constrained axes in their current spaces.
- Custom axis:
  - `G` → `Y` → `Y` (Local) → `Y` (Custom) → pick 2 points → `12` → `Enter`

---

## 3) Sketch Mode (Ctrl + K)

Sketch Mode creates/edits **mesh-based sketch geometry** (vertices/edges) which can later be filled/extruded/boolean’d by other tools. Sketching on a face should align sketch plane to that face (user faces the axis/face, selects face, enters Sketch Mode).

### 3.1 Sketch Session Control
- **Enter** — Done (finish sketch, remove constraints, leave 2D sketch mesh in 3D)
- **Esc** — Cancel sketch session (revert)
- **Ctrl + Q** — Hard exit Sketch Mode immediately

### 3.2 Primitive Creation
- **L** — Line (click-click)
- **P** — Polyline (continuous line; Enter ends)
- **R** — Rectangle (corner-corner)
- **Shift + R** — Rectangle mode cycle: corner-corner ↔ center-size
- **C** — Circle (center + radius; mesh-based)
- **A** — Arc (3-point; mesh-based)
- **O** — Offset

### 3.3 Edit Operations
- **T** — Trim (click segments to cut)
- **Shift + T** — Extend (toggle with Trim)
- **J** — Join / Weld endpoints
- **S** — Split segment
- **X** — Delete selected sketch geometry

### 3.4 Sketch Constraints (Assigned, Compact)
Geometric constraints:
- **H** — Horizontal
- **V** — Vertical
- **P** — Parallel
- **Shift + P** — Perpendicular
- **G** — Coincident (point-on-point / point-on-curve)
- **M** — Midpoint
- **N** — Concentric
- **E** — Equal
- **F** — Fix/Lock

Tangent:
- Preferred: **Alt + T** — Tangent (to avoid conflict with Trim/Extend)
  - (If cycling is preferred instead: T cycles Trim → Extend → Tangent)

Dimensioning:
- **D** — Dimension (contextual: distance/radius/angle based on selection)
- **Shift + D** — Force angle dimension

Constraint management:
- **Del** — Remove selected constraints (not geometry)
- **Ctrl + Del** — Remove constraints + geometry (hard delete selection)

---

## 4) Notes / Non-Goals (for this file)
- Face fill, extrusion, and boolean operations exist outside Sketch Mode scope.
- Sketch geometry is created directly as mesh; circle/arc vertex count is fixed once applied.
- Tool should provide a status line hint (constraints, axis space, numeric buffer, vector mode, etc.) for discoverability.

---
