<script setup>
import { ref } from 'vue';
import Header from '../components/Header.vue';
import ContentChat from '../components/ContentChat.vue';
import InputChat from '../components/InputChat.vue';
import api from '../api'

const ContentChatRef = ref(null);

const UpChat = (newMessage) => {
    if (newMessage.type === 'audio') {
        fetchAUDIO(newMessage.data)
    } else if (newMessage.type === 'text') {
        fetchCHAT(newMessage.data)
    }
}

const fetchCHAT = async (msg) => {
    ContentChatRef.value.addMessage(true, false, msg)
    ContentChatRef.value.addMessage(false, true, '');
    const endpoint = ''
    const data = {
        "userID": 'miguel',
        "query": msg
    }
    const codigo = "```python\ndef hello_world():\n    print('Hello, World!')\n    hello_world()```"
    const message = `Here is some general *information* outside of the tags.

<citations>
1. Smith, J. (2020). *Artificial Intelligence: A Modern Approach*. Cambridge Press.
2. Doe, J. (2019). *The Rise of AI in Everyday Life*. Tech Innovations Journal, 12(3), 45-67.
3. OpenAI. (2023). *Research on Language Models*. Retrieved from https://openai.com/research.
</citations>

Now let’s dive into a summary of the data.

<table>
<tr>
  <th>Year</th><th>Technology</th><th>Impact</th>
</tr>
<tr>
  <td>2020</td><td>AI in Healthcare</td><td>Revolutionized diagnostics and patient care</td>
</tr>
<tr>
  <td>2021</td><td>AI in Finance</td><td>Improved fraud detection and personalized financial services</td>
</tr>
<tr>
  <td>2022</td><td>AI in Education</td><td>Personalized learning experiences for students</td>
</tr>
<tr>
  <td>2023</td><td>AI in Autonomous Vehicles</td><td>Enhanced navigation and safety features</td>
</tr>
</table>

As you can see from the table, AI has had significant impacts across multiple industries.

<code>
/**
 * This function calculates the sum of an array.
 * @param {Array} numbers - An array of numbers
 * @returns {Number} The sum of the numbers
 */
function calculateSum(numbers) {
  return numbers.reduce((acc, num) => acc + num, 0);
}

// Example usage:
const values = [5, 10, 15, 20];
console.log(calculateSum(values)); // Output: 50
</code>

To sum up, AI continues to make profound changes in every field, and the trend is expected to grow even stronger over the coming years. By 2030, AI is predicted to become integral to the global economy, influencing not only technology but also societal norms and human interaction.

<citations>
1. Bostrom, N. (2016). *Superintelligence: Paths, Dangers, Strategies*. Oxford University Press.
2. Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*. Pearson.
</citations>

That's the complete summary of AI's recent advancements and impact across various sectors.
<code>
${codigo}
</code>

And here is a pie chart of AI technology distribution:

<chart>
{
  "type": "pie",
  "data": {
    "labels": ["Healthcare", "Finance", "Education", "Autonomous Vehicles"],
    "datasets": [
      {
        "label": "AI Technology Distribution",
        "data": [35, 25, 20, 20],
        "backgroundColor": ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56"]
      }
    ]
  },
  "options": {
    "responsive": true
  }
}
</chart>
`




    try {
        //const result = await api.requestCHAT(data);
        let result = {
            'id': Math.random(),
            'text': message
        }
        setTimeout(() => {
            result['isUser'] = false
            ContentChatRef.value.addMessage(false, false, result);
        }, 1000);

    } catch (error) {
        console.error('API error fetchCHAT:', error);
    }
}

const fetchAUDIO = async (formData) => {
    ContentChatRef.value.addMessage(true, true, '')
    try {
        //const result = await api.requestWhisper(formData)
        const result = 'audio'
        setTimeout(() => {
            fetchCHAT(result)
        }, 1000);
    } catch (error) {
        console.error('API Error fetchAUDIO:', error);
    }
}

const fetchVote = async (data) => {
    try {
        //data['user'] = localStorage.getItem('email');
        //const result = await api.requestVote(data);
        console.log(data)
    } catch (error) {
        console.error('API error fetchVote:', error);
    }

}

</script>

<template>
    <div class="cardContent">
        <div class="cardContent-content">
            <Header />
            <ContentChat ref="ContentChatRef" @pushed_vote="fetchVote" />
            <InputChat @pushed_message="UpChat" />
        </div>
    </div>
</template>

<style scoped>
.cardContent {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: width 0.3s;
    background-color: #f8f8f8;
    overflow: hidden;
    height: calc(100vh - 40px);
    display: flex;
    border-radius: 8px;
    flex: 1;
}

.cardContent-content {
    padding: 20px;
    white-space: nowrap;
    width: 100%;
}
</style>