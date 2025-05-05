
document.getElementById('file').addEventListener('change', function(e) {
    var files = e.target.files;
    var preview = document.getElementById('image-preview');
    preview.innerHTML = '';

    if (files.length > 0) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            var fileInfo = document.createElement('div');
            fileInfo.textContent = 'Selected file: ' + file.name;
            preview.appendChild(fileInfo);

            if (file.type.startsWith('image/') && file.type !== 'image/svg+xml') {
                // 普通图片 (png/jpg/webp)
                var reader = new FileReader();
                reader.onload = function(event) {
                    var img = document.createElement('img');
                    img.src = event.target.result;
                    img.style.maxWidth = '200px';
                    img.style.margin = '10px';
                    preview.appendChild(img);
                }
                reader.readAsDataURL(file);

            } else if (file.type === 'application/pdf') {
                // PDF文件预览
                var fileURL = URL.createObjectURL(file);
                var iframe = document.createElement('iframe');
                iframe.src = fileURL;
                iframe.width = "100%";
                iframe.height = "500px";
                iframe.style.margin = '10px 0';
                preview.appendChild(iframe);

            } else if (file.type === 'image/svg+xml') {
                // SVG 文件预览
                var reader = new FileReader();
                reader.onload = function(event) {
                    var object = document.createElement('object');
                    object.data = event.target.result;
                    object.type = 'image/svg+xml';
                    object.width = '200';
                    object.height = '200';
                    object.style.margin = '10px';
                    preview.appendChild(object);
                }
                reader.readAsDataURL(file);
            }
        }
    } else {
        preview.textContent = 'No file selected';
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Route for the upload section
    page('/', uploadSection);
    page('/upload', uploadSection);
    page();

    function uploadSection() {
        var uploadSection = document.getElementById('upload-container');
        uploadSection.style.display = 'flex';

        document.getElementById('toggle-upload').addEventListener('click', function() {
            if (uploadSection.style.display === 'none') {
                uploadSection.style.display = 'flex';
            } else {
                uploadSection.style.display = 'none';
            }
        });

        // Handle form submission
        var form = document.querySelector('form');
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            var formData = new FormData(form);

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                // Update the content container with the server response
                var appContainer = document.getElementById('app');
                appContainer.innerHTML = '<p>' + data.message + '</p>';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
