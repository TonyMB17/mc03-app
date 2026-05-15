"""MC-02 user-facing message rules.

Message states used by the indicator:

- ``cumple``: the component has the required valid service or a complete valid
  scheme already registered.
- ``programado``: the service is not yet required by current age and no
  out-of-window service was detected.
- ``pendiente_en_plazo``: the service is required or approaching and the record
  is still inside the normative window.
- ``incumplimiento_fuera_plazo``: no service was registered by the limit date,
  or a registered dose/service falls outside its allowed period.

Message composition still lives close to the component evaluator because the
messages depend on dose/window context. This module marks the intended boundary
for the next cleanup pass.
"""
