// Global state
let currentPhotos = [];
let selectedPhoto = null;

// Load photos when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadPhotos();
});

// Function to load photos from the API
async function loadPhotos() {
    showLoading();
    try {
        const response = await fetch('/api/photos');
        const data = await response.json();
        
        if (data.success) {
            currentPhotos = data.photos;
            renderPhotoGrid();
        } else {
            showError(data.error || 'Failed to load photos');
        }
    } catch (error) {
        showError('Failed to load photos: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Function to render the photo grid
function renderPhotoGrid() {
    const grid = document.getElementById('photoGrid');
    grid.innerHTML = '';

    currentPhotos.forEach(photo => {
        const photoCard = createPhotoCard(photo);
        grid.appendChild(photoCard);
    });
}

// Function to create a photo card
function createPhotoCard(photo) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300';
    
    const date = new Date(photo.creationTime);
    const formattedDate = date.toLocaleDateString();
    
    card.innerHTML = `
        <div class="relative aspect-w-16 aspect-h-9">
            <img src="${photo.baseUrl}" 
                 alt="${photo.filename}"
                 class="w-full h-48 object-cover cursor-pointer"
                 onclick="openPhotoModal('${photo.id}')">
            ${photo.isFavorite ? '<span class="absolute top-2 right-2 bg-yellow-400 text-white px-2 py-1 rounded-full text-sm">Favorite</span>' : ''}
        </div>
        <div class="p-4">
            <h3 class="text-sm font-medium text-gray-900 truncate">${photo.filename}</h3>
            <p class="text-sm text-gray-500">${formattedDate}</p>
        </div>
    `;
    
    return card;
}

// Function to open the photo modal
async function openPhotoModal(photoId) {
    selectedPhoto = currentPhotos.find(p => p.id === photoId);
    if (!selectedPhoto) return;

    const modal = document.getElementById('photoModal');
    const modalImage = document.getElementById('modalImage');
    const favoriteBadge = document.getElementById('favoriteBadge');
    const captionInput = document.getElementById('captionInput');

    modalImage.src = selectedPhoto.baseUrl;
    favoriteBadge.style.display = selectedPhoto.isFavorite ? 'block' : 'none';
    captionInput.value = ''; // Clear previous caption

    modal.classList.remove('hidden');
}

// Function to close the photo modal
function closeModal() {
    const modal = document.getElementById('photoModal');
    modal.classList.add('hidden');
    selectedPhoto = null;
}

// Function to approve and post the photo
async function approvePost() {
    if (!selectedPhoto) return;

    const captionInput = document.getElementById('captionInput');
    const caption = captionInput.value.trim();

    // TODO: Implement the actual posting logic
    console.log('Posting photo:', {
        photoId: selectedPhoto.id,
        caption: caption
    });

    // For now, just close the modal
    closeModal();
}

// Utility functions for loading and error states
function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showError(message) {
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorState.classList.remove('hidden');
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorState.classList.add('hidden');
    }, 5000);
} 