# Candidate profile photos

Drop 5 photos here, named:

| filename | who |
|---|---|
| `m1.jpg` | male-presenting |
| `m2.jpg` | male-presenting |
| `f1.jpg` | female-presenting |
| `f2.jpg` | female-presenting |
| `a1.jpg` | androgynous-presenting |

Spec: square crop (e.g. 800x800), JPG or WEBP, reasonably compressed.

These map to 5 of the 50+ synthetic candidates in the RAG matching pool —
the rest of the pool falls back to a generic initials avatar in the UI, no
photo needed. Served as static assets by Netlify at `/candidates/<file>`,
referenced by `candidates.photo_url` in the backend once the matching
feature is implemented — see the RAG matching plan discussed in chat.

This README is a placeholder so the folder exists in git before any real
images are added — delete it once real photos are in place, or leave it,
doesn't matter either way.
