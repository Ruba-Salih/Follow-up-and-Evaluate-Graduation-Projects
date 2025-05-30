document.addEventListener("DOMContentLoaded", function () {
    console.log("Edit form script loaded ✅");
    document.getElementById("edit-evaluation-form").onsubmit = function (e) {
        e.preventDefault();

        let formData = {
            name: document.getElementById("form-name").value,
            target_role: document.getElementById("target_role").value,
            form_weight: document.getElementById("form_weight").value,
            main_categories: []
        };

        document.querySelectorAll(".main-category").forEach((category, index) => {
            let mainCategory = {
                number: index + 1,
                text: category.querySelector("[name='main_category_text']").value,
                weight: parseFloat(category.querySelector("[name='main_category_weight']").value),
                grade_type: category.querySelector("[name='main_category_grade_type']").value,
                sub_categories: []
            };

            category.querySelectorAll(".subcategory input").forEach(sub => {
                mainCategory.sub_categories.push({ text: sub.value });
            });

            formData.main_categories.push(mainCategory);
        });

        console.log(JSON.stringify(formData, null, 2));

        fetch(editFormUrl, { // Use global variable from edit.html
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message || "Form updated successfully!");
            window.location.href = formListUrl; // Redirect using the global variable
        })
        .catch(error => {
            console.error("Error:", error);
            showAlert("Failed to update form.");
        });
    };
});

function addMainCategory() {
    const container = document.getElementById("main-categories");
    const count = container.getElementsByClassName("main-category").length + 1;

    let div = document.createElement("div");
    div.classList.add("main-category");
    div.innerHTML = `
        <div class="category-block">
            <div class="category-header">
                <h4>Main Category ${count}</h4>
                <button type="button" class="delete-main-btn" onclick="deleteMainCategory(this)">❌<br><span>Remove</span></button>
            </div>

            <div class="input-row">
                <div class="input-group">
                    <label>Text:</label> 
                    <input type="text" name="main_category_text" required>
                </div>
            </div>

            <div class="input-row">
                <div class="input-group">
                    <label>Weight:</label> 
                    <input type="number" name="main_category_weight" step="0.01" required>
                </div>
                <div class="input-group">
                    <label>Grade Type:</label>
                    <select name="main_category_grade_type">
                        <option value="individual">Individual</option>
                        <option value="group">Group</option>
                    </select>
                </div>
            </div>

            <div class="sub-categories">
                <h5>Subcategories</h5>
                <div class="subcategories-container"></div>
                <button type="button" class="add-subcategory" onclick="addSubCategory(this)">+ Add Subcategory</button>
            </div>
        </div>
    `;
    container.appendChild(div);
}

function addSubCategory(button) {
    const container = button.previousElementSibling;
    let div = document.createElement("div");
    div.classList.add("subcategory");
    div.innerHTML = `
        <input type="text" name="sub_category_text" required>
        <button type="button" class="delete-btn" onclick="deleteSubCategory(this)">❌<br><span>Remove</span></button>
    `;
    container.appendChild(div);
}

function deleteMainCategory(button) {
    if (confirmAction("Are you sure you want to delete this category?")) {
        button.closest(".main-category").remove();
    }
}

function deleteSubCategory(button) {
    if (confirmAction("Are you sure you want to delete this subcategory?")) {
        button.closest(".subcategory").remove();
    }
}

function cancelEdit() {
    if (confirmAction("Discard changes and go back?")) {
        window.history.back();
    }
}
