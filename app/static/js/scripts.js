// Function to handle tab navigation
function openTab(evt, tabName) {
    var tabContent = document.getElementsByClassName("tab-content");
    for (var i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }

    var tabButtons = document.getElementsByClassName("tab-button");
    for (var i = 0; i < tabButtons.length; i++) {
        tabButtons[i].className = tabButtons[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Open default tab
document.getElementById("defaultTab").click();

// Handle file upload
document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);  // Change from file_path to file

        const response = await fetch('/data/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.error) {
            showError(data.error);
        } else {
            showSuccess('File processed successfully');
            updateDataInfo(data);
            enableTabs();
        }
    } catch (error) {
        showError('Error processing file');
        console.error(error);
    }
});

// Handle data cleaning
document.getElementById('clean-data-btn').addEventListener('click', async function() {
    const options = {
        drop_nulls: document.getElementById('drop-nulls').checked,
        drop_duplicates: document.getElementById('drop-duplicates').checked
    };

    try {
        const response = await fetch('/data/clean', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });

        const data = await response.json();
        if (data.error) {
            showError(data.error);
        } else {
            showSuccess('Data cleaned successfully');
            updateDataInfo(data);
        }
    } catch (error) {
        showError('Error cleaning data');
        console.error(error);
    }
});

// Utility functions
function showError(message) {
    const resultsDiv = document.querySelector('.results');
    resultsDiv.innerHTML = `<p class="error">${message}</p>`;
}

function showSuccess(message) {
    const resultsDiv = document.querySelector('.results');
    resultsDiv.innerHTML = `<p class="success">${message}</p>`;
}

function updateDataInfo(data) {
    const importResults = document.getElementById('import-results');
    importResults.innerHTML = `
        <div class="data-info">
            <h3>Data Information</h3>
            <div class="info-card">Rows: ${data.shape[0]}</div>
            <div class="info-card">Columns: ${data.shape[1]}</div>
            <div class="info-card">Memory: ${formatBytes(data.memory_usage)}</div>
            <div class="missing-values">
                ${Object.entries(data.missing)
                    .filter(([_, count]) => count > 0)
                    .map(([col, count]) => 
                        `<div class="missing-value-item">
                            <span>${col}</span>
                            <span>${count}</span>
                         </div>`
                    ).join('')}
            </div>
        </div>
        <div class="data-preview">
            <h3>Data Preview</h3>
            <table>
                <thead>
                    <tr>${data.columns.map(col => 
                        `<th>${col}</th>`
                    ).join('')}</tr>
                </thead>
                <tbody>
                    ${data.preview.map(row => 
                        `<tr>${data.columns.map(col => 
                            `<td>${row[col] ?? ''}</td>`
                        ).join('')}</tr>`
                    ).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    const units = ['KB', 'MB', 'GB'];
    let i = -1;
    do {
        bytes /= 1024;
        i++;
    } while (bytes >= 1024 && i < units.length - 1);
    return bytes.toFixed(1) + ' ' + units[i];
}

function enableTabs() {
    const tabs = document.querySelectorAll('.tab-button');
    tabs.forEach(tab => tab.disabled = false);
}