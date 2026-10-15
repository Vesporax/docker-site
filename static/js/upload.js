// Mod Upload Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeImagePreview();
});

function initializeImagePreview() {
    const imageInput = document.getElementById('id_images');
    const previewContainer = document.getElementById('image-preview');

    if (!imageInput || !previewContainer) return;

    let selectedFiles = [];

    imageInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);

        if (files.length > 6) {
            alert('Vous ne pouvez téléverser que 6 images maximum. Les 6 premières seront utilisées.');
            selectedFiles = files.slice(0, 6);
        } else {
            selectedFiles = files;
        }

        previewContainer.innerHTML = '';

        selectedFiles.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                createImagePreview(file, index, previewContainer);
            }
        });

        if (files.length > 6) {
            updateFileInput(imageInput, selectedFiles);
        }
    });
}

function createImagePreview(file, index, container) {
    const reader = new FileReader();

    reader.onload = function(e) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'image-preview';

        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = `Aperçu ${index + 1}`;

        const numberLabel = document.createElement('span');
        numberLabel.className = 'image-number';
        numberLabel.textContent = index === 0 ? 'Principale' : `#${index + 1}`;

        previewDiv.appendChild(img);
        previewDiv.appendChild(numberLabel);
        container.appendChild(previewDiv);
    };

    reader.readAsDataURL(file);
}

function updateFileInput(input, files) {
    const dt = new DataTransfer();
    files.forEach(file => dt.items.add(file));
    input.files = dt.files;
}