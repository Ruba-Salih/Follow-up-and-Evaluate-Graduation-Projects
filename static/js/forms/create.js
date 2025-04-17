document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("evaluation-form").onsubmit = function (e) {
        e.preventDefault();

        let formData = {
            name: document.getElementById("form-name").value,
            target_role: document.getElementById("target_role").value,
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

        fetch(createFormUrl, { // Use global variable from create.html
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message || "Form created successfully!");
            window.location.href = formListUrl; // Redirect using the global variable
        })
        .catch(error => {
            console.error("Error:", error);
            showAlert("Failed to create form.");
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
                <button type="button" class="delete-main-btn" onclick="deleteMainCategory(this)">❌<br><span>Remove Main</span></button>
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
        <div class="input-group">
            <input type="text" name="sub_category_text" required>
            <button type="button" class="delete-btn" onclick="deleteSubCategory(this)">❌<br><span>Remove</span></button>
        </div>
    `;
    container.appendChild(div);
}

function deleteMainCategory(button) {
    button.closest(".main-category").remove();
}

function deleteSubCategory(button) {
    button.closest(".subcategory").remove();
}
