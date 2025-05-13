// Main JavaScript for the Droid AI Agent web interface

document.addEventListener('DOMContentLoaded', function() {
    // Content type selection
    const contentType = document.getElementById('content-type');
    const textOptions = document.getElementById('text-options');
    const imageOptions = document.getElementById('image-options');
    const memeOptions = document.getElementById('meme-options');
    
    contentType.addEventListener('change', function() {
        // Hide all options
        textOptions.style.display = 'none';
        imageOptions.style.display = 'none';
        memeOptions.style.display = 'none';
        
        // Show selected options
        if (this.value === 'text') {
            textOptions.style.display = 'block';
        } else if (this.value === 'image') {
            imageOptions.style.display = 'block';
        } else if (this.value === 'meme') {
            memeOptions.style.display = 'block';
        }
    });
    
    // Temperature slider
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    
    temperatureSlider.addEventListener('input', function() {
        temperatureValue.textContent = this.value;
    });
    
    // Interaction type selection
    const interactionType = document.getElementById('interaction-type');
    const messageContainer = document.getElementById('message-container');
    
    interactionType.addEventListener('change', function() {
        if (this.value === 'comment' || this.value === 'message') {
            messageContainer.style.display = 'block';
        } else {
            messageContainer.style.display = 'none';
        }
    });
    
    // Generate content form
    const generateForm = document.getElementById('generate-form');
    const generationResult = document.getElementById('generation-result');
    const textResult = document.getElementById('text-result');
    const imageResult = document.getElementById('image-result');
    
    generateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const type = contentType.value;
        const prompt = document.getElementById('prompt').value;
        
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }
        
        // Prepare request data
        let data = {
            content_type: type,
            prompt: prompt
        };
        
        // Add type-specific parameters
        if (type === 'text') {
            data.max_tokens = parseInt(document.getElementById('max-tokens').value);
            data.temperature = parseFloat(document.getElementById('temperature').value);
        } else if (type === 'image') {
            data.width = parseInt(document.getElementById('width').value);
            data.height = parseInt(document.getElementById('height').value);
            data.negative_prompt = document.getElementById('negative-prompt').value;
        } else if (type === 'meme') {
            data.topic = prompt;
            data.style = document.getElementById('style').value;
            data.template = document.getElementById('template').value;
        }
        
        // Show loading state
        generationResult.style.display = 'block';
        textResult.innerHTML = '<div class="text-center"><div class="spinner"></div><p>Generating content...</p></div>';
        imageResult.innerHTML = '';
        
        // Send request
        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            // Display result
            if (result.success) {
                if (type === 'text') {
                    textResult.textContent = result.text;
                    imageResult.innerHTML = '';
                } else if (type === 'image' || type === 'meme') {
                    textResult.textContent = '';
                    imageResult.innerHTML = `<img src="/generated/${result.filepath.split('/').pop()}" alt="Generated ${type}">`;
                    
                    if (type === 'meme' && result.caption) {
                        textResult.textContent = `Caption: ${result.caption}`;
                    }
                }
            } else {
                textResult.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
                imageResult.innerHTML = '';
            }
        })
        .catch(error => {
            textResult.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            imageResult.innerHTML = '';
        });
    });
    
    // Post content form
    const postForm = document.getElementById('post-form');
    const postResult = document.getElementById('post-result');
    const postResultContent = document.getElementById('post-result-content');
    
    postForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const platform = document.getElementById('platform').value;
        const content = document.getElementById('content').value;
        const media = document.getElementById('media').value;
        
        if (!content) {
            alert('Please enter content to post');
            return;
        }
        
        // Prepare request data
        let data = {
            platform: platform,
            content: content
        };
        
        // Add media if provided
        if (media) {
            data.media_urls = media.split(',').map(url => url.trim());
        }
        
        // Show loading state
        postResult.style.display = 'block';
        postResultContent.innerHTML = '<div class="text-center"><div class="spinner"></div><p>Posting content...</p></div>';
        
        // Send request
        fetch('/api/post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            // Display result
            if (result.success) {
                postResultContent.innerHTML = `
                    <div class="alert alert-success">
                        <h5>Posted successfully!</h5>
                        <p>Platform: ${platform}</p>
                        <p>Post ID: ${result.post_id || 'N/A'}</p>
                    </div>
                `;
            } else {
                postResultContent.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
            }
        })
        .catch(error => {
            postResultContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
    
    // Interact with influencer form
    const interactForm = document.getElementById('interact-form');
    const interactResult = document.getElementById('interact-result');
    const interactResultContent = document.getElementById('interact-result-content');
    
    interactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const platform = document.getElementById('interact-platform').value;
        const influencerId = document.getElementById('influencer-id').value;
        const type = document.getElementById('interaction-type').value;
        const message = document.getElementById('message').value;
        
        if (!influencerId) {
            alert('Please enter an influencer ID');
            return;
        }
        
        if ((type === 'comment' || type === 'message') && !message) {
            alert('Please enter a message');
            return;
        }
        
        // Prepare request data
        let data = {
            platform: platform,
            influencer_id: influencerId,
            interaction_type: type
        };
        
        // Add message if provided
        if (message) {
            data.message = message;
        }
        
        // Show loading state
        interactResult.style.display = 'block';
        interactResultContent.innerHTML = '<div class="text-center"><div class="spinner"></div><p>Processing interaction...</p></div>';
        
        // Send request
        fetch('/api/interact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            // Display result
            if (result.success) {
                interactResultContent.innerHTML = `
                    <div class="alert alert-success">
                        <h5>Interaction successful!</h5>
                        <p>Platform: ${platform}</p>
                        <p>Influencer: ${influencerId}</p>
                        <p>Type: ${type}</p>
                    </div>
                `;
            } else {
                interactResultContent.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
            }
        })
        .catch(error => {
            interactResultContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
});