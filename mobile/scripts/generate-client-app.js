#!/usr/bin/env node

/**
 * Generate Client App
 * ====================
 * Creates a white-labeled React Native app for a specific client.
 *
 * Usage:
 *   node scripts/generate-client-app.js --client-id acme --name "Acme Corp" --primary "#ff5500"
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  params[args[i].replace('--', '')] = args[i + 1];
}

const clientId = params['client-id'] || 'internal';
const companyName = params['name'] || 'AI Agency';
const primaryColor = params['primary'] || '#6366f1';
const secondaryColor = params['secondary'] || '#8b5cf6';
const accentColor = params['accent'] || '#06b6d4';
const serverUrl = params['server-url'] || 'http://localhost:5001';

const outputDir = path.join(__dirname, '..', 'clients', clientId);

console.log(`Generating app for ${companyName} (${clientId})...`);

// Create directories
fs.mkdirSync(path.join(outputDir, 'src'), { recursive: true });

// Copy base template
const mobileDir = path.join(__dirname, '..');
const copyRecursive = (src, dest) => {
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
  for (const item of fs.readdirSync(src)) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    if (item === 'node_modules' || item === 'clients' || item === '.expo') continue;
    if (fs.statSync(srcPath).isDirectory()) {
      copyRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
};

copyRecursive(mobileDir, outputDir);

// Generate client config
const config = {
  clientId,
  companyName,
  theme: {
    primary: primaryColor,
    secondary: secondaryColor,
    accent: accentColor,
  },
  serverUrl,
  generatedAt: new Date().toISOString(),
};

fs.writeFileSync(
  path.join(outputDir, 'config', 'client.json'),
  JSON.stringify(config, null, 2)
);

// Update app.json with client branding
const appJsonPath = path.join(outputDir, 'app.json');
const appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf-8'));
appJson.expo.name = companyName;
appJson.expo.slug = `ai-agency-${clientId}`;
appJson.expo.ios.bundleIdentifier = `com.amanita.${clientId}`;
appJson.expo.android.package = `com.amanita.${clientId}`;
appJson.expo.splash.backgroundColor = primaryColor;
appJson.expo.android.adaptiveIcon.backgroundColor = primaryColor;
fs.writeFileSync(appJsonPath, JSON.stringify(appJson, null, 2));

// Update package.json
const pkgPath = path.join(outputDir, 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
pkg.name = `ai-agency-${clientId}`;
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));

// Generate default theme override
const themeOverride = `
import { applyBranding } from '../theme';

export const clientBranding = {
  primary_color: '${primaryColor}',
  secondary_color: '${secondaryColor}',
  accent_color: '${accentColor}',
  company_name: '${companyName}',
};
`;
fs.writeFileSync(path.join(outputDir, 'src', 'theme', 'clientBranding.ts'), themeOverride);

console.log(`\nApp generated at: ${outputDir}`);
console.log(`\nTo run:`);
console.log(`  cd ${outputDir}`);
console.log(`  npm install`);
console.log(`  npx expo start`);
console.log(`\nTo build:`);
console.log(`  npx expo install eas-cli`);
console.log(`  eas build -p ios`);
console.log(`  eas build -p android`);
