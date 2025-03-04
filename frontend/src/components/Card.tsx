'use client';

import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  elevation?: 1 | 2 | 3;
}

export default function Card({ children, title, className = '', elevation = 1 }: CardProps) {
  return (
    <div className={`bg-white dark:bg-card-dark rounded-lg elevation-${elevation} ${className}`}>
      {title && (
        <div className="border-b dark:border-gray-700 p-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{title}</h2>
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
}
