=== DF-01: The Night Walk Photo ===

Narrative:
A Directorate field agent posted a photo. The Directorate tried to 'sanitize' it,
but operational metadata still leaks through.

Files:
- night-walk.jpg

Objective:
- Recover BOTH values hidden in the photo metadata/comment blob:
  - KEY:<challenge key>
  - FLAG:TDHCTF{exif_shadow_unit}

Hints (in-story):
- The Directorate doesn’t just delete evidence — it repackages it.
- Start where investigators start: metadata, comments, and “harmless” fields.
- If you find a long wrapped blob, treat it like a standard transport wrapper.
- Contradictory timestamps are intentional misdirection; focus on what repeats.
