export default function FormChart({ form, team }) {
  if (!form) return <span className="text-gray-400">No data</span>;

  return (
    <div className="flex gap-1">
      {form.split('').map((r, i) => (
        <span
          key={i}
          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
            r === 'W' ? 'bg-green-500' : r === 'D' ? 'bg-yellow-500' : 'bg-red-500'
          }`}
        >
          {r}
        </span>
      ))}
    </div>
  );
}
