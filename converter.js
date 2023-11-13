// Get references to HTML elements
const urlForm = document.getElementById('urlForm');          // Get the form element
const originalURL = document.getElementById('originalURL');  // Get the input field for the original URL
const shortenedURL = document.getElementById('shortenedURL');// Get the div for displaying the shortened URL

// Add a form submit event listener
urlForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent the form from submitting
    const longURL = originalURL.value; // Get the value of the input field
    try {
        // Replace this with a call to a URL shortening service like TinyURL or Bitly
        const shortURL = await shortenURL(longURL);
        if (shortURL) {
             // Display the shortened URL as a link
            shortenedURL.innerHTML = `Shortened URL: <a href="${shortURL}" target="_blank">${shortURL}</a>`;
        } else {
            // Display an error message if the shortening process fails
            shortenedURL.innerHTML = 'An error occurred while shortening the URL.';
        }
    } catch (error) {
        console.error(error); // Log any errors to the console
        shortenedURL.innerHTML = 'An error occurred while shortening the URL.';
    }
});


// Function to shorten a URL - NOT DONE
async function shortenURL(longURL) {
    try{

    } catch (error) {
        console.error(error); // Log any errors to the console
        throw error;
    }
}