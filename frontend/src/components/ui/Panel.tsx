import { type HTMLAttributes, type ReactNode } from "react";
import { motion } from "framer-motion";

import { cn } from "@/utils/cn";

export function Panel({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("terminal-panel", className)}
      {...props}
    >
      {children}
    </motion.section>
  );
}

export function PanelHeader({
  title,
  kicker,
  action
}: {
  title: string;
  kicker?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex min-h-8 items-center justify-between gap-3">
      <div>
        <p className="terminal-kicker">{kicker}</p>
        <h2 className="font-outfit text-sm font-bold text-terminal-text">{title}</h2>
      </div>
      {action}
    </div>
  );
}
