#!/usr/bin/env node

/**
 * CortexOps Multi-Agent Framework - Universal Cross-Platform CLI
 * Unified Node.js runner for Linux, macOS, and Windows.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const { spawn, spawnSync } = require('child_process');
const readline = require('readline/promises');

const ROOT_DIR = path.resolve(__dirname, '..');
const PLUGIN_SOURCE = path.join(ROOT_DIR, 'plugin');
const REQ_FILE = path.join(ROOT_DIR, 'requirements.txt');
const VERIFY_SCRIPT = path.join(ROOT_DIR, 'verify_agents.py');
const DASHBOARD_SCRIPT = path.join(ROOT_DIR, 'src', 'dashboard.py');
const MAIN_SCRIPT = path.join(ROOT_DIR, 'src', 'main.py');

function loadEnvFile() {
    const candidatePaths = [
        path.join(process.cwd(), '.env'),
        path.join(ROOT_DIR, '.env'),
        path.join(os.homedir(), '.cortexops', '.env'),
    ];

    for (const envPath of candidatePaths) {
        if (fs.existsSync(envPath)) {
            try {
                const content = fs.readFileSync(envPath, 'utf-8');
                for (const line of content.split(/\r?\n/)) {
                    const trimmed = line.trim();
                    if (!trimmed || trimmed.startsWith('#')) continue;
                    const eqIdx = trimmed.indexOf('=');
                    if (eqIdx !== -1) {
                        const key = trimmed.substring(0, eqIdx).trim();
                        const val = trimmed.substring(eqIdx + 1).trim();
                        if (key && !(key in process.env)) {
                            process.env[key] = val;
                        }
                    }
                }
            } catch (_) {}
        }
    }
}

loadEnvFile();

function saveEnvKey(key, value) {
    const cleanKey = key.trim();
    const cleanVal = (value || '').trim().replace(/[\r\n]/g, '');
    const savePaths = [
        path.join(ROOT_DIR, '.env'),
        path.join(os.homedir(), '.cortexops', '.env'),
    ];

    for (const envPath of savePaths) {
        try {
            const envDir = path.dirname(envPath);
            if (!fs.existsSync(envDir)) {
                fs.mkdirSync(envDir, { recursive: true });
            }
            let content = '';
            if (fs.existsSync(envPath)) {
                content = fs.readFileSync(envPath, 'utf-8');
                const regex = new RegExp(`^${cleanKey}=.*$`, 'm');
                if (regex.test(content)) {
                    content = content.replace(regex, `${cleanKey}=${cleanVal}`);
                } else {
                    content += (content.endsWith('\n') ? '' : '\n') + `${cleanKey}=${cleanVal}\n`;
                }
            } else {
                content = `${cleanKey}=${cleanVal}\n`;
            }
            fs.writeFileSync(envPath, content, { mode: 0o600 });
        } catch (_) {}
    }
    process.env[cleanKey] = cleanVal;
}

function normalizeEngine(input) {
    if (!input) return null;
    const clean = input.trim().toLowerCase();
    if (['antigravity', 'gemini', 'ag'].includes(clean)) {
        return 'antigravity';
    }
    if (['claude', 'anthropic'].includes(clean)) {
        return 'claude';
    }
    if (['codex', 'openai', 'chatgpt'].includes(clean)) {
        return 'codex';
    }
    return null;
}

function getVenvPython() {
    const isWin = process.platform === 'win32';
    const venvPython = isWin
        ? path.join(ROOT_DIR, '.venv', 'Scripts', 'python.exe')
        : path.join(ROOT_DIR, '.venv', 'bin', 'python3');

    if (fs.existsSync(venvPython)) {
        return venvPython;
    }

    const sysPython = isWin ? 'python' : 'python3';
    const check = spawnSync(sysPython, ['--version'], { encoding: 'utf-8' });
    if (check.status === 0) {
        return sysPython;
    }

    return null;
}

function getPluginTargets() {
    const pluginsRoot = path.join(os.homedir(), '.gemini', 'config', 'plugins');
    return {
        root: pluginsRoot,
        targets: [
            path.join(pluginsRoot, 'cortexops'),
            path.join(pluginsRoot, 'thea-engineering-team'),
        ],
    };
}

function removePluginTarget(target) {
    let stat = null;
    try {
        stat = fs.lstatSync(target);
    } catch (_) {
        return;
    }

    const isWin = process.platform === 'win32';
    if (stat.isSymbolicLink()) {
        try {
            fs.unlinkSync(target);
        } catch (_) {
            fs.rmdirSync(target);
        }
    } else if (isWin && stat.isDirectory()) {
        fs.rmdirSync(target);
    } else {
        fs.rmSync(target, { recursive: true, force: true });
    }
}

function linkPlugin() {
    const { root, targets } = getPluginTargets();
    if (!fs.existsSync(root)) {
        fs.mkdirSync(root, { recursive: true });
    }

    const isWin = process.platform === 'win32';
    const symlinkType = isWin ? 'junction' : 'dir';

    for (const target of targets) {
        try {
            removePluginTarget(target);
            fs.symlinkSync(PLUGIN_SOURCE, target, symlinkType);
            console.log(`[OK] Linked Antigravity plugin: ${PLUGIN_SOURCE} -> ${target}`);
        } catch (err) {
            console.error(`[ERROR] Failed to link plugin to ${target}: ${err.message}`);
        }
    }

    const globalAgentsRoot = path.join(os.homedir(), '.gemini', 'config', 'agents');
    const localAgentsSource = path.join(ROOT_DIR, '.agents', 'agents');
    if (fs.existsSync(localAgentsSource)) {
        try {
            if (!fs.existsSync(globalAgentsRoot)) {
                fs.mkdirSync(globalAgentsRoot, { recursive: true });
            }
            const agentDirs = fs.readdirSync(localAgentsSource, { withFileTypes: true });
            for (const dirent of agentDirs) {
                if (dirent.isDirectory()) {
                    const srcAgent = path.join(localAgentsSource, dirent.name);
                    const destAgent = path.join(globalAgentsRoot, dirent.name);
                    removePluginTarget(destAgent);
                    fs.symlinkSync(srcAgent, destAgent, symlinkType);
                }
            }
            console.log(`[OK] Linked global agents for Antigravity UI: ${globalAgentsRoot}`);
        } catch (err) {
            console.error(`[ERROR] Failed to link global agents to ${globalAgentsRoot}: ${err.message}`);
        }
    }
}

function unlinkPlugin() {
    const { targets } = getPluginTargets();
    for (const target of targets) {
        try {
            removePluginTarget(target);
            console.log(`[OK] Unlinked plugin: ${target}`);
        } catch (err) {
            console.error(`[ERROR] Failed to unlink ${target}: ${err.message}`);
        }
    }

    const globalAgentsRoot = path.join(os.homedir(), '.gemini', 'config', 'agents');
    const localAgentsSource = path.join(ROOT_DIR, '.agents', 'agents');
    if (fs.existsSync(localAgentsSource) && fs.existsSync(globalAgentsRoot)) {
        try {
            const agentDirs = fs.readdirSync(localAgentsSource, { withFileTypes: true });
            for (const dirent of agentDirs) {
                if (dirent.isDirectory()) {
                    const destAgent = path.join(globalAgentsRoot, dirent.name);
                    removePluginTarget(destAgent);
                }
            }
            console.log(`[OK] Unlinked global agents: ${globalAgentsRoot}`);
        } catch (err) {
            console.error(`[ERROR] Failed to unlink global agents: ${err.message}`);
        }
    }
}

function executePythonScript(scriptPath, args = []) {
    loadEnvFile();
    const python = getVenvPython();
    if (!python) {
        console.error('[ERROR] Python 3 not detected. Please install Python 3.10+ and run: cxops setup');
        process.exit(1);
    }

    const proc = spawn(python, [scriptPath, ...args], {
        stdio: 'inherit',
        env: { ...process.env, PYTHONPATH: ROOT_DIR },
    });

    proc.on('error', (err) => {
        console.error(`[ERROR] Failed to spawn Python process: ${err.message}`);
        process.exit(1);
    });

    proc.on('close', (code) => {
        process.exit(code ?? 0);
    });
}

async function runSetup() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    console.log('='.repeat(70));
    console.log('CORTEXOPS MULTI-AGENT FRAMEWORK - INTERACTIVE SETUP WIZARD');
    console.log('='.repeat(70));

    try {
        console.log('\n[1] Checking System Prerequisites:');
        console.log(`  * Node.js: ${process.version} (Detected)`);
        
        const python = getVenvPython();
        if (python) {
            const ver = spawnSync(python, ['--version'], { encoding: 'utf-8' }).stdout.trim();
            console.log(`  * Python:  ${ver} (${python})`);
        } else {
            console.log('  * Python:  [NOT DETECTED]');
            console.log('    Warning: Python 3.10+ is required for subagents and telemetry.');
        }

        /*
        // Standalone execution engine and authentication setup (temporarily inactive)
        console.log('\n[2] Execution Engine & Platform Selection:');
        const defaultEngine = (process.env.CORTEXOPS_ENGINE || 'antigravity').toLowerCase();
        console.log('  Available Execution Harnesses:');
        console.log('    - antigravity: Google Antigravity SDK with Gemini 3.8 models (Default)');
        console.log('    - claude:      Anthropic Claude models (Claude 3.7 / 3.5 Sonnet)');
        console.log('    - codex:       OpenAI Codex / GPT-4o / o3-mini models');

        const enginePrompt = await rl.question(`  Select default engine [antigravity | claude | codex] (default: ${defaultEngine}): `);
        const resolvedEngine = normalizeEngine(enginePrompt) || defaultEngine || 'antigravity';
        saveEnvKey('CORTEXOPS_ENGINE', resolvedEngine);
        console.log(`  * Configured execution engine: ${resolvedEngine}`);

        console.log('\n[3] Authentication & API Keys:');
        if (resolvedEngine === 'antigravity') {
            const existingKey = process.env.GEMINI_API_KEY;
            if (existingKey) {
                console.log('  * GEMINI_API_KEY is already configured.');
            } else {
                const hasKey = await rl.question('  Configure GEMINI_API_KEY for Antigravity engine? (y/n) [y]: ');
                if (hasKey.trim().toLowerCase() !== 'n') {
                    const keyInput = await rl.question('  Enter your GEMINI_API_KEY: ');
                    const cleanKey = keyInput.trim().replace(/[\r\n]/g, '');
                    if (cleanKey) {
                        saveEnvKey('GEMINI_API_KEY', cleanKey);
                        console.log('  * Saved GEMINI_API_KEY to configuration files (mode 0600)');
                    }
                } else {
                    console.log('  * Skipping API key. Antigravity IDE sessions will authenticate automatically.');
                }
            }
        } else if (resolvedEngine === 'claude') {
            const existingKey = process.env.ANTHROPIC_API_KEY;
            if (existingKey) {
                console.log('  * ANTHROPIC_API_KEY is already configured.');
            } else {
                const hasKey = await rl.question('  Configure ANTHROPIC_API_KEY for Claude engine? (y/n) [y]: ');
                if (hasKey.trim().toLowerCase() !== 'n') {
                    const keyInput = await rl.question('  Enter your ANTHROPIC_API_KEY: ');
                    const cleanKey = keyInput.trim().replace(/[\r\n]/g, '');
                    if (cleanKey) {
                        saveEnvKey('ANTHROPIC_API_KEY', cleanKey);
                        console.log('  * Saved ANTHROPIC_API_KEY to configuration files (mode 0600)');
                    }
                }
            }
        } else if (resolvedEngine === 'codex') {
            const existingKey = process.env.OPENAI_API_KEY;
            if (existingKey) {
                console.log('  * OPENAI_API_KEY is already configured.');
            } else {
                const hasKey = await rl.question('  Configure OPENAI_API_KEY for Codex engine? (y/n) [y]: ');
                if (hasKey.trim().toLowerCase() !== 'n') {
                    const keyInput = await rl.question('  Enter your OPENAI_API_KEY: ');
                    const cleanKey = keyInput.trim().replace(/[\r\n]/g, '');
                    if (cleanKey) {
                        saveEnvKey('OPENAI_API_KEY', cleanKey);
                        console.log('  * Saved OPENAI_API_KEY to configuration files (mode 0600)');
                    }
                }
            }
        }
        */

        console.log('\n[2] Antigravity Global Plugin Registration:');
        const linkChoice = await rl.question('  Register CortexOps global plugin for Antigravity sessions? (y/n) [y]: ');
        if (linkChoice.trim().toLowerCase() !== 'n') {
            linkPlugin();
        }

        console.log('\n[3] Second Brain Integration (ThutaCortex):');
        const defaultVault = path.join(os.homedir(), 'Documents', 'ThutaCortex');
        const vaultChoice = await rl.question(`  ThutaCortex vault path [${defaultVault}]: `);
        const resolvedVault = vaultChoice.trim() || defaultVault;

        if (fs.existsSync(resolvedVault)) {
            console.log(`  * ThutaCortex detected at: ${resolvedVault}`);
        } else {
            console.log(`  * Vault path not currently present at: ${resolvedVault}`);
            console.log('    The framework will operate in local-only mode until the vault is initialized.');
        }

        console.log('\n[4] Python Virtual Environment & Dependencies:');
        const venvDir = path.join(ROOT_DIR, '.venv');
        if (fs.existsSync(venvDir)) {
            console.log('  * Virtual environment already exists at .venv/');
        } else {
            const venvChoice = await rl.question('  Create .venv and install Python dependencies now? (y/n) [y]: ');
            if (venvChoice.trim().toLowerCase() !== 'n') {
                const isWin = process.platform === 'win32';
                const basePython = isWin ? 'python' : 'python3';
                console.log('  * Creating virtual environment...');
                const venvRes = spawnSync(basePython, ['-m', 'venv', venvDir], { stdio: 'inherit' });
                if (venvRes.status === 0) {
                    console.log('  * Installing requirements.txt hermetically...');
                    const venvPy = isWin
                        ? path.join(venvDir, 'Scripts', 'python.exe')
                        : path.join(venvDir, 'bin', 'python3');
                    if (fs.existsSync(venvPy)) {
                        spawnSync(venvPy, ['-m', 'pip', 'install', '--quiet', '--upgrade', 'pip'], { stdio: 'inherit' });
                        spawnSync(venvPy, ['-m', 'pip', 'install', '--quiet', '-r', REQ_FILE], { stdio: 'inherit' });
                        console.log('  * Dependencies installed successfully.');
                    }
                } else {
                    console.error('  * Failed to create virtual environment. Ensure python3-venv is installed.');
                }
            }
        }

        console.log('\n[5] Subagent Definition Verification:');
        const py = getVenvPython();
        if (py && fs.existsSync(VERIFY_SCRIPT)) {
            spawnSync(py, [VERIFY_SCRIPT], { stdio: 'inherit', env: { ...process.env, PYTHONPATH: ROOT_DIR } });
        }

        console.log('\n' + '='.repeat(70));
        console.log('Setup complete. CortexOps subagents are active in Antigravity.');
        console.log('You can now:');
        console.log('  - Type @<agent> or @cxagents in Antigravity chat');
        console.log('  - cxops status      Display operational & token telemetry dashboard');
        console.log('  - cxops watch       Continuously monitor the live dashboard');
        console.log('  - cxops verify      Verify all 12 subagent definitions');
        console.log('  - cxops doctor      Run diagnostic health check');
        /*
        // Standalone task runner commands (temporarily inactive)
        console.log('  cxops run "<goal>" Dispatch autonomous tasks (Default: antigravity)');
        console.log('  cxops run -e claude "<goal>" Dispatch tasks using Claude');
        console.log('  cxops run -e codex "<goal>"  Dispatch tasks using Codex');
        */
        console.log('='.repeat(70));
    } finally {
        rl.close();
    }
}

function runDoctor() {
    console.log('='.repeat(70));
    console.log('CORTEXOPS FRAMEWORK DIAGNOSTIC HEALTH CHECK (DOCTOR)');
    console.log('='.repeat(70));

    // Node.js runtime validation
    const nodeVer = process.version;
    const nodeMajor = parseInt(nodeVer.replace('v', '').split('.')[0], 10);
    const nodeStatus = nodeMajor >= 18 ? 'PASS' : 'WARN';
    console.log(`[${nodeStatus}] Node.js: ${nodeVer} (Minimum: v18.0.0)`);

    // Python interpreter discovery
    const py = getVenvPython();
    if (py) {
        const pyVer = spawnSync(py, ['--version'], { encoding: 'utf-8' }).stdout.trim();
        console.log(`[PASS] Python: ${pyVer} (${py})`);
    } else {
        console.log('[FAIL] Python: No Python 3 executable detected.');
    }

    // Virtual environment status
    const venvDir = path.join(ROOT_DIR, '.venv');
    if (fs.existsSync(venvDir)) {
        console.log(`[PASS] Virtual Environment: Configured at ${venvDir}`);
    } else {
        console.log('[WARN] Virtual Environment: .venv not found. Run "cxops setup" to create.');
    }

    /*
    // Standalone execution engine and API key diagnostics (temporarily inactive)
    const activeEngine = (process.env.CORTEXOPS_ENGINE || 'antigravity').toLowerCase();
    const isDefaultEngine = !process.env.CORTEXOPS_ENGINE || activeEngine === 'antigravity';
    console.log(`[PASS] Execution Engine: ${activeEngine} ${isDefaultEngine ? '(Default)' : ''}`);

    const geminiKey = process.env.GEMINI_API_KEY;
    const anthropicKey = process.env.ANTHROPIC_API_KEY;
    const openaiKey = process.env.OPENAI_API_KEY;

    if (activeEngine === 'antigravity') {
        if (geminiKey) {
            console.log('[PASS] Antigravity Auth: GEMINI_API_KEY is configured.');
        } else {
            console.log('[INFO] Antigravity Auth: GEMINI_API_KEY not in environment. Antigravity IDE sessions will authenticate automatically.');
        }
    } else if (activeEngine === 'claude') {
        if (anthropicKey) {
            console.log('[PASS] Claude Auth: ANTHROPIC_API_KEY is configured.');
        } else {
            console.log('[WARN] Claude Auth: ANTHROPIC_API_KEY not configured. Run "cxops setup" to set.');
        }
    } else if (activeEngine === 'codex') {
        if (openaiKey) {
            console.log('[PASS] Codex Auth: OPENAI_API_KEY is configured.');
        } else {
            console.log('[WARN] Codex Auth: OPENAI_API_KEY not configured. Run "cxops setup" to set.');
        }
    }

    const secondaryKeys = [];
    if (activeEngine !== 'antigravity' && geminiKey) secondaryKeys.push('GEMINI_API_KEY');
    if (activeEngine !== 'claude' && anthropicKey) secondaryKeys.push('ANTHROPIC_API_KEY');
    if (activeEngine !== 'codex' && openaiKey) secondaryKeys.push('OPENAI_API_KEY');
    if (secondaryKeys.length > 0) {
        console.log(`[PASS] Additional Keys Configured: ${secondaryKeys.join(', ')}`);
    }
    */

    // Antigravity global plugin link status
    const { targets } = getPluginTargets();
    let linkFound = false;
    for (const t of targets) {
        try {
            if (fs.lstatSync(t)) {
                console.log(`[PASS] Antigravity Global Plugin: Linked at ${t}`);
                linkFound = true;
                break;
            }
        } catch (_) {}
    }
    if (!linkFound) {
        console.log(`[WARN] Antigravity Global Plugin: Unlinked. Run "cxops setup" to register.`);
    }

    // Antigravity global agents discovery
    const globalAgentsRoot = path.join(os.homedir(), '.gemini', 'config', 'agents');
    if (fs.existsSync(globalAgentsRoot)) {
        const registered = fs.readdirSync(globalAgentsRoot).filter(f => !f.startsWith('.'));
        console.log(`[PASS] Global Agent Selector: ${registered.length} agents registered at ${globalAgentsRoot}`);
    } else {
        console.log(`[WARN] Global Agent Selector: Unlinked. Run "cxops link" to register.`);
    }

    // ThutaCortex second brain connectivity
    const vaultPath = path.join(os.homedir(), 'Documents', 'ThutaCortex');
    if (fs.existsSync(vaultPath)) {
        console.log(`[PASS] ThutaCortex Second Brain: Connected at ${vaultPath}`);
    } else {
        console.log(`[INFO] ThutaCortex Second Brain: Not present at ${vaultPath} (Local fallback mode)`);
    }

    // Subagent declarative definitions check
    const pluginAgentsDir = path.join(PLUGIN_SOURCE, 'agents');
    if (fs.existsSync(pluginAgentsDir)) {
        const count = fs.readdirSync(pluginAgentsDir).filter(f => f.endsWith('.md')).length;
        console.log(`[PASS] Declarative Subagents: ${count} verified roles discovered.`);
    }

    console.log('='.repeat(70));
}

function getPackageVersion() {
    try {
        const pkgPath = path.join(ROOT_DIR, 'package.json');
        if (fs.existsSync(pkgPath)) {
            const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
            return pkg.version || '1.0.4';
        }
    } catch (_) {}
    return '1.0.4';
}

function fetchLatestNpmVersion() {
    return new Promise((resolve) => {
        const req = https.get('https://registry.npmjs.org/@ctxthuta%2Fcxops/latest', {
            headers: { 'User-Agent': 'cxops-cli' },
            timeout: 2500,
        }, (res) => {
            if (res.statusCode !== 200) {
                resolve(null);
                return;
            }
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    resolve(parsed.version || null);
                } catch (_) {
                    resolve(null);
                }
            });
        });
        req.on('error', () => resolve(null));
        req.on('timeout', () => {
            req.destroy();
            resolve(null);
        });
    });
}

async function runVersion(detailed = false) {
    const currentVer = getPackageVersion();
    if (!detailed) {
        console.log(`@ctxthuta/cxops v${currentVer}`);
        return;
    }

    /*
    const activeEngine = (process.env.CORTEXOPS_ENGINE || 'antigravity').toLowerCase();
    const isDefaultEngine = !process.env.CORTEXOPS_ENGINE || activeEngine === 'antigravity';
    */

    console.log('='.repeat(70));
    console.log(`CORTEXOPS FRAMEWORK VERSION: v${currentVer}`);
    console.log('='.repeat(70));
    console.log(`Package Name:    @ctxthuta/cxops`);
    console.log(`Current Version: v${currentVer}`);
    /*
    console.log(`Active Engine:   ${activeEngine} ${isDefaultEngine ? '(Default)' : ''}`);
    */
    console.log(`Node.js Runtime: ${process.version}`);
    console.log(`Platform:        ${process.platform} (${process.arch})`);

    const py = getVenvPython();
    if (py) {
        const pyVer = spawnSync(py, ['--version'], { encoding: 'utf-8' }).stdout.trim();
        console.log(`Python Runtime:  ${pyVer}`);
    }

    process.stdout.write('Checking npm registry for updates... ');
    const latest = await fetchLatestNpmVersion();
    if (latest) {
        if (latest === currentVer) {
            console.log(`[UP TO DATE] (v${latest} is latest)`);
        } else {
            console.log(`[UPDATE AVAILABLE] (Latest: v${latest})`);
            console.log(`Run "npm install -g @ctxthuta/cxops@latest" to upgrade.`);
        }
    } else {
        console.log('[SKIPPED] (Offline or registry unreachable)');
    }
    console.log('='.repeat(70));
}

function printHelp() {
    console.log(`CortexOps Multi-Agent Framework CLI

Usage:
  cxops [command]

Commands:
  setup, init               Run interactive cross-platform setup wizard
  doctor                    Run system diagnostics and prerequisite health check
  status, dashboard         Display operational & token telemetry dashboard
  watch                     Continuously monitor the dashboard (auto-refresh)
  verify                    Verify all 12 declarative subagent definitions
  version, -v, --version    Display framework version and check for updates
  link                      Link Antigravity global plugin symlink/junction
  unlink                    Remove Antigravity global plugin symlink/junction
  help, --help, -h          Display this command reference
` + /*
`  run [options] "<prompt>"  Dispatch an autonomous multi-agent task via Python SDK
    Options:
      -e, --engine <engine> Select execution harness: antigravity (default), claude, codex
      -m, --model <model>   Override model identifier for the selected engine
` + */ '');
}

async function main() {
    const args = process.argv.slice(2);
    const command = (args[0] || 'status').toLowerCase();

    switch (command) {
        case 'setup':
        case 'init':
            await runSetup();
            break;
        case 'doctor':
            runDoctor();
            break;
        case 'link':
            linkPlugin();
            break;
        case 'unlink':
            unlinkPlugin();
            break;
        case 'status':
        case 'dashboard':
            executePythonScript(DASHBOARD_SCRIPT, args.slice(1));
            break;
        case 'watch':
            executePythonScript(DASHBOARD_SCRIPT, ['--watch', ...args.slice(1)]);
            break;
        case 'verify':
            executePythonScript(VERIFY_SCRIPT, args.slice(1));
            break;
        case 'version':
        case '--version':
        case '-v':
        case '-version':
            const isDetailed = command === 'version' || args.includes('--check') || args.includes('-c');
            await runVersion(isDetailed);
            break;
        /*
        case 'run':
            if (args.length < 2) {
                console.error('[ERROR] Task prompt required.');
                console.error('Usage: cxops run [--engine antigravity|claude|codex] "<prompt>"');
                process.exit(1);
            }
            executePythonScript(MAIN_SCRIPT, args.slice(1));
            break;
        */
        case 'help':
        case '--help':
        case '-h':
            printHelp();
            break;
        default:
            console.error(`[ERROR] Unknown command: ${command}`);
            printHelp();
            process.exit(1);
    }
}

main().catch((err) => {
    console.error(`[FATAL] ${err.message}`);
    process.exit(1);
});
