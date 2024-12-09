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

    const columnSelect = document.getElementById('column-x');
    columnSelect.innerHTML = data.columns.map(col => 
        `<option value="${col}">${col}</option>`
    ).join('');

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
            // Store global state
            window.currentCategoricalSummary = data.categorical_summary;
            
            // Update select options
            const select = document.getElementById('category-select');
            const columns = Object.keys(data.categorical_summary);
            
            select.innerHTML = `
                <option value="all">All Columns</option>
                ${columns.map(col => 
                    `<option value="${col}">${col}</option>`
                ).join('')}
            `;
            
            // Update table
            const categoricalStats = document.getElementById('categorical-stats');
            categoricalStats.innerHTML = createCategoricalTable(data.categorical_summary, 'all');
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

function updateCategorySelect(summary) {
    window.currentCategoricalSummary = summary;

    const select = document.getElementById('category-select');
    const columns = Object.keys(summary);
    
    select.innerHTML = `
        <option value="all">All Columns</option>
        ${columns.map(col => 
            `<option value="${col}">${col}</option>`
        ).join('')}
    `;

    const categoricalStats = document.getElementById('categorical-stats');
    categoricalStats.innerHTML = createCategoricalTable(summary, 'all');
}

function createCategoricalTable(summary, selectedColumn = 'all') {
    const filteredSummary = selectedColumn === 'all' ? 
        summary : 
        {[selectedColumn]: summary[selectedColumn]};
        
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
                ${Object.entries(filteredSummary).map(([col, values]) => 
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

// Add event listener
document.getElementById('category-select')?.addEventListener('change', function() {
    if (!window.currentCategoricalSummary) return;
    
    const categoricalStats = document.getElementById('categorical-stats');
    categoricalStats.innerHTML = createCategoricalTable(
        window.currentCategoricalSummary, 
        this.value
    );
});

// Update updateProfileData function
if (data.categorical_summary) {
    window.currentCategoricalSummary = data.categorical_summary;
    updateCategorySelect(data.categorical_summary);
    categoricalStats.innerHTML = createCategoricalTable(data.categorical_summary);
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
    if (!columns || !Array.isArray(columns)) return;
    
    const xSelect = document.getElementById('column-x');
    const ySelect = document.getElementById('column-y');
    
    if (!xSelect || !ySelect) return;
    
    const options = columns.map(col => 
        `<option value="${col}">${col}</option>`
    ).join('');
    
    xSelect.innerHTML = options;
    ySelect.innerHTML = options;
}

function handleUploadSuccess(data) {
    updateDataInfo(data);
    populateColumnSelectors(data.columns);
    enableTabs();
}

document.getElementById('plot-type').addEventListener('change', function() {
    const ySelect = document.getElementById('column-y');
    ySelect.style.display = this.value === 'scatter' ? 'inline-block' : 'none';
});

async function createVisualization() {
    const plotType = document.getElementById('plot-type');
    const columnX = document.getElementById('column-x');
    const columnY = document.getElementById('column-y');
    
    // Validate inputs
    if (!plotType || !columnX || !columnX.value) {
        showError('Please select valid columns');
        return;
    }
    
    try {
        const response = await fetch('/data/visualize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: plotType.value,
                x: columnX.value,
                y: plotType.value === 'scatter' && columnY ? columnY.value : null
            })
        });

        const result = await response.json();
        
        if (result.error) {
            showError(result.error);
            return;
        }

        // Result already contains the plot data, no need for JSON.parse
        const layout = {
            title: `${plotType.value.charAt(0).toUpperCase() + plotType.value.slice(1)} of ${columnX.value}`,
            xaxis: {title: columnX.value},
            yaxis: {title: plotType.value === 'scatter' ? columnY.value : 'Count'},
            font: {
                family: 'JetBrains Mono'
            },
            colorway: ['#1e1e1e']
        };

        Plotly.newPlot('plot-container', result.data, layout);

    } catch (error) {
        showError('Error creating visualization');
        console.error('Visualization error:', error);
    }
}

function updateDatatypesSummary(dtypes) {
    const dtypesStats = document.getElementById('dtypes-stats');
    dtypesStats.innerHTML = `
        <div class="dtype-summary">
            <div class="dtype-count">
                <span>Numeric Columns:</span>
                <span>${dtypes.numeric}</span>
            </div>
            <div class="dtype-count">
                <span>Categorical Columns:</span>
                <span>${dtypes.categorical}</span>
            </div>
        </div>
        <div class="dtype-details">
            ${Object.entries(dtypes.details).map(([col, type]) => 
                `<div class="dtype-item">
                    <span>${col}</span>
                    <span>${type}</span>
                </div>`
            ).join('')}
        </div>
    `;
}

function createCorrelationMatrix(correlation) {
    // Get container dimensions
    const container = document.getElementById('correlation-plot');
    const containerWidth = container.offsetWidth;
    
    const data = [{
        type: 'heatmap',
        z: Object.values(correlation).map(row => Object.values(row)),
        x: Object.keys(correlation),
        y: Object.keys(correlation),
        colorscale: [
            [0, '#ffffff'],  // Start with white
            [0.25, '#d9d9d9'],
            [0.5, '#a6a6a6'],
            [0.75, '#737373'],
            [1, '#1e1e1e']  // End with dark gray
        ],
        zmin: -1,
        zmax: 1,
        hoverongaps: false,
        hoverlabel: {
            bgcolor: '#1e1e1e',
            bordercolor: '#1e1e1e',
            font: { 
                family: 'JetBrains Mono',
                size: 12,
                color: 'white' 
            }
        },
        hovertemplate: 
            '<b>%{x}</b> × <b>%{y}</b><br>' +
            'Correlation: %{z:.2f}<extra></extra>'
    }];
    
    const layout = {
        width: containerWidth,
        height: containerWidth,  // Keep it square
        margin: {
            l: 80,  // Increased left margin
            r: 20,
            t: 20,
            b: 60
        },
        xaxis: {
            tickfont: { size: 12, family: 'JetBrains Mono' },
            tickangle: 45
        },
        yaxis: {
            tickfont: { size: 12, family: 'JetBrains Mono' }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    const config = {
        displayModeBar: false,
        responsive: true
    };

    Plotly.newPlot('correlation-plot', data, layout, config);

    // Update on window resize
    window.addEventListener('resize', () => {
        const newWidth = container.offsetWidth;
        Plotly.relayout('correlation-plot', {
            width: newWidth,
            height: newWidth
        });
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