"""
Aurora Benchmark Launcher

Simple script to run Aurora evaluation (works with A2A or legacy endpoints).
"""

import requests
import argparse

def _detect_a2a(green_agent_url: str) -> bool:
    """Return True if the green agent exposes A2A endpoints."""
    try:
        r = requests.get(f"{green_agent_url}/a2a/health", timeout=10)
        return r.status_code == 200
    except requests.RequestException:
        return False

def _get_tasks(green_agent_url: str, use_a2a: bool):
    """Fetch task list and return (tasks_list, raw_payload)."""
    tasks_endpoint = "/a2a/tasks" if use_a2a else "/tasks"
    url = f"{green_agent_url}{tasks_endpoint}"
    r = requests.get(url, timeout=20)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        # Show server-provided error body if available
        raise SystemExit(f"Error getting tasks ({r.status_code}): {r.text}")

    data = r.json() or {}
    # A2A shape: {"protocol":"a2a","tasks":[...], "total":N}
    # Legacy:    {"tasks":[...], "total":N}
    tasks = data.get("tasks", data)
    return tasks, data

def _evaluate(green_agent_url: str, use_a2a: bool, white_agent_url: str, task_ids: list):
    """Call the evaluate endpoint and return JSON."""
    evaluate_endpoint = "/a2a/evaluate" if use_a2a else "/evaluate"
    url = f"{green_agent_url}{evaluate_endpoint}"
    payload = {"white_agent_url": white_agent_url, "task_ids": task_ids}
    r = requests.post(url, json=payload, timeout=120)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        raise SystemExit(f"Error during evaluation ({r.status_code}): {r.text}")
    return r.json() or {}

def run_benchmark(green_agent_url: str, white_agent_url: str, task_ids: list = None):
    """Run Aurora benchmark."""

    print("=" * 70)
    print("Aurora Benchmark")
    print("=" * 70)
    print(f"Green Agent: {green_agent_url}")
    print(f"White Agent: {white_agent_url}")
    print()

    use_a2a = _detect_a2a(green_agent_url)
    print(f"Detected protocol: {'A2A' if use_a2a else 'Legacy'}")
    tasks, raw = _get_tasks(green_agent_url, use_a2a)

    # Normalize tasks to a list of dicts with 'id' and optional 'route'
    known_ids = [t.get("id") for t in tasks if isinstance(t, dict) and "id" in t]
    if not known_ids:
        raise SystemExit("No tasks discovered from the green agent.")

    # If no explicit list provided, use all
    if not task_ids:
        task_ids = known_ids

    # Validate passed task ids
    unknown = [tid for tid in task_ids if tid not in known_ids]
    if unknown:
        raise SystemExit(f"Unknown task_ids: {unknown}\nKnown: {known_ids}")

    print(f"Tasks to evaluate: {len(task_ids)}")
    for t in tasks:
        tid = t.get("id")
        if tid in task_ids:
            route = t.get("route")
            if isinstance(route, dict) and "start" in route and "end" in route:
                print(f"  - {tid}: {route['start']} -> {route['end']}")
            else:
                print(f"  - {tid}")
    print()

    print("Running evaluation...")
    result = _evaluate(green_agent_url, use_a2a, white_agent_url, task_ids)

    # A2A:   {"protocol":"a2a","status":"completed","results":{...}}
    # Legacy:{"status":"completed","results":{...}}
    results_data = result.get("results", {})
    avg_score = results_data.get("average_aurora_score", 0)
    passed = results_data.get("passed", False)

    print()
    print("=" * 70)
    print("Benchmark Complete")
    print("=" * 70)
    print(f"Average Aurora Score: {avg_score}")
    print(f"Passed: {'YES' if passed else 'NO'}")
    print()

    detailed = results_data.get("results", [])
    if isinstance(detailed, list) and detailed:
        print("Detailed Results:")
        for tr in detailed:
            tid = tr.get("task_id")
            err = tr.get("error")
            if err:
                print(f"  - {tid}: ERROR - {err}")
            else:
                print(f"  - {tid}: Score={tr.get('aurora_score', 0)}")
                print(f"      Context={tr.get('context_alignment', 0)}  "
                      f"Creativity={tr.get('creativity', 0)}  "
                      f"UX={tr.get('ux_coherence', 0)}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Aurora benchmark")
    parser.add_argument("--green-url", default="http://localhost:8001", help="Green agent URL")
    parser.add_argument("--white-url", default="http://localhost:9000", help="White agent URL")
    parser.add_argument("--tasks", nargs="+", help="Specific task IDs to run (optional)")
    args = parser.parse_args()

    run_benchmark(args.green_url, args.white_url, args.tasks)
