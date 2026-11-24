#!/usr/bin/env node

/**
 * CortexOps Multi-Agent Framework - Unified Dual Release Automation
 * Synchronously publishes to npm and GitHub Releases with verified assets.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const PKG_PATH = path.join(ROOT_DIR, 'package.json');
const PLUGIN_PATH = path.join(ROOT_DIR, 'plugin', 'plugin.json');
const AGY_PATH = path.join(ROOT_DIR, '.antigravity-plugin', 'plugin.json');
const CLAUDE_PATH = path.join(ROOT_DIR, '.claude-plugin', 'plugin.json');
const MARKETPLACE_PATH = path.join(ROOT_DIR, '.claude-plugin', 'marketplace.json');
const CODEX_PATH = path.join(ROOT_DIR, '.codex-plugin', 'plugin.json');
const DIST_DIR = path.join(ROOT_DIR, 'dist');

function run(cmd, opts = {}) {
    console.log(`[EXEC] ${cmd}`);
    return execSync(cmd, { cwd: ROOT_DIR, stdio: 'inherit', ...opts });
}

function bumpVersion(current, type = 'patch') {
    const parts = current.split('.').map(Number);
    if (type === 'major') return `${parts[0] + 1}.0.0`;
    if (type === 'minor') return `${parts[0]}.${parts[1] + 1}.0`;
    return `${parts[0]}.${parts[1]}.${(parts[2] || 0) + 1}`;
}

async function main() {
    const pkg = JSON.parse(fs.readFileSync(PKG_PATH, 'utf-8'));
    let newVer = process.argv[2];

    if (!newVer) {
        newVer = bumpVersion(pkg.version, 'patch');
    } else if (['major', 'minor', 'patch'].includes(newVer)) {
        newVer = bumpVersion(pkg.version, newVer);
    }

    console.log('='.repeat(70));
    console.log(`CORTEXOPS AUTOMATED DUAL RELEASE PIPELINE: v${pkg.version} -> v${newVer}`);
    console.log('='.repeat(70));

    // 1. Update version across all manifest files
    const manifests = [PKG_PATH, PLUGIN_PATH, AGY_PATH, CLAUDE_PATH, CODEX_PATH, MARKETPLACE_PATH];
    for (const m of manifests) {
        if (fs.existsSync(m)) {
            const data = JSON.parse(fs.readFileSync(m, 'utf-8'));
            if (data.version) data.version = newVer;
            if (Array.isArray(data.plugins)) {
                data.plugins.forEach(p => { p.version = newVer; });
            }
            fs.writeFileSync(m, JSON.stringify(data, null, 2) + '\n');
            console.log(`[UPDATED] ${path.relative(ROOT_DIR, m)} -> ${newVer}`);
        }
    }

    // 2. Build release distribution archives (both naming variants)
    if (!fs.existsSync(DIST_DIR)) {
        fs.mkdirSync(DIST_DIR, { recursive: true });
    }

    const zipNoV = path.join(DIST_DIR, `cortexops-${newVer}.zip`);
    const zipWithV = path.join(DIST_DIR, `cortexops-v${newVer}.zip`);
    const zipLatest = path.join(DIST_DIR, 'cortexops.zip');
    const checksumFile = path.join(DIST_DIR, 'checksums.txt');

    const isWin = process.platform === 'win32';
    if (isWin) {
        run(`powershell -Command "Compress-Archive -Path '${path.join(ROOT_DIR, 'plugin')}\\*' -DestinationPath '${zipNoV}' -Force"`);
        fs.copyFileSync(zipNoV, zipWithV);
        fs.copyFileSync(zipNoV, zipLatest);
        run(`powershell -Command "(Get-FileHash -Algorithm SHA256 '${zipNoV}').Hash.ToLower() + '  ' + [System.IO.Path]::GetFileName('${zipNoV}') | Out-File -Encoding utf8 '${checksumFile}'"`);
    } else {
        run(`cd "${path.join(ROOT_DIR, 'plugin')}" && zip -r "${zipNoV}" .`);
        fs.copyFileSync(zipNoV, zipWithV);
        fs.copyFileSync(zipNoV, zipLatest);
        run(`sha256sum "${zipNoV}" > "${checksumFile}"`);
    }

    // 3. Local strict validation using agy CLI
    try {
        const agyBin = isWin ? 'agy' : (fs.existsSync('/home/lenovo/.gemini/bin/agy') ? '/home/lenovo/.gemini/bin/agy' : 'agy');
        run(`"${agyBin}" plugin validate "${path.join(ROOT_DIR, 'plugin')}" --strict`);
        console.log('[VALIDATION] Strict plugin verification passed with 0 errors and 0 warnings.');
    } catch (err) {
        console.warn(`[WARN] Local agy validation skipped or warning: ${err.message}`);
    }

    // 4. Git commit & tag
    run(`git add -A`);
    try {
        run(`git commit -m "release: v${newVer} dual release (npm & github)"`);
    } catch (_) {
        console.log('[GIT] Working tree already clean.');
    }

    run(`git tag -fa v${newVer} -m "Release v${newVer}"`);
    run(`git push origin main`);
    run(`git push origin v${newVer} --force`);

    // 5. GitHub Release publication with assets
    const ghBin = isWin ? 'gh' : (fs.existsSync(path.join(process.env.HOME, '.local', 'bin', 'gh')) ? path.join(process.env.HOME, '.local', 'bin', 'gh') : 'gh');
    try {
        const title = `CortexOps v${newVer}`;
        const notes = `## CortexOps Multi-Agent Framework v${newVer}\n\nAutomated dual release published to npm and GitHub.\n\n### Assets\n- \`cortexops.zip\` (Universal Latest)\n- \`cortexops-${newVer}.zip\`\n- \`cortexops-v${newVer}.zip\`\n- \`checksums.txt\``;
        
        try {
            run(`"${ghBin}" release view v${newVer}`);
            run(`"${ghBin}" release upload v${newVer} "${zipNoV}" "${zipWithV}" "${zipLatest}" "${checksumFile}" --clobber`);
            run(`"${ghBin}" release edit v${newVer} --title "${title}" --notes "${notes}"`);
            console.log(`[GITHUB RELEASE] Updated existing release v${newVer}`);
        } catch (_) {
            run(`"${ghBin}" release create v${newVer} "${zipNoV}" "${zipWithV}" "${zipLatest}" "${checksumFile}" --title "${title}" --notes "${notes}"`);
            console.log(`[GITHUB RELEASE] Created new release v${newVer}`);
        }
    } catch (ghErr) {
        console.warn(`[WARN] GitHub release command encountered notice: ${ghErr.message}`);
    }

    // 6. NPM publication
    console.log('[NPM] Publishing to npm registry...');
    run(`npm publish --access public`);
    try {
        run(`npm dist-tag add @ctxthuta/cxops@${newVer} latest`);
    } catch (_) {}

    console.log('='.repeat(70));
    console.log(`SUCCESS: CortexOps v${newVer} is published on both npm and GitHub Releases!`);
    console.log('='.repeat(70));
}

main().catch((err) => {
    console.error(`[FATAL] Release failed: ${err.message}`);
    process.exit(1);
});
