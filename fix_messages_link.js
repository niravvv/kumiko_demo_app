// This script will fix the Messages tab link issue
document.addEventListener('DOMContentLoaded', function() {
    // Get all tab items
    const tabItems = document.querySelectorAll('.mobile-tabs .tab-item');
    
    // Add click event listener to the Messages tab
    tabItems.forEach(tab => {
        if (tab.querySelector('span').textContent.trim() === 'Messages') {
            console.log('Found Messages tab, adding event listener');
            
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Messages tab clicked');
                
                // Navigate directly to the messages URL
                window.location.href = '/messages';
            });
        }
    });
    
    console.log('Tab fix script loaded');
});
