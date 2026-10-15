from __future__ import annotations

import argparse
import sys
from pathlib import Path

from firm_bench.export import build_export_tree
from firm_bench.paths import DEFAULT_AREA
from firm_bench.run import run_area
from firm_bench.score import score_results
from firm_bench.validate import validate_area


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="firm-bench")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Validate tasks and gold for a practice area")
    p_val.add_argument("--area", default=DEFAULT_AREA)

    p_exp = sub.add_parser("export", help="Export a portable pack without gold")
    p_exp.add_argument("dest", type=Path)
    p_exp.add_argument("--area", default=DEFAULT_AREA)

    p_run = sub.add_parser("run", help="Run tasks against a system adapter")
    p_run.add_argument("--area", default=DEFAULT_AREA)
    p_run.add_argument(
        "--system",
        default="canned",
        choices=["canned", "openai", "openai-compatible"],
    )
    p_run.add_argument("--out", type=Path, default=None)

    p_score = sub.add_parser("score", help="Score a results directory")
    p_score.add_argument("results_dir", type=Path)
    p_score.add_argument("--area", default=DEFAULT_AREA)

    args = parser.parse_args(argv)

    if args.command == "validate":
        errors = validate_area(args.area)
        if errors:
            print("validate failed:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print(f"validate ok: {args.area}")
        return 0

    if args.command == "export":
        pack = build_export_tree(args.dest, args.area)
        print(f"exported {pack}")
        return 0

    if args.command == "run":
        out = run_area(args.area, system_id=args.system, out_dir=args.out)
        print(f"wrote runs to {out}")
        return 0

    if args.command == "score":
        card = score_results(args.results_dir, args.area)
        print(
            f"{'task_id':<22}{'rubric':>8}{'status':>8}{'hard_fail':>11}{'breach':>8}{'pass':>6}"
        )
        for case in card.cases:
            print(
                f"{case.task_id:<22}"
                f"{case.rubric_score:>8.2f}"
                f"{'ok' if case.status_ok else 'no':>8}"
                f"{'yes' if case.hard_fail else 'no':>11}"
                f"{'yes' if case.boundary_breach else 'no':>8}"
                f"{'yes' if case.effective_pass else 'no':>6}"
            )
        print(
            f"suite mean={card.suite_rubric_mean:.2f} "
            f"hard_fail={card.suite_hard_fail_count} "
            f"breach={card.suite_boundary_breach_count} "
            f"pass={card.suite_effective_pass_count}/{len(card.cases)}"
        )
        print(f"scorecard: {args.results_dir / 'scorecard.json'}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
