document.addEventListener('DOMContentLoaded', () => {
    // Tab switching logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    // File input UX
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const dropArea = input.closest('.file-drop-area');
        const message = dropArea.querySelector('.file-message');
        const defaultMsg = message.textContent;

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                message.textContent = e.target.files[0].name;
                message.style.color = 'var(--text-main)';
            } else {
                message.textContent = defaultMsg;
                message.style.color = '';
            }
        });

        // drag and drop styles
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropArea.classList.remove('dragover');
            });
        });
        
        dropArea.addEventListener('drop', (e) => {
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                
                // Manually trigger the change event
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        });
    });

    // Encrypt
    const encryptForm = document.getElementById('encrypt-form');
    encryptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('encrypt-btn');
        const btnText = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.loader');
        const resultDiv = document.getElementById('encrypt-result');

        btnText.style.display = 'none';
        loader.style.display = 'block';
        btn.disabled = true;
        resultDiv.textContent = '';
        resultDiv.className = 'result-message';

        try {
            const formData = new FormData(encryptForm);
            const res = await fetch('/encrypt', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error('Encryption request failed.');

            const disposition = res.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                // It's a file blob payload
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                let filename = 'encrypted_stego.png';
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                resultDiv.textContent = '✅ Image encrypted & downloaded successfully!';
                resultDiv.className = 'result-message success-alert';
            } else {
                // Probably an error text returned
                const text = await res.text();
                resultDiv.textContent = text;
                resultDiv.className = 'result-message error-alert';
            }
        } catch (err) {
            resultDiv.textContent = '❌ Error: ' + err.message;
            resultDiv.className = 'result-message error-alert';
        } finally {
            btnText.style.display = 'block';
            loader.style.display = 'none';
            btn.disabled = false;
        }
    });

    // Decrypt
    const decryptForm = document.getElementById('decrypt-form');
    decryptForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('decrypt-btn');
        const btnText = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.loader');
        const resultDiv = document.getElementById('decrypt-result');

        btnText.style.display = 'none';
        loader.style.display = 'block';
        btn.disabled = true;
        resultDiv.style.display = 'none';
        resultDiv.className = 'result-message';

        try {
            const formData = new FormData(decryptForm);
            const res = await fetch('/decrypt', {
                method: 'POST',
                body: formData
            });
            const text = await res.text();

            resultDiv.style.display = 'block';
            if (text.includes('✅')) {
                // Remove the raw checkmark from the backend for styling if desired, but including it is fine.
                resultDiv.textContent = text;
                resultDiv.className = 'result-message success-alert';
            } else {
                resultDiv.textContent = text;
                resultDiv.className = 'result-message error-alert';
            }
        } catch (err) {
            resultDiv.style.display = 'block';
            resultDiv.textContent = '❌ Error: ' + err.message;
            resultDiv.className = 'result-message error-alert';
        } finally {
            btnText.style.display = 'block';
            loader.style.display = 'none';
            btn.disabled = false;
        }
    });

    // Generate Keys
    const genKeysBtn = document.getElementById('generate-keys-btn');
    genKeysBtn.addEventListener('click', async () => {
        const btnText = genKeysBtn.querySelector('.btn-text');
        const loader = genKeysBtn.querySelector('.loader');
        const resultDiv = document.getElementById('keys-result');

        btnText.style.display = 'none';
        loader.style.display = 'block';
        genKeysBtn.disabled = true;
        resultDiv.style.display = 'none';

        try {
            const res = await fetch('/generate_keys');
            if(res.ok) {
                // Keys are ready to download
                resultDiv.style.display = 'block';
            } else {
                alert('Failed to generate keys!');
            }
        } catch (err) {
            alert('Error generating keys: ' + err.message);
        } finally {
            btnText.style.display = 'block';
            loader.style.display = 'none';
            genKeysBtn.disabled = false;
        }
    });
});
