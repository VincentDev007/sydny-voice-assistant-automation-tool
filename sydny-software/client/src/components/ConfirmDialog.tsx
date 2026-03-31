interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

function ConfirmDialog({ message, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-80 z-50">
      <div className="border border-orange-900 bg-black p-8 text-center font-mono max-w-sm">
        <p className="text-orange-200 text-base mb-6">{message}</p>
        <div className="flex justify-center gap-6">
          <button
            onClick={onConfirm}
            className="px-6 py-2 border border-orange-500 text-orange-500 font-bold hover:bg-orange-500 hover:text-black transition-colors"
          >
            YES
          </button>
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-600 text-gray-500 font-bold hover:bg-gray-700 hover:text-white transition-colors"
          >
            NO
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
