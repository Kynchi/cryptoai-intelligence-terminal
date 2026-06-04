import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/utils/cn";

interface MetricCardProps {
  label: string;
  value: string;
  sub?: string;
  icon?: LucideIcon;
  tone?: "neutral" | "success" | "danger" | "warning" | "accent";
  mono?: boolean;
}

const tones = {
  neutral: "text-terminal-text",
  success: "text-terminal-success",
  danger: "text-terminal-danger",
  warning: "text-terminal-warning",
  accent: "text-terminal-accent"
};

export function MetricCard({ label, value, sub, icon: Icon, tone = "neutral", mono = true }: MetricCardProps) {
  return (
    <motion.div whileHover={{ y: -3 }} className="metric-card">
      <div className="flex items-center gap-2 text-terminal-muted">
        {Icon && <Icon className="h-3.5 w-3.5 text-terminal-accent" />}
        <span className="terminal-kicker">{label}</span>
      </div>
      <div className={cn("mt-2 truncate text-xl font-semibold", mono && "font-mono", tones[tone])}>{value}</div>
      {sub && <div className="mt-1 truncate text-[11px] text-terminal-muted">{sub}</div>}
    </motion.div>
  );
}
