// Function to handle tab navigation
function openTab(evt, tabName) {
    // Get all elements with class="tab-content" and hide them
    var tabContent = document.getElementsByClassName("tab-content");
    for (var i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }

    // Get all elements with class="tab-button" and remove the class "active"
    var tabButtons = document.getElementsByClassName("tab-button");
    for (var i = 0; i < tabButtons.length; i++) {
        tabButtons[i].className = tabButtons[i].className.replace(" active", "");
    }

    // Show the current tab and add "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// By default, open the Data Import tab
document.getElementById("defaultTab").click();

// Handle file upload
document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent form submission

    // Get the file from the input
    var fileInput = document.getElementById('file-upload');
    var file = fileInput.files[0];

    if (file) {
        var formData = new FormData();
        formData.append('file', file);

        // Send the file to the Flask backend
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById('upload-status').innerHTML = `<p>${data.message}</p>`;
                
                // Load data info after upload
                loadDataInfo();
                
                // Load the head of the DataFrame
                document.getElementById('data-head-container').innerHTML = data.head_data; // Show the head of the DataFrame
            } else {
                document.getElementById('upload-status').innerHTML = `<p class="error">${data.error}</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('upload-status').innerHTML = '<p class="error">An error occurred during file upload.</p>';
        });
    } else {
        document.getElementById('upload-status').innerHTML = '<p class="error">Please select a file to upload.</p>';
    }
});

// Function to load data info
function loadDataInfo() {
    fetch('/data-info')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('data-info-container').innerHTML = `<p class="error">${data.error}</p>`;
        } else {
            var infoHtml = `
                <p><strong>Rows:</strong> ${data.rows}</p>
                <p><strong>Columns:</strong> ${data.columns}</p>
                <p><strong>Column Names:</strong> ${data.column_names.join(', ')}</p>
            `;
            document.getElementById('data-info-container').innerHTML = infoHtml;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('data-info-container').innerHTML = '<p class="error">An error occurred while loading data info.</p>';
    });
}

// Handle loading data profiling info with data type selection
document.getElementById('load-profile-btn').addEventListener('click', function () {
    // Get the selected data type (original or cleaned)
    var dataType = document.getElementById('data-select').value;

    // Fetch the profile data based on the selected data type
    fetch(`/profile?data_type=${dataType}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('profiling-container').innerHTML = `<p class="error">${data.error}</p>`;
        } else {
            var profilingHtml = `
                <h3>Basic Statistics:</h3>
                ${data.describe}
                <h3>Data Info:</h3>
                <pre>${data.info}</pre>
                <h3>Missing Values:</h3>
                <ul>
                    ${Object.keys(data.missing).map(key => `<li>${key}: ${data.missing[key]}</li>`).join('')}
                </ul>
            `;
            document.getElementById('profiling-container').innerHTML = profilingHtml;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('profiling-container').innerHTML = '<p class="error">An error occurred while loading data profiling.</p>';
    });
});

// Handle data cleaning form submission
document.getElementById('clean-data-btn').addEventListener('click', function () {
    // Get the selected cleaning operations (e.g., drop nulls, remove duplicates)
    var dropNulls = document.getElementById('drop-nulls').checked;
    var dropDuplicates = document.getElementById('drop-duplicates').checked;
    var columnsToDrop = document.getElementById('columns-to-drop').value;

    var cleaningOptions = {
        drop_nulls: dropNulls,
        drop_duplicates: dropDuplicates,
        columns_to_drop: columnsToDrop.split(',').map(col => col.trim())
    };

    // Send cleaning options to the backend
    fetch('/clean-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleaningOptions),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('cleaning-status').innerHTML = `<p>${data.message}</p>`;
            // Update the profiling dropdown menu with the new "Cleaned Data" option
            var select = document.getElementById('data-select');
            if (!select.querySelector('option[value="cleaned"]')) {
                var option = document.createElement('option');
                option.value = 'cleaned';
                option.text = 'Cleaned Data';
                select.add(option);
            }
        } else {
            document.getElementById('cleaning-status').innerHTML = `<p class="error">${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('cleaning-status').innerHTML = '<p class="error">An error occurred during cleaning.</p>';
    });
});