// Initialize Socket.IO connection
console.log('Initializing Socket.IO connection');
const socket = io('http://127.0.0.1:5000', {
    transports: ['polling', 'websocket'],  // Try polling first, then websocket
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
    autoConnect: true,
    forceNew: true,
    path: '/socket.io'
});

const activityInput = document.getElementById('activityInput');
const submitBtn = document.getElementById('submitBtn');
const executeBtn = document.getElementById('executeBtn');
const responseSection = document.getElementById('responseSection');
const responseContainer = document.getElementById('responseContainer');
let currentTasks = [];

// Add a function to append log messages
function appendLog(message) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.textContent = message;
    responseContainer.appendChild(logEntry);
    responseContainer.scrollTop = responseContainer.scrollHeight;
}

// Connect to WebSocket server
socket.on('connect', () => {
    console.log('Connected to server');
    appendLog('Connected to server successfully!');
    responseSection.classList.remove('hidden');
});

socket.on('connect_error', (error) => {
    console.log('Connection error:', error);
    console.log('Transport:', socket.io.engine.transport.name);
    appendLog(`Error: Connection failed. Transport: ${socket.io.engine.transport.name}. Please make sure the server is running.`);
    responseSection.classList.remove('hidden');
});

socket.io.on('error', (error) => {
    console.log('Socket.IO error:', error);
});

socket.io.on('reconnect_attempt', (attempt) => {
    console.log('Reconnection attempt:', attempt);
});

socket.io.on('transport', (transport) => {
    console.log('Transport changed to:', transport.name);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    appendLog('Disconnected from server');
    responseSection.classList.remove('hidden');
});

// Handle logs from the server
socket.on('log', (data) => {
    console.log('Server log:', data.message);
    appendLog(data.message);
});

// Handle error messages
socket.on('error', (data) => {
    console.error('Server error:', data.message);
    appendLog(`Error: ${data.message}`);
});

// Handle task messages
socket.on('tasks', (data) => {
    console.log('Received tasks:', data);
    currentTasks = data.tasks;
    appendLog('Tasks received from server');
    executeBtn.classList.remove('hidden');
});

// Handle submit button click
submitBtn.addEventListener('click', () => {
    console.log('Submit button clicked');
    const activity = activityInput.value.trim();
    if (!activity) {
        console.log('No activity provided');
        appendLog('Please enter an activity');
        return;
    }

    console.log('Sending activity to server:', activity);
    // Emit decompose_task event
    socket.emit('decompose_task', { activity }, (response) => {
        console.log('Received response:', response);
        if (response.error) {
            appendLog(`Error: ${response.error}`);
            return;
        }

        // Show the response section
        responseSection.classList.remove('hidden');
        
        // Clear previous responses
        responseContainer.innerHTML = '';
        currentTasks = [];

        // Display each task
        response.tasks.forEach(task => {
            if (task !== 'finish') {
                currentTasks.push(task);
                const taskElement = document.createElement('div');
                taskElement.textContent = JSON.stringify(task, null, 2);
                responseContainer.appendChild(taskElement);
            }
        });

        // Show execute button if tasks are available
        if (currentTasks.length > 0) {
            executeBtn.classList.remove('hidden');
        }
    });
});

// Handle execute button click
executeBtn.addEventListener('click', () => {
    console.log('Execute button clicked');
    currentTasks.forEach(task => {
        console.log('Executing task:', task);
        // Emit execute_task event for each task
        socket.emit('execute_task', { task }, (response) => {
            console.log('Task execution response:', response);
            if (response.error) {
                const resultElement = document.createElement('div');
                resultElement.textContent = `Error: ${response.error}`;
                responseContainer.appendChild(resultElement);
                return;
            }

            const resultElement = document.createElement('div');
            resultElement.textContent = response.message;
            responseContainer.appendChild(resultElement);
        });
    });
});
