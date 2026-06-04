export function TerminalSkeleton() {
  return (
    <div className="grid gap-3 lg:grid-cols-4">
      {Array.from({ length: 12 }).map((_, index) => (
        <div key={index} className="terminal-panel h-28 animate-pulse bg-gradient-to-r from-white/[0.03] via-white/[0.07] to-white/[0.03]" />
      ))}
    </div>
  );
}
