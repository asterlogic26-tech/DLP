import fs from 'fs';
import path from 'path';

// Only run on non-Windows platforms (like Vercel/Linux)
if (process.platform !== 'win32') {
  try {
    const vitePath = path.resolve('node_modules', '.bin', 'vite');
    if (fs.existsSync(vitePath)) {
      fs.chmodSync(vitePath, '755'); // Make executable
      console.log('Fixed permissions for vite binary');
    }
  } catch (e) {
    console.log('Skipping permission fix (not needed or failed)');
  }
}
