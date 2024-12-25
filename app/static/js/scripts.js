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

    if (tabName === 'model') {
        initializeModeling();
    }
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
            window.currentData = data;
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

function handleCategoryChange(event) {
    if (!window.currentCategoricalSummary) return;
    
    const categoricalStats = document.getElementById('categorical-stats');
    categoricalStats.innerHTML = createCategoricalTable(
        window.currentCategoricalSummary, 
        event.target.value
    );
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

function handleUploadSuccess(responseData) {
    console.log('=== Upload Success Debug ===');
    console.log('Response data:', responseData);
    
    if (!responseData) return;
    
    window.hasData = true;  // Set this explicitly
    window.currentData = {
        ...responseData,
        numeric_summary: null  // Will be populated later
    };
    
    console.log('Window state after upload:', {
        hasData: window.hasData,
        currentData: window.currentData
    });
    
    updateDataInfo(responseData);
    populateColumnSelectors(responseData.columns);
    enableTabs();

    // Get profile data for modeling
    fetch('/data/profile')
        .then(response => response.json())
        .then(profileData => {
            console.log('Profile data received:', profileData);
            if (!profileData.error) {
                window.currentData.numeric_summary = profileData.numeric_summary;
                console.log('Numeric summary updated:', window.currentData.numeric_summary);
                initializeModeling();
            }
        });
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







// Modeling Functions

function showModelError(message) {
    const errorDiv = document.getElementById('model-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
    console.error('Model error:', message);
}

function populateModelSelectors(data) {
    console.log('PopulateModelSelectors called with:', data);
    
    const targetSelect = document.getElementById('target-column');
    const featureSelect = document.getElementById('feature-columns');
    
    if (!targetSelect || !featureSelect) {
        console.error('Select elements not found');
        return;
    }
    
    // Clear existing options
    targetSelect.innerHTML = '';
    featureSelect.innerHTML = '';
    
    // Add default option to target
    targetSelect.add(new Option('Select target column...', ''));
    
    // Get numeric columns from numeric_summary
    const numericColumns = data.numeric_summary ? Object.keys(data.numeric_summary) : [];
    console.log('Found numeric columns:', numericColumns);
    
    if (numericColumns.length === 0) {
        console.warn('No numeric columns found in data');
        return;
    }
    
    // Populate options
    numericColumns.forEach(col => {
        targetSelect.add(new Option(col, col));
        featureSelect.add(new Option(col, col));
    });
    
    // Configure feature select
    featureSelect.multiple = true;
    featureSelect.size = 5;
}


async function initializeModeling() {
    try {
        console.log('Starting modeling initialization...');
        console.log('Current data:', window.currentData);
        
        if (window.currentData && window.currentData.numeric_summary) {
            console.log('Using cached data');
            populateModelSelectors(window.currentData);
            return;
        }
        
        // Fetch new data if needed
        const profileResponse = await fetch('/data/profile');
        const profileData = await profileResponse.json();
        
        if (profileData.error) {
            showModelError(profileData.error);
            return;
        }
        
        if (!window.currentData) window.currentData = {};
        window.currentData.numeric_summary = profileData.numeric_summary;
        populateModelSelectors(window.currentData);
        
    } catch (error) {
        console.error('Modeling initialization error:', error);
        showModelError('Error initializing modeling form');
    }
}

// Update event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize global state
    window.hasData = false;
    window.currentData = null;
    
    // Set up all event listeners
    const modelTab = document.querySelector('button[onclick="openTab(event, \'model\')"]');
    const trainBtn = document.querySelector('.train-btn');
    const categorySelect = document.getElementById('category-select');
    
    if (modelTab) {
        modelTab.addEventListener('click', () => {
            console.log('Model tab clicked');
            if (window.hasData) {
                initializeModeling();
            }
        });
    }
    
    if (trainBtn) {
        trainBtn.addEventListener('click', trainModel);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', handleCategoryChange);
    }
});

async function trainModel() {
    try {
        console.log('=== Training Model Debug ===');
        console.log('Current state:', {
            hasData: window.hasData,
            currentData: window.currentData,
            numeric_summary: window.currentData?.numeric_summary
        });

        if (!window.currentData?.numeric_summary) {
            showModelError('No data available. Please upload data first.');
            return;
        }

        const formData = {
            testSize: document.getElementById('test-size').value,
            targetColumn: document.getElementById('target-column').value,
            featureColumns: Array.from(document.getElementById('feature-columns').selectedOptions)
                .map(opt => opt.value)
        };
        
        console.log('Form data:', formData);

        const modelData = {
            test_size: parseFloat(formData.testSize),
            target_column: formData.targetColumn,
            feature_columns: formData.featureColumns
        };

        console.log('Sending model request:', modelData);

        const response = await fetch('/modeling', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(modelData)
        });

        const results = await response.json();
        console.log('Model response:', results);

        if (!response.ok) {
            throw new Error(results.error || 'Server error');
        }

        displayModelResults(results);

    } catch (error) {
        console.error('Training error:', error);
        showModelError(error.message);
    }
}

function displayModelResults(results) {
    const resultsDiv = document.getElementById('model-results');
    if (!resultsDiv) return;
    
    resultsDiv.classList.remove('hidden');

    // Update metrics
    document.getElementById('r2-score').textContent = results.r2_score.toFixed(4);
    document.getElementById('rmse').textContent = results.rmse.toFixed(4);
    document.getElementById('train-samples').textContent = results.samples.train;
    document.getElementById('test-samples').textContent = results.samples.test;

    // Update feature importance table
    const tbody = document.getElementById('importance-table').getElementsByTagName('tbody')[0];
    if (tbody) {
        tbody.innerHTML = Object.entries(results.feature_importance)
            .map(([feature, importance]) => `
                <tr>
                    <td>${feature}</td>
                    <td>${importance.toFixed(4)}</td>
                </tr>
            `).join('');
    }
}