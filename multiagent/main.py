"""
main.py — End-to-End Pipeline Execution
Lab 2: Multi-Agent Orchestration with LangGraph + Azure AI Foundry

Runs the full multi-agent remittance processing pipeline:
  1. Feeds a sample remittance document into the graph
  2. Streams agent outputs as the pipeline executes
  3. Handles the HITL interrupt (simulated human approval)
  4. Prints the final results and matching report
"""

import json
from graph import build_graph
from langgraph.types import Command


# ── Sample Remittance Documents ─────────────────────────────────────────
SAMPLE_DOCUMENT_GOOD = """
REMITTANCE ADVICE
=================
From:      Contoso Ltd (Account: ACC-98765)
Date:      August 10, 2026
Reference: REM-2026-001

Payment Details:
  - Invoice INV-1001:  $5,000.00
  - Invoice INV-1002:  $7,500.00
  - Invoice INV-1003:  $3,250.00

Total Payment: $15,750.00
Currency: USD

Notes: Payment for Q3 professional services.
"""

SAMPLE_DOCUMENT_BAD = """
REMITTANCE ADVICE
=================
From:      Contoso Ltd (Account: ACC-98765)
Date:      August 10, 2026
Reference: REM-2026-001

Payment Details:
  - Invoice INV-1001:  $5,000.00
  - Invoice INV-1002:  $5,000.00
  - Invoice INV-1003:  $1,250.00

Total Payment: $11,250.00
Currency: USD

Notes: Payment for Q3 professional services (Short Payment).
"""


def run_orchestration():
    """Execute the multi-agent orchestration pipeline end-to-end."""

    print("=" * 70)
    print("   MULTI-AGENT REMITTANCE PROCESSING ORCHESTRATION")
    print("   LangGraph + Azure AI Foundry")
    print("=" * 70)

    print("\n📝 Select a document to test:")
    print("   [1] Perfect Match (Auto-Approve)")
    print("   [2] Variance / Short Payment (Triggers HITL Reject)")
    print("   [3] Type your own custom document")
    
    choice = input("\nEnter 1, 2, or 3: ").strip()
    
    if choice == "2":
        print("\n[Using Sample 2: Variance / Reject...]")
        user_document = SAMPLE_DOCUMENT_BAD
    elif choice == "3":
        print("\n📝 Enter your remittance document text below.")
        print("   (Type 'END' on a new line when finished)")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "END": break
                lines.append(line)
            except EOFError: break
        user_document = "\n".join(lines).strip()
    else:
        print("\n[Using Sample 1: Perfect Match...]")
        user_document = SAMPLE_DOCUMENT_GOOD

    # ── Build the graph ──────────────────────────────────────────────
    graph = build_graph()

    # ── Initial state ────────────────────────────────────────────────
    initial_state = {
        "messages":          [],
        "raw_document":      user_document,
        "remittance_data":   None,
        "payment_records":   None,
        "match_results":     None,
        "matching_report":   None,
        "current_agent":     "none",
        "next_agent":        "",
        "routing_history":   [],
        "confidence_scores": {},
        "error_log":         [],
        "retry_count":       0,
        "requires_hitl":     False,
        "hitl_decision":     None,
        "final_output":      None,
    }

    config = {"configurable": {"thread_id": "remittance-001"}}

    # ── Phase 1: Run until first interrupt (HITL) ────────────────────
    print("\n[Phase 1/3] Starting orchestration pipeline...\n")

    for event in graph.stream(initial_state, config, stream_mode="updates"):
        for node_name, node_output in event.items():
            if "messages" in node_output and node_output["messages"]:
                for msg in node_output["messages"]:
                    print(f"  {msg.content}")
        print()

    # ── Phase 2: Handle HITL interrupt ───────────────────────────────
    current_state = graph.get_state(config)

    if current_state.next:
        print("\n[Phase 2/3] Pipeline PAUSED for Human-in-the-Loop review.")
        print(f"            Pending node: {current_state.next}")
        print("  " + "─" * 50)
        print("  [Human Reviewer] Inspecting matching results...")
        
        # Interactive HITL prompt
        user_decision = input("  [Human Reviewer] Type 'approve' to proceed or 'reject' to stop: ").strip().lower()
        resume_val = "approved" if user_decision == "approve" else "rejected"
        
        print(f"  [Human Reviewer] Decision: {resume_val.upper()} ✓")
        print("  " + "─" * 50)

        # Resume the graph — passes through the HITL node and
        # continues back to the Supervisor for finalisation.
        for event in graph.stream(
            Command(resume=resume_val), config, stream_mode="updates"
        ):
            for node_name, node_output in event.items():
                if "messages" in node_output and node_output["messages"]:
                    for msg in node_output["messages"]:
                        print(f"  {msg.content}")
            print()
    else:
        print("\n[Phase 2/3] No HITL interrupt — pipeline completed automatically.")

    # ── Phase 3: Print final results ─────────────────────────────────
    final_state = graph.get_state(config)

    print("\n[Phase 3/3] Pipeline Complete!")
    print("=" * 70)
    print("\n📊 FINAL RESULTS:\n")
    print(f"  Routing History    : {final_state.values.get('routing_history', [])}")
    print(f"  Confidence Scores  : {json.dumps(final_state.values.get('confidence_scores', {}), indent=4)}")
    print(f"  Errors             : {final_state.values.get('error_log', [])}")
    print(f"  HITL Required      : {final_state.values.get('requires_hitl', False)}")
    print(f"  HITL Decision      : {final_state.values.get('hitl_decision', 'N/A')}")

    report = final_state.values.get("matching_report")
    if report:
        print(f"\n  📋 Matching Report:")
        print(f"     Remittance ID      : {report.get('remittance_id')}")
        print(f"     Total Matched      : {report.get('total_matched')}")
        print(f"     Total Unmatched    : {report.get('total_unmatched')}")
        print(f"     Amount Matched     : ${report.get('total_amount_matched', 0):,.2f}")
        print(f"     Overall Confidence : {report.get('overall_confidence')}")

    print("\n" + "=" * 70)
    print("  ✅ Lab 2 — Multi-Agent Orchestration Skeleton — COMPLETE")
    print("=" * 70)

    return final_state


if __name__ == "__main__":
    run_orchestration()
