import "@/styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "GitLab Delivery Agent",
  description: "Wizard to deliver branches and commits between GitLab repositories"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-50">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <p className="text-sm text-slate-500">GitLab Content Delivery Agent</p>
                <h1 className="text-lg font-semibold text-slate-900">Delivery Wizard</h1>
              </div>
              <span className="rounded-full bg-brand-500 px-3 py-1 text-xs font-medium text-white">
                v0.1
              </span>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
