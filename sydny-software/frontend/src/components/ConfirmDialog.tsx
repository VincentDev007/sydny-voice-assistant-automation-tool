interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

function ConfirmDialog({ message, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-80 z-50">
      <div className="border border-gray-600 bg-black p-8 text-center font-mono">
        <p className="text-gray-400 text-lg mb-6">{message}</p>
        <div className="flex justify-center gap-6">
          <button
            onClick={onConfirm}
            className="px-6 py-2 border-2 border-green-500 text-green-500 font-bold hover:bg-green-500 hover:text-black transition-colors"
          >
            CONFIRM
          </button>
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
