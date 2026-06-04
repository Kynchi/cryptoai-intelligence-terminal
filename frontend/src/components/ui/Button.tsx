import { type ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "@/utils/cn";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "icon";
}

const variants = {
  primary: "border-terminal-accent/70 bg-terminal-accent text-[#08101a] shadow-glow hover:bg-[#7dc6f5]",
  secondary: "border-white/10 bg-terminal-panel2 text-terminal-text hover:border-terminal-accent/60",
  ghost: "border-transparent bg-transparent text-terminal-muted hover:bg-terminal-panel2 hover:text-terminal-text",
  danger: "border-terminal-danger/40 bg-terminal-danger/10 text-terminal-danger hover:bg-terminal-danger/20"
};

const sizes = {
  sm: "h-8 px-3 text-[11px]",
  md: "h-10 px-4 text-xs",
  icon: "h-9 w-9 p-0"
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "secondary", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg border font-bold transition-all duration-200 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  )
);

Button.displayName = "Button";
