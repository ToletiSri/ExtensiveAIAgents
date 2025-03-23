// Web Worker for running Python code
self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");

let pyodide = null;

async function loadPyodideAndPackages() {
    pyodide = await loadPyodide();
    
    // Install required packages
    await pyodide.loadPackage(["micropip"]);
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install(['google-generativeai', 'yfinance', 'apscheduler'])
    `);

    try {
        // Load activity.py which imports UtilityFunctions.py
        const activityResponse = await fetch('activity.py');
        if (!activityResponse.ok) throw new Error('Failed to load activity.py');
        const activityCode = await activityResponse.text();

        // Run the Python code
        await pyodide.runPythonAsync(activityCode);

    } catch (error) {
        console.error('Error loading Python files:', error);
        throw error;
    }
}

// Initialize Pyodide
let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async function(e) {
    await pyodideReadyPromise;
    
    const { type, data } = e.data;
    
    try {
        if (type === 'decompose') {
            const result = await pyodide.runPythonAsync(`
                process_input(${JSON.stringify(data.prompt)})
            `);
            self.postMessage({ type: 'result', data: result.toJs() });
        } 
        else if (type === 'execute') {
            const result = await pyodide.runPythonAsync(`
                execute_task(${JSON.stringify(data.task)})
            `);
            self.postMessage({ type: 'result', data: result });
        }
    } catch (error) {
        self.postMessage({ type: 'error', error: error.message });
    }
};