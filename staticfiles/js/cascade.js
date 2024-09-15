// static/admin/js/cascade.js

document.addEventListener('DOMContentLoaded', function () {
    const parentSelect = document.getElementById('id_parent_category');
    const subcategorySelect = document.getElementById('id_subcategory');

    if (parentSelect && subcategorySelect) {
        parentSelect.addEventListener('change', function () {
            console.log('Parent category changed:', parentSelect.value);
            const parentCategoryId = parentSelect.value;

            fetch(`/admin/api/subcategories/?parent_category=${parentCategoryId}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Subcategories:', data.subcategories);
                    subcategorySelect.innerHTML = '<option value="">---------</option>';
                    data.subcategories.forEach(subcategory => {
                        const option = document.createElement('option');
                        option.value = subcategory.id;
                        option.textContent = subcategory.name;
                        subcategorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching subcategories:', error));
        });
    }
});
