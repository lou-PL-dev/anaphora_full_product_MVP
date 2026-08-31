# Cost model

`cost_model.py` computes the numbers in `../cost_timeline_estimate.md`.
Reuses `anaphora_backend`'s own environment (imports the real system
prompts straight from its chain modules) — no separate install needed
beyond `anaphora_backend/requirements.txt`.

```bash
cd anaphora_backend && pip install -r requirements.txt   # if not already done
cd ../product_document/cost_estimate
python cost_model.py
```

No API key or database needed — this is offline arithmetic over the real
prompt text plus the labeled assumptions in the script, not a live call.
