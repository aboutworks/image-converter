function checkProgress(filename) {
    const statusElement = document.getElementById('status');
    const filesElement = document.getElementById('files');

    function fetchProgress() {
        fetch(`/progress/${filename}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'Completed') {
                    statusElement.textContent = 'Conversion Completed!';
                    data.files.forEach(file => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = `/download/${file}`;
                        a.textContent = file;
                        li.appendChild(a);
                        filesElement.appendChild(li);
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