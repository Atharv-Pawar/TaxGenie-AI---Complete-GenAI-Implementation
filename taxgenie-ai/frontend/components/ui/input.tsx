import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "flex w-full px-4 py-3 rounded-xl bg-surface border border-surface-border",
        "text-slate-200 placeholder-slate-600 text-sm",
        "focus:outline-none focus:border-brand-500/60 transition-colors",
        "disabled:opacity-40 disabled:cursor-not-allowed",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
