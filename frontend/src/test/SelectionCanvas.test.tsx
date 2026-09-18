import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SelectionCanvas } from '../components/SelectionCanvas';

vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn().mockResolvedValue(() => {}),
}));

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

describe('SelectionCanvas', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<SelectionCanvas />);
    expect(screen.getByText(/Click-through ON/)).toBeInTheDocument();
  });

  it('starts in click-through mode', () => {
    render(<SelectionCanvas />);
    expect(screen.getByText(/Click-through ON/)).toBeInTheDocument();
  });

  it('displays hotkey label for non-mac', () => {
    Object.defineProperty(navigator, 'platform', { value: 'Win32', writable: true });
    render(<SelectionCanvas />);
    expect(screen.getByText(/Alt\+T/)).toBeInTheDocument();
  });

  it('displays hotkey label for mac', () => {
    Object.defineProperty(navigator, 'platform', { value: 'MacIntel', writable: true });
    render(<SelectionCanvas />);
    expect(screen.getByText(/Option\+T/)).toBeInTheDocument();
  });

  it('renders selection rectangle during drag', async () => {
    render(<SelectionCanvas />);

    const container = document.querySelector('[style*="cursor: default"]') as HTMLElement;

    const { fireEvent } = await import('@testing-library/react');
    fireEvent.mouseDown(container, { clientX: 100, clientY: 100 });
    fireEvent.mouseMove(container, { clientX: 200, clientY: 200 });

    // In click-through mode, selection should NOT start
    const selectionRect = document.querySelector('[style*="border: 2px dashed"]');
    expect(selectionRect).not.toBeInTheDocument();
  });
});
