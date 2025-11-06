# FocusFlow
# https://nicktask.vercel.app

An intelligent daily task planner that uses AI-powered optimization algorithms (0/1 Knapsack or Fractional Knapsack) to optimize your schedule based on task duration, priority, and category.

## Features

- **Dual Optimization Methods**: Choose between 0/1 Knapsack (all-or-nothing) or Fractional Knapsack (partial task inclusion)
- **Smart Task Optimization**: Maximizes productivity using dynamic programming algorithms
- **Category-Based Weighting**: Work (1.2x), Health (1.1x), Learning (1.15x), Chore (0.9x), Relaxation (0.8x)
- **Firebase Integration**: Save and load your tasks and plans with username-based storage
- **Modern UI**: Responsive design with light/dark mode toggle
- **Real-time Results**: See optimized tasks and explanations for skipped items

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python (Flask) on Vercel Serverless Functions
- **Database**: Firebase Realtime Database
- **Algorithms**: 0/1 Knapsack DP and Fractional Knapsack
- **Hosting**: Vercel

## Project Structure

```
FocusFlow/
├── index.html              # Main HTML file (root)
├── style.css               # Styles (root)
├── script.js               # Frontend logic (root)
├── api/
│   ├── optimize.py         # Optimization endpoint
│   ├── save.py             # Save tasks endpoint
│   ├── load.py             # Load tasks endpoint
│   └── requirements.txt    # Python dependencies
├── backend/
│   ├── __init__.py
│   ├── optimizer.py        # 0/1 Knapsack DP algorithm
│   ├── fractional_optimize.py  # Fractional Knapsack algorithm
│   └── firebase_connect.py # Firebase integration
├── vercel.json             # Vercel configuration
└── README.md
```

## Firebase Setup

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable **Realtime Database** in your project
3. Go to Project Settings → Service Accounts
4. Generate a new private key (downloads a JSON file)
5. Add to Vercel as environment variables:
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: Paste the entire JSON content
   - `FIREBASE_DATABASE_URL`: Your database URL (e.g., `https://your-project.firebaseio.com`)

## Local Development

1. Install Python dependencies:
   ```
   bash
   pip install -r api/requirements.txt
   ```

2. Set environment variables:
   ```
   bash
   export FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
   export FIREBASE_DATABASE_URL='https://your-project.firebaseio.com'
   ```

3. Run locally with Vercel CLI:
   ```
   bash
   vercel dev
   ```

## API Endpoints

### POST /api/optimize
Optimizes tasks using selected algorithm (0/1 Knapsack or Fractional Knapsack).

**Request Body:**
```
json
{
  "tasks": [
    {
      "name": "Morning Workout",
      "duration": 60,
      "priority": 5,
      "category": "health"
    }
  ],
  "available_time": 480,
  "method": "0/1"
}
```

**Response:**
```
json
{
  "optimized_tasks": [...],
  "skipped_tasks": [...],
  "total_time": 420,
  "total_value": 28.5,
  "explanation": "Optimized for maximum productivity...",
  "partial_inclusion": false
}
```

### POST /api/save
Saves tasks and plan to Firebase.

### GET /api/load
Loads previous tasks and plans from Firebase.

## Algorithm Details

### 0/1 Knapsack (All-or-Nothing)
- **Weight**: Task duration (in minutes)
- **Value**: Priority × Category Weight
- **Capacity**: Available time (default: 8 hours = 480 minutes)
- **Time Complexity**: O(n × W) where n = number of tasks, W = available time
- **Use Case**: When you want to complete tasks fully or not at all

### Fractional Knapsack (Partial Inclusion)
- **Efficiency**: Value per minute (Priority × Category Weight / Duration)
- **Sorting**: Tasks sorted by efficiency in descending order
- **Partial Inclusion**: Can include part of a task if time allows
- **Time Complexity**: O(n log n) for sorting
- **Use Case**: When you can work on tasks partially (e.g., reading, studying)

## Category Weights

- **Work**: 1.2x multiplier - High priority for productivity
- **Health**: 1.1x multiplier - Important for wellbeing
- **Learning**: 1.15x multiplier - Skill development
- **Chore**: 0.9x multiplier - Necessary but lower priority
- **Relaxation**: 0.8x multiplier - Lower priority for optimization

## Deployment

Deploy to Vercel with one click:

```
bash
vercel --prod
```

Make sure to add your Firebase environment variables in the Vercel dashboard.

## License

MIT
