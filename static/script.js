// Selecteer de benodigde elementen
const scanNowLink = document.getElementById('scanNowLink');
const facialContainer = document.getElementById('facialContainer');
const registerFacialBtn = document.getElementById('registerFacialBtn');
const closeFacialBtn = document.getElementById('closeFacialBtn');
const video = document.getElementById('video');
const imageInput = document.getElementById('imageInput');
const facialForm = document.getElementById('facialForm');
const loginFacialBtn = document.getElementById('loginFacialBtn');
const showFaceIDBtn = document.getElementById('showFaceIDBtn');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const showFaceContainer = document.getElementById('showFaceContainer');
const previewVideo = document.getElementById('previewVideo');

// Webcam stream variabele
let webcamStream = null;

// Start webcam voor een specifiek video-element
function startWebcam(videoElement) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            webcamStream = stream;
            videoElement.srcObject = stream;
            if (facialContainer) facialContainer.classList.remove('hidden'); // Toon registratiecontainer indien aanwezig
            if (showFaceContainer) showFaceContainer.classList.remove('hidden'); // Toon login-container indien aanwezig
        })
        .catch(error => {
            console.error("Kan de webcam niet openen:", error);
            alert("Kan geen toegang krijgen tot de camera. Controleer je instellingen.");
        });
}

// Stop webcam en verberg container
function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    if (facialContainer) facialContainer.classList.add('hidden');
    if (showFaceContainer) showFaceContainer.classList.add('hidden');
}

// Gezicht vastleggen en verzenden (voor registratie)
function captureFacial() {
    if (!video) {
        alert("Geen video beschikbaar voor registratie.");
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');
    imageInput.value = imageData;
    facialForm.submit();
    stopWebcam(); // Stop webcam na registratie
}

// Login met Face ID
function loginWithFaceID() {
    alert("Logging in with Face ID now...");
    const canvas = document.createElement('canvas');
    const hiddenVideo = document.createElement('video'); // Verborgen video-element voor Face ID-scanning

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            hiddenVideo.srcObject = stream;
            hiddenVideo.play();

            setTimeout(() => {
                // Maak een afbeelding van het gezicht
                canvas.width = hiddenVideo.videoWidth;
                canvas.height = hiddenVideo.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(hiddenVideo, 0, 0, canvas.width, canvas.height);

                // Zet de afbeelding om naar base64
                const imageData = canvas.toDataURL('image/png');

                // Verstuur de afbeelding naar de server
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/login_facial';
                const imageInput = document.createElement('input');
                imageInput.type = 'hidden';
                imageInput.name = 'image';
                imageInput.value = imageData;
                form.appendChild(imageInput);
                document.body.appendChild(form);
                form.submit();

                // Stop de webcam na login
                stream.getTracks().forEach(track => track.stop());
            }, 3000); // Wacht 3 seconden voor het vastleggen
        })
        .catch(error => {
            console.error("Kan de webcam niet openen:", error);
            alert("Kan geen toegang krijgen tot de camera. Controleer je instellingen.");
        });
}

// Eventlisteners

// Start webcam en toon registratiecontainer bij "Scan Now"
if (scanNowLink) {
    scanNowLink.addEventListener('click', (e) => {
        e.preventDefault();
        startWebcam(video);
    });
}

// Gezicht vastleggen bij "Scan Facial ID"
if (registerFacialBtn) {
    registerFacialBtn.addEventListener('click', captureFacial);
}

// Sluit webcam preview bij "Close" in de registratiecontainer
if (closeFacialBtn) {
    closeFacialBtn.addEventListener('click', stopWebcam);
}

// Start webcam voor het loginproces
if (showFaceIDBtn) {
    showFaceIDBtn.addEventListener('click', () => startWebcam(previewVideo));
}

// Sluit de webcam preview-container bij "Close" in het loginproces
if (closePreviewBtn) {
    closePreviewBtn.addEventListener('click', stopWebcam);
}

// Login met Face ID
if (loginFacialBtn) {
    loginFacialBtn.addEventListener('click', loginWithFaceID);
}
