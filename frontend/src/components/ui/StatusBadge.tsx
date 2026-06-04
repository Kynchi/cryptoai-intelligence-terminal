import { cn } from "@/utils/cn";

interface StatusBadgeProps {
  children: React.ReactNode;
  tone?: "success" | "danger" | "warning" | "accent" | "neutral";
}

const tones = {
  success: "border-terminal-success/30 bg-terminal-success/10 text-terminal-success",
  danger: "border-terminal-danger/30 bg-terminal-danger/10 text-terminal-danger",
  warning: "border-terminal-warning/30 bg-terminal-warning/10 text-terminal-warning",
  accent: "border-terminal-accent/30 bg-terminal-accent/10 text-terminal-accent",
  neutral: "border-white/10 bg-white/5 text-terminal-muted"
};

export function StatusBadge({ children, tone = "neutral" }: StatusBadgeProps) {
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-1 font-mono text-[10px] uppercase", tones[tone])}>
      {children}
    </span>
  );
}
