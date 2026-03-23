// ============================================================
// ConfirmDialog.tsx — Confirmation Modal for Dangerous Commands
// ============================================================
// A modal overlay that blocks the UI and asks the user to confirm
// before a destructive or dangerous command is executed.
//
// WHEN IT APPEARS:
//   When the command parser returns needs_confirm: true.
//   This happens for: shutdown, restart, sleep, delete-file, delete-task.
//   App.tsx's pendingCommand useEffect calls showConfirm() which
//   sets confirmMessage and confirmAction in the store → App.tsx renders this component.
//
// HOW IT WORKS:
//   1. Command parser returns needs_confirm: true
//   2. App.tsx calls showConfirm(message, action) → stores both in Zustand
//   3. App.tsx conditionally renders ConfirmDialog when confirmMessage is not null
//   4. User clicks CONFIRM → onConfirm() runs the stored action + closes dialog
//   5. User clicks CANCEL  → onCancel() just closes the dialog, nothing executes
//
// VISUAL DESIGN:
//   Fixed fullscreen overlay (z-50) with semi-transparent black background
//   Dark themed modal box with gray border — matches SYDNY's terminal aesthetic
//   Green CONFIRM button — hover fills green (go / execute)
//   Red CANCEL button   — hover fills red (stop / abort)
//   transition-colors   — smooth color transition on hover
//
// PROPS:
//   message   → the confirmation question shown to the user
//   onConfirm → called when user clicks CONFIRM (executes the command)
//   onCancel  → called when user clicks CANCEL (discards the command)
// ============================================================


interface ConfirmDialogProps {
  message: string;      // e.g., 'Execute "shutdown"?'
  onConfirm: () => void; // Execute the dangerous action
  onCancel: () => void;  // Abort — do nothing
}


function ConfirmDialog({ message, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    // Full-screen overlay: fixed positioning, covers entire viewport
    // bg-opacity-80 makes the overlay semi-transparent (80% opaque)
    // z-50 puts it above everything else in the stacking order
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-80 z-50">

      {/* Modal box — centered, black background, gray border */}
      <div className="border border-gray-600 bg-black p-8 text-center font-mono">

        {/* The confirmation question */}
        <p className="text-gray-400 text-lg mb-6">{message}</p>

        {/* Action buttons */}
        <div className="flex justify-center gap-6">

          {/* CONFIRM button — green, hover fills background */}
          <button
            onClick={onConfirm}
            className="px-6 py-2 border-2 border-green-500 text-green-500 font-bold hover:bg-green-500 hover:text-black transition-colors"
          >
            CONFIRM
          </button>

          {/* CANCEL button — red, hover fills background */}
          <button
            onClick={onCancel}
            className="px-6 py-2 border-2 border-red-500 text-red-500 font-bold hover:bg-red-500 hover:text-black transition-colors"
          >
            CANCEL
          </button>

        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
