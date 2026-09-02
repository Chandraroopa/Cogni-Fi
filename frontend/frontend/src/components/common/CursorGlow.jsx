import React, { useEffect, useState } from 'react';

function CursorGlow() {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setPosition({
        x: e.clientX,
        y: e.clientY,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div
      className="pointer-events-none fixed z-[9999] hidden h-40 w-40 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400/20 blur-3xl md:block"
      style={{
        left: position.x,
        top: position.y,
      }}
    />
  );
}

export default CursorGlow;