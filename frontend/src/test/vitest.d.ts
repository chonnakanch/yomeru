/// <reference types="vitest" />
import type { Assertion } from 'vitest';

declare module 'vitest' {
  interface Assertion<T = any> {
    toBeInTheDocument(): T;
    toHaveBeenCalled(): T;
    toHaveBeenCalledWith(...args: any[]): T;
    toBeNull(): T;
    not: Assertion<T>;
  }
}
