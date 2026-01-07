# CAD Transform Add-on — Engineering Specification

This document defines the **authoritative behavior and architecture** of the CAD Transform add-on.
All implementation decisions MUST conform to this specification unless explicitly revised.

This is a **build contract**, not marketing documentation.

---

## 1. Purpose

The CAD Transform add-on provides **deterministic, numeric, reference-driven transformations**
for Blender, comparable to CAD software.

It replaces viewport- and gizmo-dependent transforms with:
- Explicit numeric input
- Multi-axis constraints
- Origin- and reference-based pivots
- Custom coordinate systems
- Mesh-native operation

Supported operations:
- Move (Translate)
- Rotate
- Scale

---

## 2. Default Transform Rules

- All operations operate about the **Object Origin by default**
- Applies in both Object Mode and Edit Mode
- Geometry moves relative to the origin unless overridden

This default MUST remain consistent.

---

## 3. Pivot Override System (Optional)

The user may override the pivot point with:
- Vertex
- Edge point
- Face point

Rules:
- Pivot override is **tool-local**
- Does NOT modify Blender global pivot settings
- Pivot affects **position only**, not axis orientation
- User can clear pivot override at any time

World-space pivot point is used for all calculations.

---

## 4. Axis Constraint System

### 4.1 Active Axis Set

The tool maintains an **active axis set**:
