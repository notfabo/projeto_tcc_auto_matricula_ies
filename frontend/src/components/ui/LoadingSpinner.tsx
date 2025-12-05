export function LoadingSpinner({ label = 'Carregando...' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-10">
      <div className="inline-flex items-center gap-3 text-gray-600">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></span>
        <span className="text-sm">{label}</span>
      </div>
    </div>
  );
}


