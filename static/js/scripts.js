function checkProgress(filename) {
    const statusElement = document.getElementById('status');
    const filesElement = document.getElementById('files');

    function fetchProgress() {
        fetch(`/progress/${filename}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'Completed') {
                    statusElement.textContent = 'Conversion Completed!';

                    function createImage(file) {
                        const li = document.createElement('li');
                        const img = document.createElement('img');
                        img.src = `/download/${file}`;
                        img.alt = file;
                        img.style.width = '200px';
                        img.style.height = '200px';
                        img.style.objectFit = 'contain';
                        img.style.border = '1px solid #00ff77';
                        img.style.borderRadius = '5px';

                        img.onload = () => {
                            console.log('Image loaded successfully:', file);
                        };

                        img.onerror = () => {
                            console.error('Error loading image:', file);
                            img.src = ''; // Set a placeholder or error image
                            img.alt = 'Failed to load image';
                            img.style.backgroundColor = 'red';
                        };

                        li.appendChild(img);
                        filesElement.appendChild(li);
                    }

                    data.files.forEach(file => {
                        createImage(file);
                    });

                } else {
                    statusElement.textContent = 'Conversion in Progress...';
                    setTimeout(fetchProgress, 2000); // Retry after 2 seconds
                }
            })
            .catch(error => {
                console.error('Error checking progress:', error);
                statusElement.textContent = 'An error occurred. Please try again.';
            });
    }

    fetchProgress();
}

document.getElementById('file').addEventListener('change', function(e) {
    var file = e.target.files[0];
    if (file) {
        document.getElementById('pdf-preview').textContent = 'Selected file: ' + file.name;
    } else {
        document.getElementById('pdf-preview').textContent = 'No PDF selected';
    }
});

document.getElementById('toggle-upload').addEventListener('click', function() {
    console.log("click")
    var uploadSection = document.getElementById('upload-container');
    if (uploadSection.style.display === 'none') {
        uploadSection.style.display = 'flex';
    } else {
        uploadSection.style.display = 'none';
    }
});
