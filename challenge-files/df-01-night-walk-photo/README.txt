=== DF-01: The Night Walk Photo ===

Narrative:
A Directorate field agent posted a photo. The Directorate tried to 'sanitize' it,
but operational metadata still leaks through.

Files:
- night-walk.jpg

Objective:
- Recover BOTH values from the file's metadata:
  - KEY:<challenge key>
  - FLAG:TDHCTF{exif_shadow_unit}

Tips:
- Start with metadata tools (EXIF/XMP/comments).
- If your tool shows multiple contradictory timestamps, that's intentional.
