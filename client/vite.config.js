import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    sourcemapIgnoreList: (sourcePath, sourcemapPath) => {
      return sourcemapPath.includes('installHook.js.map');
    },
  },
  build: {
    sourcemap: true,
  },
})
