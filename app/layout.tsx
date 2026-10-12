import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AtlasLaunch — N-ATLAS Developer Workbench",
  description: "Connect to N-ATLAS, inspect multilingual responses, run repeatable tests and export honest evidence.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
