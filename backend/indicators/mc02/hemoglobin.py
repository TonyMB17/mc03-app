"""MC-02 hemoglobin dosage rules.

Technical sheet summary kept close to code:

- Valid codes: ``85018``, ``85018.01`` and ``85031``.
- The dosage must be performed between 170 and 209 days of age.
- From 210 to 364 days, the child must already have one valid hemoglobin
  dosage in that window.

The current implementation evaluates this component with the operative Excel
flag ``Obs_dh1`` and displays the detail columns ``fecha_1DH``, ``edad_1DH``
and ``CIE_DH_1DH`` for traceability. This module marks the boundary for future
raw-attendance recalculation of the 170-209 day window.
"""
