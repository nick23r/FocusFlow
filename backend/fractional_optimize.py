"""
AI-powered task optimizer using Fractional Knapsack algorithm.
Allows partial inclusion of tasks to maximize time utilization.
"""

def optimize_tasks_fractional(tasks, available_time):
    """
    Optimize tasks using Fractional Knapsack algorithm.
    Tasks can be partially included based on available time.
    
    Args:
        tasks: List of task dictionaries with name, duration, priority, category
        available_time: Available time in minutes
        
    Returns:
        Dictionary with optimized_tasks, skipped_tasks, total_time, total_value, explanation
    """
    if not tasks or available_time <= 0:
        return {
            "optimized_tasks": [],
            "skipped_tasks": tasks,
            "total_time": 0,
            "total_value": 0,
            "explanation": "No tasks to optimize or no available time."
        }
    
    # Category weights for value calculation
    category_weights = {
        "work": 1.2,
        "health": 1.1,
        "learning": 1.15,
        "chore": 0.9,
        "relaxation": 0.8
    }
    
    # Calculate value and efficiency for each task
    for task in tasks:
        category_weight = category_weights.get(task["category"], 1.0)
        task["value"] = task["priority"] * category_weight
        task["efficiency"] = task["value"] / task["duration"] if task["duration"] > 0 else 0
    
    # Sort tasks by efficiency (value per minute) in descending order
    sorted_tasks = sorted(tasks, key=lambda t: t["efficiency"], reverse=True)
    
    optimized_tasks = []
    skipped_tasks = []
    remaining_time = available_time
    total_value = 0
    total_time = 0
    partial_inclusion = False
    
    for task in sorted_tasks:
        if remaining_time >= task["duration"]:
            # Task fits completely
            optimized_tasks.append(task)
            remaining_time -= task["duration"]
            total_time += task["duration"]
            total_value += task["value"]
        elif remaining_time > 0:
            # Task can be partially included
            fraction = remaining_time / task["duration"]
            partial_task = task.copy()
            partial_task["duration"] = remaining_time
            partial_task["value"] = task["value"] * fraction
            partial_task["is_partial"] = True
            partial_task["original_duration"] = task["duration"]
            partial_task["fraction"] = fraction
            optimized_tasks.append(partial_task)
            total_value += partial_task["value"]
            total_time += remaining_time
            remaining_time = 0
            partial_inclusion = True
        else:
            # No time left for this task
            skipped_tasks.append(task)
    
    # Generate explanation
    explanation = generate_explanation_fractional(
        optimized_tasks,
        skipped_tasks,
        total_time,
        available_time,
        category_weights,
        partial_inclusion
    )
    
    return {
        "optimized_tasks": optimized_tasks,
        "skipped_tasks": skipped_tasks,
        "total_time": total_time,
        "total_value": round(total_value, 2),
        "explanation": explanation,
        "partial_inclusion": partial_inclusion
    }


def generate_explanation_fractional(optimized_tasks, skipped_tasks, total_time, available_time, category_weights, partial_inclusion):
    """
    Generate a human-readable explanation of the fractional knapsack optimization results.
    """
    explanation_parts = []
    
    # Overview
    explanation_parts.append(
        f"Optimized your schedule using fractional knapsack algorithm within {available_time} minutes "
        f"({available_time / 60:.1f} hours). "
    )
    
    # Selected tasks summary
    if optimized_tasks:
        full_tasks = [t for t in optimized_tasks if not t.get("is_partial", False)]
        partial_tasks = [t for t in optimized_tasks if t.get("is_partial", False)]
        
        explanation_parts.append(
            f"Selected {len(full_tasks)} full task(s)"
        )
        
        if partial_tasks:
            explanation_parts.append(
                f" and {len(partial_tasks)} partial task(s)"
            )
        
        explanation_parts.append(
            f" totaling {total_time} minutes ({total_time / 60:.1f} hours), "
            f"leaving {available_time - total_time} minutes free. "
        )
        
        # Category breakdown
        category_counts = {}
        for task in optimized_tasks:
            cat = task["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if category_counts:
            cat_summary = ", ".join([
                f"{count} {cat}" for cat, count in category_counts.items()
            ])
            explanation_parts.append(f"Your optimized schedule includes: {cat_summary}. ")
        
        # Partial inclusion note
        if partial_inclusion:
            explanation_parts.append(
                "This schedule includes partial task completion to maximize time utilization. "
            )
    
    # Skipped tasks explanation
    if skipped_tasks:
        explanation_parts.append(
            f"{len(skipped_tasks)} task(s) were skipped due to lower efficiency scores. "
        )
    
    # Algorithm explanation
    explanation_parts.append(
        "The fractional knapsack algorithm prioritizes tasks by efficiency (value per minute) "
        "and can include partial tasks. Category weights: "
        f"Work ({category_weights['work']}x), "
        f"Health ({category_weights['health']}x), "
        f"Learning ({category_weights['learning']}x), "
        f"Chore ({category_weights['chore']}x), "
        f"Relaxation ({category_weights['relaxation']}x). "
    )
    
    return "".join(explanation_parts)
