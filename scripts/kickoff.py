"""
Aurora Benchmark Launcher

Simple script to run Aurora evaluation.
"""

import requests
import json
import argparse

def run_benchmark(green_agent_url: str, white_agent_url: str, task_ids: list = None):
    """Run Aurora benchmark."""
    
    print("=" * 70)
    print("🎵 Aurora Benchmark")
    print("=" * 70)
    print(f"Green Agent: {green_agent_url}")
    print(f"White Agent: {white_agent_url}")
    print()
    
    # Get available tasks
    try:
        response = requests.get(f"{green_agent_url}/tasks")
        response.raise_for_status()
        tasks_data = response.json()
        
        if not task_ids:
            task_ids = [t['id'] for t in tasks_data['tasks']]
        
        print(f"Tasks to evaluate: {len(task_ids)}")
        for task in tasks_data['tasks']:
            if task['id'] in task_ids:
                print(f"  • {task['id']}: {task['route']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting tasks: {e}")
        return None
    
    # Run evaluation
    try:
        print("Running evaluation...")
        response = requests.post(
            f"{green_agent_url}/evaluate",
            json={
                'white_agent_url': white_agent_url,
                'task_ids': task_ids
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Display results
        print()
        print("=" * 70)
        print("✓ Benchmark Complete!")
        print("=" * 70)
        
        results_data = result.get('results', {})
        print(f"\nAverage Aurora Score: {results_data.get('average_aurora_score', 0)}")
        print(f"Passed: {'✓' if results_data.get('passed') else '✗'}")
        print()
        
        print("Detailed Results:")
        for task_result in results_data.get('results', []):
            task_id = task_result.get('task_id')
            score = task_result.get('aurora_score', 0)
            error = task_result.get('error')
            
            if error:
                print(f"  • {task_id}: ✗ Error - {error}")
            else:
                print(f"  • {task_id}: Score = {score}")
                print(f"    - Context: {task_result.get('context_alignment', 0)}")
                print(f"    - Creativity: {task_result.get('creativity', 0)}")
                print(f"    - UX: {task_result.get('ux_coherence', 0)}")
        
        print("=" * 70)
        return result
        
    except requests.exceptions.Timeout:
        print("\n❌ Timeout: Evaluation took too long")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error during evaluation: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Aurora benchmark")
    parser.add_argument("--green-url", default="http://localhost:8001", help="Green agent URL")
    parser.add_argument("--white-url", default="http://localhost:9000", help="White agent URL")
    parser.add_argument("--tasks", nargs="+", help="Specific task IDs to run (optional)")
    args = parser.parse_args()
    
    run_benchmark(args.green_url, args.white_url, args.tasks)
