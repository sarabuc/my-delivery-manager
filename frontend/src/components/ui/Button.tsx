import type { ButtonHTMLAttributes } from "react";

const base =
  "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";

export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`${base} ${className}`}
      {...props}
      type={props.type ?? "button"}
    />
  );
}
