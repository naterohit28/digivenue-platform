const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Target password (must match what index.html accepts)
const PASSWORD = "DigiVenue_Secure_Sales_2026!";

// File mappings: [source, destination]
const MAPPINGS = [
  [
    path.join(__dirname, '..', '..', 'digistories-sales-tool-v2.html'),
    path.join(__dirname, 'sales-tool.html')
  ],
  [
    path.join(__dirname, '..', '..', 'venue-growth-bible-engine.html'),
    path.join(__dirname, 'bible-engine.html')
  ]
];

const WRAPPER_TEMPLATE = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Loading...</title>
  <style>
    body {
      background-color: #FAF7F2;
      color: #1F1D1C;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }
    .spinner {
      border: 3px solid #EBE4D8;
      border-top: 3px solid #D94822;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      animation: spin 1s linear infinite;
      margin-bottom: 16px;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .text {
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #6F6864;
    }
  </style>
</head>
<body>
  <div class="spinner"></div>
  <div class="text">Decrypting Session...</div>

  <script>
    (async function() {
      const ciphertextBase64 = "CIPHERTEXT_HERE";
      const ivBase64 = "IV_HERE";
      const password = sessionStorage.getItem('dv_portal_key');
      
      const currentFile = window.location.pathname.split('/').pop() || 'index.html';
      
      if (!password) {
        window.location.href = "index.html?redirect=" + encodeURIComponent(currentFile);
        return;
      }
      
      try {
        // Hash password to get a 256-bit key
        const encoder = new TextEncoder();
        const passwordData = encoder.encode(password);
        const keyHash = await window.crypto.subtle.digest('SHA-256', passwordData);
        
        // Import raw key
        const key = await window.crypto.subtle.importKey(
          'raw',
          keyHash,
          { name: 'AES-CBC' },
          false,
          ['decrypt']
        );
        
        // Convert IV and ciphertext from base64
        const iv = Uint8Array.from(atob(ivBase64), c => c.charCodeAt(0));
        const ciphertext = Uint8Array.from(atob(ciphertextBase64), c => c.charCodeAt(0));
        
        // Decrypt
        const decryptedBuffer = await window.crypto.subtle.decrypt(
          { name: 'AES-CBC', iv: iv },
          key,
          ciphertext
        );
        
        const decryptedHtml = new TextDecoder().decode(decryptedBuffer);
        
        // Render decrypted page
        document.open();
        document.write(decryptedHtml);
        document.close();
      } catch (e) {
        console.error("Decryption failed:", e);
        sessionStorage.removeItem('dv_portal_key');
        window.location.href = "index.html?redirect=" + encodeURIComponent(currentFile);
      }
    })();
  </script>
</body>
</html>`;

function encryptFile(srcPath, destPath, password) {
  if (!fs.existsSync(srcPath)) {
    console.error(`Source file not found: ${srcPath}`);
    return false;
  }
  
  const plaintext = fs.readFileSync(srcPath, 'utf8');
  
  // Deriving the 256-bit key from password hash
  const key = crypto.createHash('sha256').update(password).digest();
  
  // Generate random 16-byte initialization vector
  const iv = crypto.randomBytes(16);
  
  // Encrypt using AES-256-CBC
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let ciphertext = cipher.update(plaintext, 'utf8', 'base64');
  ciphertext += cipher.final('base64');
  
  const ivBase64 = iv.toString('base64');
  
  // Replace placeholders in wrapper template
  const wrappedHtml = WRAPPER_TEMPLATE
    .replace('CIPHERTEXT_HERE', ciphertext)
    .replace('IV_HERE', ivBase64);
    
  fs.writeFileSync(destPath, wrappedHtml, 'utf8');
  console.log(`Successfully encrypted: ${path.basename(srcPath)} -> ${path.basename(destPath)}`);
  return true;
}

function run() {
  console.log("Starting encryption of tools...");
  let successCount = 0;
  for (const [src, dest] of MAPPINGS) {
    if (encryptFile(src, dest, PASSWORD)) {
      successCount++;
    }
  }
  console.log(`Encryption finished. ${successCount}/${MAPPINGS.length} files processed successfully.`);
}

run();
