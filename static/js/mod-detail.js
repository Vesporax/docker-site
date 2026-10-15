// Mod Detail Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeCarousel();
});

function initializeCarousel() {
    const mainImage = document.getElementById('carousel-main-image');
    const thumbnails = document.querySelectorAll('.carousel-thumbnail');
    const prevBtn = document.querySelector('.carousel-nav.prev');
    const nextBtn = document.querySelector('.carousel-nav.next');
    
    if (!mainImage || thumbnails.length === 0) return;
    
    let currentIndex = 0;
    const images = Array.from(thumbnails).map(thumb => 
        thumb.querySelector('img').src
    );
    
    // Thumbnail click handler
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', function() {
            setActiveImage(index);
        });
    });
    
    // Navigation buttons
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            setActiveImage(currentIndex);
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            currentIndex = (currentIndex + 1) % images.length;
            setActiveImage(currentIndex);
        });
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft' && prevBtn) {
            prevBtn.click();
        } else if (e.key === 'ArrowRight' && nextBtn) {
            nextBtn.click();
        }
    });
    
    function setActiveImage(index) {
        currentIndex = index;
        mainImage.src = images[index];
        
        // Update active thumbnail
        thumbnails.forEach((thumb, i) => {
            if (i === index) {
                thumb.classList.add('active');
            } else {
                thumb.classList.remove('active');
            }
        });
    }
    
    // Set first image as active
    if (thumbnails.length > 0) {
        thumbnails[0].classList.add('active');
    }
}