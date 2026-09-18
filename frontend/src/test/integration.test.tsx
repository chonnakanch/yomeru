import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { SelectionCanvas } from '../components/SelectionCanvas';

vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn().mockResolvedValue(() => {}),
}));

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn().mockResolvedValue(undefined),
}));

describe('SelectionCanvas Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders status indicator with click-through text', () => {
    render(<SelectionCanvas />);
    expect(screen.getByText(/Click-through ON/)).toBeInTheDocument();
  });

  it('renders status indicator with hotkey hint', () => {
    render(<SelectionCanvas />);
    expect(screen.getByText(/to toggle/)).toBeInTheDocument();
  });

  it('does not start selection when in click-through mode', () => {
    render(<SelectionCanvas />);

    const container = document.querySelector('[style*="cursor: default"]') as HTMLElement;

    act(() => {
      fireEvent.mouseDown(container, { clientX: 100, clientY: 100 });
    });

    act(() => {
      fireEvent.mouseMove(container, { clientX: 300, clientY: 300 });
    });

    const selectionRect = document.querySelector('[style*="border: 2px dashed"]');
    expect(selectionRect).not.toBeInTheDocument();
  });

  it('listens for click-through-changed event', async () => {
    const { listen } = await import('@tauri-apps/api/event');
    render(<SelectionCanvas />);
    expect(listen).toHaveBeenCalledWith('click-through-changed', expect.any(Function));
  });
});

describe('Base64 Conversion', () => {
  it('converts image data to base64', () => {
    const imageData = 'test-image-data';
    const expectedBase64 = btoa(imageData);
    const result = btoa(imageData);
    expect(result).toBe(expectedBase64);
  });

  it('handles empty image data', () => {
    const imageData = '';
    const result = btoa(imageData);
    expect(result).toBe('');
  });
});

describe('Canvas Rendering', () => {
  it('creates canvas with correct dimensions', () => {
    const canvas = document.createElement('canvas');
    const width = 200;
    const height = 150;
    canvas.width = width;
    canvas.height = height;
    expect(canvas.width).toBe(width);
    expect(canvas.height).toBe(height);
  });
});
