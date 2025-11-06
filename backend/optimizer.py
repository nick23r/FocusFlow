"""
AI-powered task optimizer using 0/1 Knapsack Dynamic Programming algorithm.
Optimizes daily tasks based on duration, priority, and category weights.
"""

def optimize_tasks(tasks, available_time):
    """
    Optimize tasks using 0/1 Knapsack Dynamic Programming.
    
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
    
    category_weights = {
        "work": 1.2,
        "health": 1.1,
        "learning": 1.15,
        "chore": 0.9,
        "relaxation": 0.8
    }
    
    # Calculate value for each task (priority * category_weight)
    for task in tasks:
        category_weight = category_weights.get(task["category"], 1.0)
        task["value"] = task["priority"] * category_weight
    
    n = len(tasks)
    W = int(available_time)
    
    # Create DP table
    # dp[i][w] = maximum value achievable with first i tasks and w minutes
    dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        task = tasks[i - 1]
        weight = int(task["duration"])
        value = task["value"]
        
        for w in range(W + 1):
            # Don't include current task
            dp[i][w] = dp[i - 1][w]
            
            # Include current task if it fits
            if weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weight] + value)
    
    # Backtrack to find which tasks were selected
    selected_indices = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_indices.append(i - 1)
            w -= int(tasks[i - 1]["duration"])
    
    selected_indices.reverse()
    
    # Separate optimized and skipped tasks
    optimized_tasks = [tasks[i] for i in selected_indices]
    skipped_tasks = [tasks[i] for i in range(n) if i not in selected_indices]
    
    # Calculate totals
    total_time = sum(task["duration"] for task in optimized_tasks)
    total_value = sum(task["value"] for task in optimized_tasks)
    
    # Generate explanation
    explanation = generate_explanation(
        optimized_tasks, 
        skipped_tasks, 
        total_time, 
        available_time,
        category_weights
    )
    
    return {
        "optimized_tasks": optimized_tasks,
        "skipped_tasks": skipped_tasks,
        "total_time": total_time,
        "total_value": round(total_value, 2),
        "explanation": explanation
    }


def generate_explanation(optimized_tasks, skipped_tasks, total_time, available_time, category_weights):
    """
    Generate a human-readable explanation of the optimization results.
    """
    explanation_parts = []
    
    # Overview
    explanation_parts.append(
        f"Optimized your schedule to maximize productivity within {available_time} minutes "
        f"({available_time / 60:.1f} hours). "
    )
    
    # Selected tasks summary
    if optimized_tasks:
        explanation_parts.append(
            f"Selected {len(optimized_tasks)} task(s) totaling {total_time} minutes "
            f"({total_time / 60:.1f} hours), leaving {available_time - total_time} minutes free. "
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
    
    # Skipped tasks explanation
    if skipped_tasks:
        explanation_parts.append(
            f"{len(skipped_tasks)} task(s) were skipped due to time constraints or lower priority-to-duration ratio. "
        )
        
        # Explain why tasks were skipped
        high_priority_skipped = [t for t in skipped_tasks if t["priority"] >= 4]
        if high_priority_skipped:
            explanation_parts.append(
                "Some high-priority tasks were skipped because they couldn't fit in the remaining time. "
                "Consider extending your available time or breaking down larger tasks. "
            )
    
    explanation_parts.append(
        "The algorithm prioritizes tasks using category weights: "
        f"Work ({category_weights['work']}x), "
        f"Health ({category_weights['health']}x), "
        f"Learning ({category_weights['learning']}x), "
        f"Chore ({category_weights['chore']}x), "
        f"Relaxation ({category_weights['relaxation']}x). "
    )
    
    return "".join(explanation_parts)


def calculate_task_efficiency(task, category_weights):
    """
    Calculate efficiency score for a task (value per minute).
    """
    category_weight = category_weights.get(task["category"], 1.0)
    value = task["priority"] * category_weight
    return value / task["duration"] if task["duration"] > 0 else 0
