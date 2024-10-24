function openTab(tabName) {
    var i, tabContent;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
}


// Fetch data info once the page loads
window.onload = function() {
    fetch('/data-info')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('data-info-container').innerHTML = '<p>No data loaded yet.</p>';
        } else {
            document.getElementById('data-info-container').innerHTML = `
                <p>Rows: ${data.rows}</p>
                <p>Columns: ${data.columns}</p>
                <p>Column Names: ${data.column_names.join(', ')}</p>
            `;
        }
    })
    .catch(error => {
        console.error('Error fetching data info:', error);
    });
}