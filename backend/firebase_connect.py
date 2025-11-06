"""
Firebase Realtime Database integration for AI Task Optimizer.
Handles saving and loading user tasks and optimization plans using username-based storage.
Falls back to in-memory storage when Firebase is not configured.
"""
import os
import json

# Try to import Firebase, but don't fail if not available
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase Admin SDK not available, using in-memory storage")

# Initialize Firebase Admin SDK
_firebase_initialized = False
_in_memory_storage = {}  # Fallback storage when Firebase is not available

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    Uses environment variables for configuration.
    Falls back to in-memory storage if Firebase is not configured.
    """
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    if not FIREBASE_AVAILABLE:
        print("Using in-memory storage (Firebase not available)")
        return False
    
    try:
        # Get service account JSON from environment variable
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        database_url = os.environ.get('FIREBASE_DATABASE_URL')
        
        if not service_account_json or not database_url:
            print("Firebase credentials not configured, using in-memory storage")
            return False
        
        # Parse service account JSON
        service_account_dict = json.loads(service_account_json)
        
        # Initialize Firebase
        cred = credentials.Certificate(service_account_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        _firebase_initialized = True
        print("Firebase initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}, using in-memory storage")
        return False


def save_user_tasks(username, tasks):
    """
    Save user tasks to Firebase Realtime Database or in-memory storage.
    Uses username as the unique key instead of user ID.
    
    Args:
        username: Username identifier (unique key)
        tasks: List of task dictionaries
        
    Returns:
        Dictionary with success status
    """
    try:
        firebase_ready = initialize_firebase()
        
        if firebase_ready and _firebase_initialized:
            # Use Firebase with username-based path
            ref = db.reference(f'users/{username}/tasks')
            
            import time
            data = {
                'tasks': tasks,
                'saved_at': int(time.time() * 1000),
                'task_count': len(tasks)
            }
            
            ref.set(data)
        else:
            import time
            if username not in _in_memory_storage:
                _in_memory_storage[username] = {}
            _in_memory_storage[username]['tasks'] = {
                'tasks': tasks,
                'saved_at': int(time.time() * 1000),
                'task_count': len(tasks)
            }
            print(f"Saved tasks to in-memory storage for user {username}")
        
        return {
            "success": True,
            "message": "Tasks saved successfully",
            "task_count": len(tasks)
        }
        
    except Exception as e:
        print(f"Error saving tasks: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def load_user_tasks(username):
    """
    Load user tasks from Firebase Realtime Database or in-memory storage.
    Uses username as the unique key.
    
    Args:
        username: Username identifier (unique key)
        
    Returns:
        Dictionary with success status and tasks
    """
    try:
        firebase_ready = initialize_firebase()
        
        if firebase_ready and _firebase_initialized:
            # Use Firebase with username-based path
            ref = db.reference(f'users/{username}/tasks')
            data = ref.get()
            
            if data and 'tasks' in data:
                return {
                    "success": True,
                    "tasks": data['tasks'],
                    "saved_at": data.get('saved_at'),
                    "task_count": len(data['tasks'])
                }
        else:
            data = _in_memory_storage.get(username, {}).get('tasks')
            
            if data and 'tasks' in data:
                print(f"Loaded tasks from in-memory storage for user {username}")
                return {
                    "success": True,
                    "tasks": data['tasks'],
                    "saved_at": data.get('saved_at'),
                    "task_count": len(data['tasks'])
                }
        
        return {
            "success": False,
            "tasks": [],
            "message": "No tasks found"
        }
        
    except Exception as e:
        print(f"Error loading tasks: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tasks": []
        }


def save_optimization_plan(username, plan_data):
    """
    Save an optimization plan to Firebase using username-based storage.
    
    Args:
        username: Username identifier (unique key)
        plan_data: Dictionary with optimization results
        
    Returns:
        Dictionary with success status
    """
    try:
        firebase_ready = initialize_firebase()
        
        if firebase_ready and _firebase_initialized:
            # Use Firebase with username-based path
            ref = db.reference(f'users/{username}/plans')
            
            # Add timestamp
            import time
            plan_data['created_at'] = int(time.time() * 1000)
            
            # Push new plan (auto-generates unique ID)
            new_plan_ref = ref.push(plan_data)
            
            return {
                "success": True,
                "message": "Plan saved successfully",
                "plan_id": new_plan_ref.key
            }
        else:
            import time
            plan_data['created_at'] = int(time.time() * 1000)
            if username not in _in_memory_storage:
                _in_memory_storage[username] = {}
            if 'plans' not in _in_memory_storage[username]:
                _in_memory_storage[username]['plans'] = []
            _in_memory_storage[username]['plans'].append(plan_data)
            print(f"Saved plan to in-memory storage for user {username}")
            return {
                "success": True,
                "message": "Plan saved successfully",
                "plan_id": len(_in_memory_storage[username]['plans']) - 1
            }
        
    except Exception as e:
        print(f"Error saving plan: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_user_plans(username, limit=10):
    """
    Get user's optimization plans from Firebase using username-based storage.
    
    Args:
        username: Username identifier (unique key)
        limit: Maximum number of plans to retrieve
        
    Returns:
        Dictionary with success status and plans
    """
    try:
        firebase_ready = initialize_firebase()
        
        if firebase_ready and _firebase_initialized:
            # Use Firebase with username-based path
            ref = db.reference(f'users/{username}/plans')
            
            # Get plans ordered by creation time
            plans = ref.order_by_child('created_at').limit_to_last(limit).get()
            
            if plans:
                # Convert to list and reverse to get newest first
                plans_list = [
                    {"id": plan_id, **plan_data}
                    for plan_id, plan_data in plans.items()
                ]
                plans_list.reverse()
                
                return {
                    "success": True,
                    "plans": plans_list,
                    "count": len(plans_list)
                }
        else:
            data = _in_memory_storage.get(username, {}).get('plans', [])
            
            if data:
                plans_list = data[-limit:]
                plans_list = [
                    {"id": idx, **plan}
                    for idx, plan in enumerate(plans_list)
                ]
                print(f"Loaded plans from in-memory storage for user {username}")
                return {
                    "success": True,
                    "plans": plans_list,
                    "count": len(plans_list)
                }
        
        return {
            "success": False,
            "plans": [],
            "message": "No plans found"
        }
        
    except Exception as e:
        print(f"Error getting plans: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "plans": []
        }
