'use client';

import Link from 'next/link';
import ThemeToggle from './ThemeToggle';
import { AudioFile, Home, Settings } from '@mui/icons-material';

export default function Header() {
  return (
    <header className="bg-primary-700 dark:bg-primary-900 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <AudioFile className="text-2xl" />
          <Link href="/" className="text-2xl font-bold">
            FlacJacket
          </Link>
        </div>
        
        <div className="flex items-center space-x-4">
          <Link 
            href="/" 
            className="flex items-center space-x-1 hover:text-gray-200 transition-colors"
          >
            <Home />
            <span>Home</span>
          </Link>
          
          <Link 
            href="/admin" 
            className="flex items-center space-x-1 hover:text-gray-200 transition-colors"
          >
            <Settings />
            <span>Admin</span>
          </Link>
          
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
