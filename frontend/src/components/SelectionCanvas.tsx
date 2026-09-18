import { useState, useRef, useCallback, useEffect } from 'react';
import { listen } from '@tauri-apps/api/event';

interface SelectionRect {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

interface SelectionCanvasProps {
  onCapture?: (base64Image: string) => void;
}

export function SelectionCanvas({ onCapture }: SelectionCanvasProps) {
  const [isSelecting, setIsSelecting] = useState(false);
  const [selection, setSelection] = useState<SelectionRect | null>(null);
  const [isClickThrough, setIsClickThrough] = useState(true);
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const hotkeyLabel = isMac ? 'Option+T' : 'Alt+T';
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const unlisten = listen<boolean>('click-through-changed', (event) => {
      setIsClickThrough(event.payload);
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!isClickThrough) {
      setIsSelecting(true);
      setSelection({
        startX: e.clientX,
        startY: e.clientY,
        endX: e.clientX,
        endY: e.clientY,
      });
    }
  }, [isClickThrough]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isSelecting && selection) {
      setSelection({
        ...selection,
        endX: e.clientX,
        endY: e.clientY,
      });
    }
  }, [isSelecting, selection]);

  const handleMouseUp = useCallback(async () => {
    if (isSelecting && selection) {
      setIsSelecting(false);
      
      const width = Math.abs(selection.endX - selection.startX);
      const height = Math.abs(selection.endY - selection.startY);
      
      if (width > 10 && height > 10) {
        const base64Image = await captureRegion(selection);
        onCapture?.(base64Image);
      }
      
      setSelection(null);
    }
  }, [isSelecting, selection, onCapture]);

  const captureRegion = async (rect: SelectionRect): Promise<string> => {
    const canvas = canvasRef.current;
    if (!canvas) return '';
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return '';
    
    const x = Math.min(rect.startX, rect.endX);
    const y = Math.min(rect.startY, rect.endY);
    const width = Math.abs(rect.endX - rect.startX);
    const height = Math.abs(rect.endY - rect.startY);
    
    canvas.width = width;
    canvas.height = height;
    
    const imageData = ctx.getImageData(x, y, width, height);
    ctx.putImageData(imageData, 0, 0);
    
    const dataUrl = canvas.toDataURL('image/png');
    return dataUrl.split(',')[1];
  };

  const getSelectionStyle = (): React.CSSProperties => {
    if (!selection) return {};
    
    const x = Math.min(selection.startX, selection.endX);
    const y = Math.min(selection.startY, selection.endY);
    const width = Math.abs(selection.endX - selection.startX);
    const height = Math.abs(selection.endY - selection.startY);
    
    return {
      position: 'fixed',
      left: x,
      top: y,
      width,
      height,
      border: '2px dashed #007AFF',
      backgroundColor: 'rgba(0, 122, 255, 0.1)',
      pointerEvents: 'none',
      zIndex: 9999,
    };
  };

  return (
    <>
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      {selection && <div style={getSelectionStyle()} />}
      
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          cursor: isClickThrough ? 'default' : 'crosshair',
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      />
      
      <div
        style={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 10000,
          width: 40,
          height: 40,
          borderRadius: '50%',
          backgroundColor: isClickThrough ? 'rgba(0, 0, 0, 0.75)' : 'rgba(0, 122, 255, 0.9)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          userSelect: 'none',
        }}
        title={isClickThrough ? `Click-through ON (${hotkeyLabel} to toggle)` : `Selecting mode (${hotkeyLabel} to toggle)`}
      >
        {isClickThrough ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
            <circle cx="12" cy="12" r="3" fill="rgba(0,122,255,0.9)" stroke="white" strokeWidth="1.5" />
          </svg>
        )}
      </div>
    </>
  );
}
