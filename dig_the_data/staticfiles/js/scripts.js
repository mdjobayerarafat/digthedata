function submitAnswer(questionId) {
    const answerInput = document.getElementById(`answer_${questionId}`);
    const answer = answerInput.value;

    // Make an AJAX request to submit the answer
    fetch(`/submit_answer/${questionId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Use the function to get the CSRF token
        },
        body: JSON.stringify({ answer: answer })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.is_correct ? 'Correct answer!' : 'Wrong answer!');
            // Disable the input field if the answer is correct
            if (data.is_correct) {
                answerInput.disabled = true;  // Disable the input field
            }
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error submitting answer:', error);
    });
}
// Function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
