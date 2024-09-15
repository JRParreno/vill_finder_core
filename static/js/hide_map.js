document.addEventListener("DOMContentLoaded", function () {
    // Get all list items (tabs)
    var tabItems = document.querySelectorAll('li.changeform-tabs-item');

    // Function to show or hide the map based on selected tab
    function toggleMapVisibility(linkText) {
        var mapClass = document.querySelector('.map');

        if (linkText === 'General') {
            // Show the map if the "General" tab is selected
            mapClass.style.display = 'block';
        } else {
            // Hide the map if any other tab is selected
            mapClass.style.display = 'none';
        }
    }

    // Loop through each tab and add a click event listener
    tabItems.forEach(function (item) {
        item.addEventListener('click', function () {
            // Get the text inside the clicked anchor tag
            var linkText = item.querySelector('a').textContent.trim();

            // Call the toggle function to show or hide the map
            toggleMapVisibility(linkText);
        });
    });

    // Initial load check: call the function based on the initially selected tab
    var selectedTab = document.querySelector('li.changeform-tabs-item.selected');
    if (selectedTab) {
        var linkText = selectedTab.querySelector('a').textContent.trim();
        toggleMapVisibility(linkText);
    }
});
