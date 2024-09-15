// static/js/admin/business_category.js
document.addEventListener('DOMContentLoaded', function () {
    const parentSelect = document.getElementById('id_parent_category');
    const subcategorySelect = document.getElementById('id_subcategories');

    function updateSubcategories() {
        const parentId = parentSelect.value;
        if (parentId) {
            fetch(`/admin/api/subcategories/${parentId}/`)
                .then(response => response.json())
                .then(data => {
                    subcategorySelect.innerHTML = '';
                    data.forEach(subcategory => {
                        const option = document.createElement('option');
                        option.value = subcategory.id;
                        option.textContent = subcategory.name;
                        option.selected = subcategorySelect.querySelector(`option[value="${subcategory.id}"]`);
                        subcategorySelect.appendChild(option);
                    });
                });
        } else {
            subcategorySelect.innerHTML = '';
        }
    }

    parentSelect.addEventListener('change', updateSubcategories);
});
