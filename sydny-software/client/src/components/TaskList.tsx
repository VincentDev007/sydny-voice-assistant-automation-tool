// ============================================================
// TaskList.tsx — Task Display Component
// ============================================================
// Renders the list of tasks from the database.
// Tasks are read-only here — all modifications happen through voice commands.
// This component only DISPLAYS tasks; it doesn't add, complete, or delete them.
//
// VISUAL DESIGN:
//   Priority-based color coding (defined in TaskList.css):
//     task-priority-high   → red text     (urgent)
//     task-priority-normal → yellow text  (default)
//     task-priority-low    → green text   (low urgency)
//
//   Completion state:
//     ○ (empty circle) → incomplete task
//     ✓ (checkmark)    → completed task (also gets task-item-completed class for strikethrough)
//
// EMPTY STATE:
//   Shows "No tasks" when the array is empty — handled with early return.
//
// PROPS:
//   tasks → array of Task objects from useStore (passed down from App.tsx)
// ============================================================

import "./TaskList.css";


// Task shape — must match what the backend returns in TaskResponse
interface Task {
  id: number;
  description: string;
  priority: string;   // "low" | "normal" | "high"
  completed: boolean;
}

interface TaskListProps {
  tasks: Task[]; // Array of tasks to display
}


function TaskList({ tasks }: TaskListProps) {
  // Empty state — show a placeholder message when there are no tasks
  if (tasks.length === 0) {
    return (
      <div className="task-list bg-black">
        <span className="text-gray-500 font-mono">No tasks</span>
      </div>
    );
  }

  return (
    <div className="task-list bg-black">
      {tasks.map((task) => (
        <div
          key={task.id} // React list key — must be unique, use the database ID
          className={`task-item task-priority-${task.priority} ${
            task.completed ? "task-item-completed" : "" // Add completed style if done
          }`}
        >
          {/* Left: completion icon + description */}
          <span>
            {task.completed ? "✓" : "○"} {/* Visual completion indicator */}
            {" "}{task.description}
          </span>

          {/* Right: priority label (low/normal/high) — small gray text */}
          <span className="text-gray-500 text-xs">{task.priority}</span>
        </div>
      ))}
    </div>
  );
}

export default TaskList;
