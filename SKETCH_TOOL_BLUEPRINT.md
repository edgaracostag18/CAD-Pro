# Sketch Tool Blueprint (Mesh-First, Constraint-Assisted, Non-Parametric Output)

## Purpose
Provide a CAD-like 2D sketch workflow inside Blender that:
- Creates a NEW mesh object consisting of vertices + edges in a locked sketch plane.
- Supports temporary CAD constraints and editable dimensions DURING the sketch session.
- On "Done", removes all constraints/solver state and leaves a plain 2D edge sketch in 3D space.
- Does NOT include face fill, extrude, boolean, or solid modeling operations (use Blender tools after).

License: GPL (project is open source).

---

## User Workflow (How it is used)
### A) Sketch on a face
1) User orients the view toward the target face (faces the axis/face).
2) User selects the face.
3) User enables Sketch Tool.
4) Sketch plane locks to the selected face orientation (rotation locked).
5) Tool creates a NEW sketch mesh object aligned to that face (optionally slight normal offset to prevent z-fighting).
6) User draws points/lines/circles/curves, applies constraints/dimensions as needed.
7) User clicks "Done" -> constraints removed; mesh edges remain.

### B) Sketch on an axis / view plane
1) User orients the view to the desired axis (front/right/top or arbitrary view).
2) User enables Sketch Tool (no face required).
3) Sketch plane locks to the view orientation (rotation locked).
4) Tool creates a NEW sketch mesh object in that plane.
5) User sketches, constrains, then Done removes constraints leaving mesh edges.

---

## Output & Object Rules
- Starting a sketch always creates a NEW mesh object (e.g., "Sketch.001").
- The sketch object is intended to be joined/boolean’d/used later in Blender.
- On Done: the object must remain as a normal mesh with only verts/edges (2D in a plane).

---

## Sketch Plane (Locked Orientation)
- Plane is determined ON TOOL START:
  - If a face is selected: plane = face plane (origin at face center or cursor; orientation from face normal + stable tangent).
  - Else: plane = current view plane orientation.
- Orientation is locked during the session (no drifting).
- Optional: small offset along normal when sketching on a face to avoid z-fighting.

---

## Geometry Types (Mesh-First)
All geometry is created as mesh vertices/edges immediately.

### Entities (internal session model)
Maintain a lightweight session graph that maps to mesh indices:
- Point (PointID -> mesh vertex index)
- Line segment (PointID A, PointID B -> mesh edge)
- Circle / Arc / Curve (represented as polylines in mesh; also tracked as a grouped entity for constraints)

### Circles and Curves
- Create circles/curves as mesh polylines with user-selected segment count at creation time.
- Once constraints are applied to a circle/curve entity: SEGMENT COUNT IS FROZEN (cannot be changed after).
- Constraints should operate on stable entity IDs (not raw vertex indices alone).

---

## Constraints (Temporary, Session-Only)
Constraints exist only while sketching. They are deleted on Done.

### Minimum constraint set (MVP)
- Coincident (point-point, point-on-line)
- Horizontal / Vertical (relative to sketch plane axes)
- Distance (dimension) between two points
- Fixed point (locks a point)
- Equal length (line-line)

### CAD-grade constraint set (target)
- Parallel, Perpendicular
- Angle (dimension) between two lines
- Midpoint
- Symmetry
- Concentric (circle-circle)
- Tangent (line-circle, circle-circle) [if implemented, must be reliable]
- Radius / Diameter (dimension) for circles/arcs

### Dimensional Editing
- Dimensions store numeric values (unit-aware) and can be edited during the session.
- Editing a dimension triggers a re-solve and updates the sketch mesh.

### Solve Feedback
During the session, show solve state:
- OK / Under-constrained / Over-constrained / Failed
- Failed constraints should be identifiable (list + highlight).

---

## Input & Controls (Session UX)
- Tool runs as a modal sketch session with:
  - Place point
  - Draw line (click-click)
  - Create circle/arc/curve (dedicated sub-modes)
  - Apply constraint tools (selected entities -> apply)
  - Edit dimension values
  - Confirm/Done and Cancel

Suggested minimal controls (exact hotkeys may be defined elsewhere):
- LMB: place/select
- Enter: confirm numeric input / accept edit
- Esc: cancel current action
- Done button: finalize sketch (removes constraints, leaves mesh)

Numeric input:
- Accept unit-aware values (e.g., 10mm, 1/4in) and basic expressions.
- Used for distance/angle/radius constraints and optional guided drawing.

---

## Finalization Behavior
### Done
- Perform final solve (if applicable).
- Write final point positions to mesh vertices.
- Remove ALL session constraint/solver data and internal graph metadata.
- Leave a plain mesh object with edges/verts only.

### Cancel
- Revert changes made during the current sketch session.
- Remove the created sketch object if it was created by this session (unless explicitly saved).

---

## Non-Goals (Explicit)
- No face fill, extrude, boolean, or solid creation in this tool.
- No post-Done parametric edits (constraints are removed; sketch becomes “dumb” geometry).

---

## Acceptance Criteria (Must Pass)
1) Start sketch on face: mesh sketch object aligns to face plane; rotation stays locked.
2) Start sketch on view: mesh sketch object aligns to view plane; rotation stays locked.
3) Draw points/lines produces correct mesh verts/edges in-plane.
4) Apply distance constraint adjusts geometry predictably during session.
5) Circles created with N segments; after constraints applied, N cannot be changed.
6) Done leaves a normal mesh object with edges only and no remaining constraint data.
