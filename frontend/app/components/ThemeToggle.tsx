"use client";

import { useState, useEffect } from "react";
import { Sun, Moon, Monitor } from "lucide-react";

type ThemeMode = "light" | "dark" | "auto";

export default function ThemeToggle() {
  const [mode, setMode] = useState<ThemeMode>("auto");
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("iztack_theme") as ThemeMode | null;
    const initialMode: ThemeMode = stored || "auto";
    setMode(initialMode);
    applyTheme(initialMode);

    // Listen to system changes when in auto mode
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => {
      if ((localStorage.getItem("iztack_theme") as ThemeMode | null) === "auto") {
        applyTheme("auto");
      }
    };
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  function applyTheme(nextMode: ThemeMode) {
    let isDark = false;
    if (nextMode === "dark") {
      isDark = true;
    } else if (nextMode === "auto") {
      isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    document.documentElement.classList.toggle("dark", isDark);
    setDark(isDark);
  }

  function cycleMode() {
    const order: ThemeMode[] = ["auto", "light", "dark"];
    const next = order[(order.indexOf(mode) + 1) % order.length];
    setMode(next);
    localStorage.setItem("iztack_theme", next);
    applyTheme(next);
  }

  const icon =
    mode === "dark" ? <Moon className="h-5 w-5" /> :
    mode === "light" ? <Sun className="h-5 w-5" /> :
    <Monitor className="h-5 w-5" />;

  const label =
    mode === "dark" ? "Modo oscuro" :
    mode === "light" ? "Modo claro" :
    "Automático";

  return (
    <button
      onClick={cycleMode}
      className="flex items-center gap-2 p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
      title={`Tema: ${label} (clic para cambiar)`}
    >
      {icon}
      <span className="text-sm hidden sm:inline">{label}</span>
    </button>
  );
}
