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
    clearError();
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
            updateProfileData();
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
    const errorDiv = document.getElementById('import-error');
    if (errorDiv) {
        errorDiv.textContent = message;
    }
}

function clearError() {
    const errorDiv = document.getElementById('import-error');
    if (errorDiv) {
        errorDiv.textContent = '';
    }
}

function showSuccess(message) {
    const resultsDiv = document.querySelector('.results');
    resultsDiv.innerHTML = `<p class="success">${message}</p>`;
}

function updateProfile(data) {
    updateDatatypesSummary(data.dtypes);
    updateMissingData(data.missing);
    updateNumericStats(data.numeric_summary);
    createCorrelationMatrix(data.correlation);
}

function updateDataInfo(data) {
    const infoCards = document.querySelector('.info-cards');
    infoCards.innerHTML = `
        <h3>Data Information</h3>
        <div class="info-card">
            <span>Rows:</span>
            <span>${data.shape[0]}</span>
        </div>
        <div class="info-card">
            <span>Columns:</span>
            <span>${data.shape[1]}</span>
        </div>
        <div class="info-card">
            <span>Size:</span>
            <span>${formatBytes(data.memory_usage)}</span>
        </div>
    `;

    fetch('/data/profile')
        .then(response => response.json())
        .then(profileData => {
            if (!profileData.error) {
                updateDatatypesSummary(profileData.dtypes);
                updateMissingData(profileData.missing);
                if (profileData.numeric_summary) {
                    const numericStats = document.getElementById('numeric-stats');
                    numericStats.innerHTML = createNumericTable(profileData.numeric_summary);
                }
                if (profileData.categorical_summary) {
                    const categoricalStats = document.getElementById('categorical-stats');
                    categoricalStats.innerHTML = createCategoricalTable(profileData.categorical_summary);
                }
                if (profileData.correlation) {
                    createCorrelationMatrix(profileData.correlation);
                }
            }
        })
        .catch(error => console.error('Error updating profile:', error));

    const numericStats = document.getElementById('numeric-stats');
    if (numericStats) {
        numericStats.innerHTML = `
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Mean</th>
                        <th>Std</th>
                        <th>Min</th>
                        <th>Max</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.numeric_summary || {}).map(([col, stats]) => `
                        <tr>
                            <td>${col}</td>
                            <td>${stats.mean.toFixed(2)}</td>
                            <td>${stats.std.toFixed(2)}</td>
                            <td>${stats.min}</td>
                            <td>${stats.max}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    const categoricalStats = document.getElementById('categorical-stats');
    if (categoricalStats) {
        categoricalStats.innerHTML = `
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Value</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.categorical_summary || {}).map(([col, values]) => 
                        Object.entries(values).map(([val, count]) => `
                            <tr>
                                <td>${col}</td>
                                <td>${val}</td>
                                <td>${count}</td>
                            </tr>
                        `).join('')
                    ).join('')}
                </tbody>
            </table>
        `;
    }
    
    const dataPreview = document.querySelector('.data-preview');
    dataPreview.innerHTML = `
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


async function updateProfileData() {
    try {
        const response = await fetch('/data/profile');
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }

        const numericStats = document.getElementById('numeric-stats');
        const categoricalStats = document.getElementById('categorical-stats');

        if (data.numeric_summary) {
            numericStats.innerHTML = createNumericTable(data.numeric_summary);
        }

        if (data.categorical_summary) {
            categoricalStats.innerHTML = createCategoricalTable(data.categorical_summary);
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}

function createNumericTable(summary) {
    return `
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Mean</th>
                    <th>Std</th>
                    <th>Min</th>
                    <th>Max</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(summary).map(([col, stats]) => `
                    <tr>
                        <td>${col}</td>
                        <td>${Number(stats.mean).toFixed(2)}</td>
                        <td>${Number(stats.std).toFixed(2)}</td>
                        <td>${stats.min}</td>
                        <td>${stats.max}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function createCategoricalTable(summary) {
    return `
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Value</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(summary).map(([col, values]) => 
                    Object.entries(values).map(([val, count]) => `
                        <tr>
                            <td>${col}</td>
                            <td>${val}</td>
                            <td>${count}</td>
                        </tr>
                    `).join('')
                ).join('')}
            </tbody>
        </table>
    `;
}


function enableTabs() {
    const tabs = document.querySelectorAll('.tab-button');
    tabs.forEach(tab => tab.disabled = false);
}

function updatePlotSelectors(data) {
    const columns = data.columns;
    populateColumnSelectors(columns);
}

function populateColumnSelectors(columns) {
    const xSelect = document.getElementById('column-x');
    const ySelect = document.getElementById('column-y');
    
    xSelect.innerHTML = columns.map(col => 
        `<option value="${col}">${col}</option>`
    ).join('');
    ySelect.innerHTML = xSelect.innerHTML;
}

document.getElementById('plot-type').addEventListener('change', function() {
    const ySelect = document.getElementById('column-y');
    ySelect.style.display = this.value === 'scatter' ? 'inline-block' : 'none';
});

async function createVisualization() {
    const plotType = document.getElementById('plot-type').value;
    const columnX = document.getElementById('column-x').value;
    const columnY = document.getElementById('column-y').value;
    
    try {
        const response = await fetch('/data/visualize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: plotType,
                x: columnX,
                y: plotType === 'scatter' ? columnY : null
            })
        });

        const data = await response.json();
        if (data.error) {
            showError(data.error);
        } else {
            Plotly.newPlot('plot-container', data.data);
        }
    } catch (error) {
        showError('Error creating visualization');
        console.error(error);
    }
}

function updateDatatypesSummary(dtypes) {
    const dtypesStats = document.getElementById('dtypes-stats');
    dtypesStats.innerHTML = `
        <div class="dtype-pie" id="dtype-chart"></div>
        <div class="dtype-details">
            ${Object.entries(dtypes.details).map(([col, type]) => 
                `<div class="dtype-item">
                    <span>${col}</span>
                    <span>${type}</span>
                </div>`
            ).join('')}
        </div>
    `;
    
    Plotly.newPlot('dtype-chart', [{
        values: [dtypes.numeric, dtypes.categorical],
        labels: ['Numeric', 'Categorical'],
        type: 'pie'
    }], {
        height: 150,
        margin: {t: 0, b: 0, l: 0, r: 0}
    });
}

function createCorrelationMatrix(correlation) {
    const data = [{
        type: 'heatmap',
        z: Object.values(correlation).map(row => Object.values(row)),
        x: Object.keys(correlation),
        y: Object.keys(correlation),
        colorscale: 'RdBu'
    }];
    
    Plotly.newPlot('correlation-plot', data, {
        margin: {t: 25, b: 25, l: 25, r: 25}
    });
}

function updateMissingData(missing) {
    const missingStats = document.getElementById('missing-stats');
    missingStats.innerHTML = `
        <div class="missing-overview">
            <p>Total Missing: ${missing.total}</p>
        </div>
        <div class="missing-details">
            ${Object.entries(missing.by_column).map(([col, count]) => `
                <div class="missing-item">
                    <span>${col}</span>
                    <span>${count} (${missing.percentage[col]}%)</span>
                </div>
            `).join('')}
        </div>
    `;
}