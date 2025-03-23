document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    const submitBtn = document.getElementById('submitBtn');
    const taskArea = document.getElementById('taskArea');
    const taskButton = document.getElementById('taskButton');
    const resultBox = document.getElementById('resultBox');
    const loadingIndicator = document.getElementById('loading');

    let currentTasks = [];
    let currentTaskIndex = 0;
    
    // Create Pyodide worker
    const worker = new Worker('pyodide_worker.js');

    // Handle worker messages
    worker.onmessage = function(e) {
        loadingIndicator.style.display = 'none';
        submitBtn.disabled = false;
        taskButton.disabled = false;

        if (e.data.type === 'error') {
            resultBox.textContent = `Error: ${e.data.error}`;
            return;
        }

        if (e.data.type === 'result') {
            if (Array.isArray(e.data.data)) {
                // Handle decomposition result
                currentTasks = e.data.data;
                currentTaskIndex = 0;
                taskArea.style.display = 'block';
                updateTaskButton();
                resultBox.textContent = '';
            } else {
                // Handle task execution result
                resultBox.textContent = e.data.data;
                currentTaskIndex++;
                if (currentTaskIndex < currentTasks.length) {
                    updateTaskButton();
                } else {
                    taskButton.textContent = 'FINISHED';
                    taskButton.disabled = true;
                }
            }
        }
    };

    // Handle initial task submission
    submitBtn.addEventListener('click', function() {
        const prompt = userInput.value.trim();
        if (!prompt) return;

        loadingIndicator.style.display = 'block';
        submitBtn.disabled = true;
        
        worker.postMessage({
            type: 'decompose',
            data: { prompt: prompt }
        });
    });

    // Handle task execution
    taskButton.addEventListener('click', function() {
        if (currentTaskIndex >= currentTasks.length) return;

        loadingIndicator.style.display = 'block';
        taskButton.disabled = true;
        
        worker.postMessage({
            type: 'execute',
            data: { task: currentTasks[currentTaskIndex] }
        });
    });

    function updateTaskButton() {
        if (currentTaskIndex < currentTasks.length) {
            taskButton.textContent = currentTasks[currentTaskIndex];
            taskButton.disabled = false;
        }
    }
});