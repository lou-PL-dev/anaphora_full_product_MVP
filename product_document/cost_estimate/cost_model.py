"""
Anaphora — Cost & Timeline Estimate: cost calculator.

Computes a grounded per-user-journey LLM cost estimate by combining:
- Character counts of the real system prompts shipped in anaphora_backend
  — imported directly from the actual chain modules, not paraphrased or
  guessed at — converted to an approximate token count (see count_tokens).
- Clearly labeled ASSUMPTIONS for everything that varies per real user
  (message length, conversation length, etc.) — anything not measured from
  real code lives in the ASSUMPTIONS dict below, nowhere else, so it's all
  auditable in one place.
- OpenAI's published per-token pricing (see PRICING below for sourcing and
  its caveat).

Run: python cost_model.py
"""
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "anaphora_backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.chains.conversation_chain import SYSTEM_PROMPT as CONVO_SYSTEM_PROMPT
from app.chains.extraction_chain import EXTRACTION_SYSTEM_PROMPT
from app.chains.discovery_chain import SYNTHESIS_SYSTEM_PROMPT
from app.chains.matching_chain import MATCH_SYSTEM_PROMPT

# --- Pricing ($ per 1M tokens) ----------------------------------------------
# Sourced via web search against aggregator pricing pages (cloudzero.com,
# lmmarketcap.com, openrouter.ai) on 2026-08-31 — OpenAI's own pricing page
# (platform.openai.com/docs/pricing) was not directly reachable from this
# environment (network egress restriction blocked it), so these numbers
# could NOT be cross-checked against the canonical source. Spot-check
# against OpenAI's own pricing page before treating this as final.
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}

# --- Hosting ($/month, fixed regardless of usage within a tier) ------------
# Sourced via web search (Render/Netlify's own pricing pages return
# JavaScript-rendered content this environment's fetch tool couldn't parse
# directly, so these come from aggregator pages current as of 2026-08-31)
# — spot-check against render.com/pricing and netlify.com/pricing directly
# before treating this as final.
HOSTING = {
    "render_web_free": 0.0,        # spins down after ~15 min idle, ~50s cold start on wake
    "render_web_starter": 7.0,     # always-on, 0.5 vCPU / 512MB
    "render_postgres_free": 0.0,   # NOTE: expires 30 days after creation — needs monitoring
    "render_postgres_basic": 6.0,  # Basic-256mb, persists indefinitely
    "netlify_free": 0.0,           # credit-based since Apr 2026: 300 credits/mo, ~15GB effective bandwidth, no auto-recharge
    "netlify_personal": 9.0,       # 1,000 credits/mo
}

HOSTING_FREE_TOTAL = HOSTING["render_web_free"] + HOSTING["render_postgres_free"] + HOSTING["netlify_free"]
HOSTING_PAID_TOTAL = HOSTING["render_web_starter"] + HOSTING["render_postgres_basic"] + HOSTING["netlify_personal"]


def count_tokens(text: str) -> int:
    """Approximates token count using OpenAI's own published rule of thumb
    (~4 characters per token for English text). tiktoken's exact BPE
    tokenizer needs to download its vocab file from
    openaipublic.blob.core.windows.net, which this sandboxed environment's
    network policy blocks — the character counts fed into this ARE exact
    (measured directly from the real prompt strings imported above), only
    the chars-to-tokens conversion is an approximation. Good enough for
    order-of-magnitude cost estimation; once real conversations are
    happening, LangSmith's traces (already wired in — see
    anaphora_backend/README.md) report EXACT real token usage per call and
    should replace this approximation entirely."""
    return max(1, len(text) // 4)


# --- Assumptions -------------------------------------------------------------
# Everything here is a stated assumption, not a measurement. Conversation
# turn count is bounded by MINIMUM_USER_TURNS=3 / MAXIMUM_USER_TURNS=12 in
# conversation_chain.py; 6 is a middle-of-the-range guess pending real usage
# data (no production traffic exists yet to measure this from).
ASSUMPTIONS = {
    "avg_user_turns_per_conversation": 6,
    "avg_user_message_tokens": 40,       # ~30 words
    "avg_ai_reply_tokens": 45,           # mirror + one question, per the "one or two sentences" prompt rule
    "extraction_output_tokens": 600,     # ideal_partner + me blueprints + narrative, structured
    "discovery_answers_tokens": 60,
    "discovery_output_tokens": 25,
    "match_candidates_per_request": 5,   # k in matching_router.get_matches's default
    "match_explanation_output_tokens_per_candidate": 35,
    "candidate_text_tokens": 120,        # narrative + signal labels, embedded text length
}


def cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    p = PRICING[model]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000


def conversation_cost() -> tuple[float, dict]:
    """The conversation chain resends the ENTIRE message history every turn
    (conversation_chain._to_langchain_messages) — cost grows with the SQUARE
    of turn count, not linearly, since each turn's input token count
    includes every prior turn. This loop reflects that exactly; it's the
    single biggest cost-shape finding in this estimate (see the writeup)."""
    turns = ASSUMPTIONS["avg_user_turns_per_conversation"]
    system_tokens = count_tokens(CONVO_SYSTEM_PROMPT)
    total_input = 0
    total_output = 0
    history_tokens = 0
    for _turn in range(turns):
        history_tokens += ASSUMPTIONS["avg_user_message_tokens"]
        total_input += system_tokens + history_tokens
        total_output += ASSUMPTIONS["avg_ai_reply_tokens"]
        history_tokens += ASSUMPTIONS["avg_ai_reply_tokens"]
    return cost("gpt-4o", total_input, total_output), {
        "turns": turns, "input_tokens": total_input, "output_tokens": total_output,
    }


def extraction_cost() -> tuple[float, dict]:
    turns = ASSUMPTIONS["avg_user_turns_per_conversation"]
    transcript_tokens = turns * (ASSUMPTIONS["avg_user_message_tokens"] + ASSUMPTIONS["avg_ai_reply_tokens"])
    input_tokens = count_tokens(EXTRACTION_SYSTEM_PROMPT) + transcript_tokens
    output_tokens = ASSUMPTIONS["extraction_output_tokens"]
    return cost("gpt-4o-mini", input_tokens, output_tokens), {
        "input_tokens": input_tokens, "output_tokens": output_tokens,
    }


def discovery_cost() -> tuple[float, dict]:
    input_tokens = count_tokens(SYNTHESIS_SYSTEM_PROMPT) + ASSUMPTIONS["discovery_answers_tokens"]
    output_tokens = ASSUMPTIONS["discovery_output_tokens"]
    return cost("gpt-4o-mini", input_tokens, output_tokens), {
        "input_tokens": input_tokens, "output_tokens": output_tokens,
    }


def matching_cost() -> tuple[float, dict]:
    """One /matches request: one query-side embedding + one generation call
    covering k retrieved candidates at once (matching_chain.find_matches)."""
    k = ASSUMPTIONS["match_candidates_per_request"]
    embed_cost = cost("text-embedding-3-small", ASSUMPTIONS["candidate_text_tokens"])
    candidates_block_tokens = k * 40  # "candidate_id: ...\nshared_signals: ..." per candidate
    gen_input = count_tokens(MATCH_SYSTEM_PROMPT) + candidates_block_tokens + 100  # + user narrative
    gen_output = k * ASSUMPTIONS["match_explanation_output_tokens_per_candidate"]
    gen_cost = cost("gpt-4o-mini", gen_input, gen_output)
    return embed_cost + gen_cost, {"gen_input": gen_input, "gen_output": gen_output}


def candidate_ingestion_cost_per_candidate() -> float:
    """One-time cost, NOT per active user — seeding the synthetic candidate
    pool (rag_demo/ingest_candidates.py): a narrative-writing call + an
    extraction call (same shape as a real extraction, minus the multi-turn
    conversation) + one embedding."""
    narrative_gen = cost("gpt-4o", 300, 120)
    extraction = cost("gpt-4o-mini", count_tokens(EXTRACTION_SYSTEM_PROMPT) + 150, 300)
    embedding = cost("text-embedding-3-small", ASSUMPTIONS["candidate_text_tokens"])
    return narrative_gen + extraction + embedding


def main():
    conv_c, conv_d = conversation_cost()
    ext_c, _ = extraction_cost()
    disc_c, _ = discovery_cost()
    match_c, _ = matching_cost()
    journey_cost = conv_c + ext_c + disc_c + match_c

    print("=== Real system prompt sizes (exact chars, approximate tokens) ===")
    print(f"  conversation SYSTEM_PROMPT:      {count_tokens(CONVO_SYSTEM_PROMPT):>4} tokens")
    print(f"  extraction EXTRACTION_SYSTEM_PROMPT: {count_tokens(EXTRACTION_SYSTEM_PROMPT):>4} tokens")
    print(f"  discovery SYNTHESIS_SYSTEM_PROMPT: {count_tokens(SYNTHESIS_SYSTEM_PROMPT):>4} tokens")
    print(f"  matching MATCH_SYSTEM_PROMPT:    {count_tokens(MATCH_SYSTEM_PROMPT):>4} tokens")

    print(f"\n=== Per-user-journey cost (conversation + extraction + Discovery + one /matches call, {conv_d['turns']} turns) ===")
    print(f"  conversation (gpt-4o):     ${conv_c:.5f}")
    print(f"  extraction (gpt-4o-mini):  ${ext_c:.5f}")
    print(f"  discovery (gpt-4o-mini):   ${disc_c:.5f}")
    print(f"  matching (embed + mini):   ${match_c:.5f}")
    print(f"  TOTAL per user journey:    ${journey_cost:.5f}")

    per_candidate = candidate_ingestion_cost_per_candidate()
    print(f"\n=== One-time candidate pool seeding ===")
    print(f"  per candidate: ${per_candidate:.5f}   x 50 candidates = ${per_candidate * 50:.4f}")

    print("\n=== Fixed hosting costs ($/month) ===")
    print(f"  Free tier (current):  ${HOSTING_FREE_TOTAL:.2f}/mo — but Render's free Postgres expires 30 days after creation")
    print(f"  Paid tier (recommended once traffic is real): ${HOSTING_PAID_TOTAL:.2f}/mo")
    print(f"    Render web Starter:        ${HOSTING['render_web_starter']:.2f}")
    print(f"    Render Postgres Basic:     ${HOSTING['render_postgres_basic']:.2f}")
    print(f"    Netlify Personal:          ${HOSTING['netlify_personal']:.2f}")

    print("\n=== Total monthly cost at different new-user scales (LLM + hosting) ===")
    print(f"  {'new users/mo':>13}  {'LLM only':>10}  {'+ free hosting':>15}  {'+ paid hosting':>15}")
    for n in (100, 1_000, 10_000):
        llm = journey_cost * n
        print(f"  {n:>13}  ${llm:>9.2f}  ${llm + HOSTING_FREE_TOTAL:>14.2f}  ${llm + HOSTING_PAID_TOTAL:>14.2f}")


if __name__ == "__main__":
    main()
