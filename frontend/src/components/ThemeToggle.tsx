'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { Brightness4, Brightness7 } from '@mui/icons-material';

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();

  // Avoid hydration mismatch by only rendering after component is mounted
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-full hover:bg-opacity-10 hover:bg-white transition-colors"
      aria-label="Toggle Dark Mode"
    >
      {theme === 'dark' ? (
        <Brightness7 className="text-white" />
      ) : (
        <Brightness4 className="text-white" />
      )}
    </button>
  );
}
