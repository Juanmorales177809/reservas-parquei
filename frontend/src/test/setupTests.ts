import '@testing-library/jest-dom/vitest';

import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Limpieza de DOM entre tests y aislamiento de localStorage.
afterEach(() => {
  cleanup();
  window.localStorage.clear();
});
