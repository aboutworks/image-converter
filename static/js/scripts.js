document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const imagePreviewArea = document.getElementById('imagePreview');
    const convertButtons = document.querySelectorAll('.button-container button');
    const fileLabel = document.querySelector('.file-label');

    fileInput.addEventListener('change', function () {
        imagePreviewArea.innerHTML = ''; // Clear previous previews
        const files = fileInput.files;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();

                reader.onload = function (e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '100px';
                    img.style.margin = '5px';
                    imagePreviewArea.appendChild(img);
                }

                reader.readAsDataURL(file);
            }
        }
    });

    // convertButtons.forEach(button => {
    //     button.addEventListener('click', function () {
    //         const format = this.dataset.format;
    //         const files = fileInput.files;

    //         // Implement conversion logic here
    //         console.log(`Converting ${files.length} files to ${format}`);
    //     });
    // });

    // // Route for the upload section
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
        // var form = document.querySelector('form');
        // form.addEventListener('submit', function(event) {
        //     event.preventDefault();

        //     var formData = new FormData(form);

        //     fetch('/upload', {
        //         method: 'POST',
        //         body: formData,
        //     })
        //     .then(response => response.json())
        //     .then(data => {
        //         // Update the content container with the server response
        //         var appContainer = document.getElementById('app');
        //         appContainer.innerHTML = '<p>' + data.message + '</p>';
        //     })
        //     .catch(error => {
        //         console.error('Error:', error);
        //     });
        // });
    }
});

// 拖拽上传
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");

// 点击触发
dropZone.addEventListener("click", () => {
  fileInput.click();
});

// 拖拽效果
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#333";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "#ccc";
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#ccc";

  const files = e.dataTransfer.files;
  fileInput.files = files;

  // 可选：你可以在此触发上传或预览
  console.log("Dropped files:", files);
});

document.querySelectorAll('.full-button').forEach(button => {
    button.addEventListener('click', () => {
        const format = button.dataset.format;
        const files = document.getElementById('fileInput').files;

        if (!files.length) {
            alert("请先选择文件！");
            return;
        }

        Array.from(files).forEach(file => {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("convert_type", format);

            fetch("/convert", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("转换失败：" + data.error);
                } else {
                    const link = document.createElement('a');
                    link.href = data.download_url;
                    link.download = data.output_file;
                    link.textContent = "下载: " + data.output_file;
                    document.getElementById("image-list").appendChild(link);
                }
            })
            .catch(err => {
                alert("请求失败：" + err);
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // 点击按钮切换主题
    themeToggle.addEventListener('click', () => {
      const currentTheme = body.getAttribute('theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      body.setAttribute('theme', newTheme);

      // 可选：保存到 localStorage，页面刷新后保持上次主题
      localStorage.setItem('theme', newTheme);
    });

    // 页面加载时自动应用上次保存的主题（如果有）
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      body.setAttribute('theme', savedTheme);
    }
  });