import "./TaskList.css";

interface Task {
  id: number;
  description: string;
  priority: string;
  completed: boolean;
}

interface TaskListProps {
  tasks: Task[];
}

function TaskList({ tasks }: TaskListProps) {
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
          key={task.id}
          className={`task-item task-priority-${task.priority} ${
            task.completed ? "task-item-completed" : ""
          }`}
        >
          <span>{task.completed ? "✓" : "○"} {task.description}</span>
          <span className="text-gray-500 text-xs">{task.priority}</span>
        </div>
      ))}
    </div>
  );
}

export default TaskList;
