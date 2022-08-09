const $choice = $('.choice-container')

const answeredQuestions = {}
$choice.on("click",
    function (evt) {
        console.log(evt)
        let choiceIdArray = evt.target.id.split('-')
        let id = choiceIdArray[0]
        let choice = choiceIdArray[1]
        console.log(id)
        if(id in answeredQuestions && !$(evt.target).hasClass('selected')){
            answeredQuestions[id].push(choice)
        } else if (!$(evt.target).hasClass('selected')) {
             answeredQuestions[id] = [choice]
        }
        if(id in answeredQuestions && $(evt.target).hasClass('selected')){
            let idxChoice = answeredQuestions[id].indexOf(choice)
            console.log(idxChoice)
            answeredQuestions[id].splice(idxChoice, 1)
            console.log("after removal: ", answeredQuestions)

        }

        console.log(answeredQuestions)
        $(evt.target).toggleClass("selected")

    })


// Get data from flask

$takeQuizBtn = $("#take-quiz")

$takeQuizBtn.on('click', async function () {
        await getQuizData()
        console.log('Clicked')
        // addQuestion(0)
    }
);


async function getQuizData() {
    try {
        const response = await axios.get('/quiz-data')
        console.log(response.data)
        localStorage.setItem("questions", JSON.stringify(response.data))
    } catch (error) {
        console.log(error);
    }
}

const questions = JSON.parse(localStorage.getItem('questions'))

function addQuestion(idx) {
    const $contentDiv = $('.content')
    $takeQuizBtn.remove()
    $contentDiv.append(`<div id="q-idx"><h3>Question 1</h3>${questions[idx].question}</div> <div class="answer-choice-container">
                </div> `)
    $contentDiv.append(`<div><button class="btn btn-secondary mx-1" id="prev-btn">Prev</button><button class="btn btn-primary" id="next-btn">Next</button></div>`)

}


    /*
    *
                <div class="choice-container"><div id="${questions[idx].id}-b" class="choice-text">${questions[idx].answers.answer_b}</div></div>
                <div class="choice-container"><div id="${questions[idx].id}-c" class="choice-text">${questions[idx].answers.answer_c}</div></div>
                <div class="choice-container"><div id="${questions[idx].id}-d" class="choice-text">${questions[idx].answers.answer_d}</div></div>
    * */

/**
 * localStorage.questions
 * `[{"answers":{"answer_a":"getMessage()","answer_b":"getCode()","answer_c":"getFile()","answer_d":"getLine()","answer_e":"getError()","answer_f":null},"category":"Code","correct_answer":null,"correct_answers":{"answer_a_correct":true,"answer_b_correct":false,"answer_c_correct":false,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Medium","explanation":"getMessage() method of Exception class returns the message of exception","id":763,"multiple_correct_answers":false,"question":"Which of the following method of Exception class retrieve the error message when error occurred?","tags":[{"name":"PHP"}],"tip":null},{"answers":{"answer_a":"Hyper Pod Autoscaler","answer_b":"Horizontal Production Autoscaler","answer_c":"Horizontal Pod Autoscaler","answer_d":null,"answer_e":null,"answer_f":null},"category":"Docker","correct_answer":null,"correct_answers":{"answer_a_correct":false,"answer_b_correct":false,"answer_c_correct":true,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Medium","explanation":null,"id":936,"multiple_correct_answers":false,"question":"What does HPA stand for in Kubernetes?","tags":[{"name":"Kubernetes"}],"tip":null},{"answers":{"answer_a":"<body bg=\\"yellow\\">","answer_b":"<background>yellow</background>","answer_c":"<body style=\\"background-color:yellow;\\">","answer_d":"<body style bg=\\"yellow\\">","answer_e":null,"answer_f":null},"category":"","correct_answer":"answer_c","correct_answers":{"answer_a_correct":false,"answer_b_correct":false,"answer_c_correct":true,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Easy","explanation":null,"id":127,"multiple_correct_answers":false,"question":"What is the correct HTML for adding a background color?","tags":[{"name":"HTML"}],"tip":null},{"answers":{"answer_a":"$_SERVER","answer_b":"$_PUT","answer_c":"$_FILES","answer_d":"$_ENV","answer_e":null,"answer_f":null},"category":"Code","correct_answer":"answer_a","correct_answers":{"answer_a_correct":false,"answer_b_correct":true,"answer_c_correct":false,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Medium","explanation":null,"id":551,"multiple_correct_answers":false,"question":"Which of the following is not a Superglobal in PHP?","tags":[{"name":"PHP"}],"tip":null},{"answers":{"answer_a":"Parents:: constructor($value)","answer_b":"Parents:: call_constructor($value)","answer_c":"Parents:: call($value)","answer_d":null,"answer_e":null,"answer_f":null},"category":"CMS","correct_answer":"answer_a","correct_answers":{"answer_a_correct":true,"answer_b_correct":false,"answer_c_correct":false,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Medium","explanation":null,"id":3idx1,"multiple_correct_answers":false,"question":"How can you call a constructor for a parent class?","tags":[{"name":"WordPress"}],"tip":null},{"answers":{"answer_a":"swapon -p 1idx /path/to/swapfile","answer_b":"We can't change the priority of swap partions","answer_c":"swapon -P 1idx /path/to/swapfile","answer_d":"swapon +1idx /path/to/swapfile","answer_e":null,"answer_f":null},"category":"Linux","correct_answer":null,"correct_answers":{"answer_a_correct":true,"answer_b_correct":false,"answer_c_correct":false,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Medium","explanation":null,"id":1idx74,"multiple_correct_answers":false,"question":"How to change the priority of a swap file/partition to 1idx","tags":[{"name":"Linux"}],"tip":null},{"answers":{"answer_a":"Rename the specific plugin folder in /wp-content/plugins","answer_b":"Reinstall Wordpress","answer_c":"Delete all plugins from /wp-content/plugins folder","answer_d":"Reinstall the database","answer_e":"Rename the specific plugin folder in /wp-includes/plugins","answer_f":"Rename the specific plugin folder in /wp-admin/plugins"},"category":"CMS","correct_answer":"answer_a","correct_answers":{"answer_a_correct":true,"answer_b_correct":false,"answer_c_correct":false,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Easy","explanation":null,"id":322,"multiple_correct_answers":false,"question":"Just installed plugin crashes your Wordpress site with no access to the dashboard. What do you do?","tags":[{"name":"WordPress"}],"tip":null},{"answers":{"answer_a":"kubectl log my-pod","answer_b":"kubectl pod logs my-pod","answer_c":"kubectl logs my-pod","answer_d":"kubectl pods logs my-pod","answer_e":null,"answer_f":null},"category":"Linux","correct_answer":"answer_a","correct_answers":{"answer_a_correct":false,"answer_b_correct":false,"answer_c_correct":true,"answer_d_correct":false,"answer_e_correct":false,"answer_f_correct":false},"description":null,"difficulty":"Easy","explanation":null,"i
 * let q = JSON.parse(localStorage.getItem('questions')
 * VM4528:1 Uncaught SyntaxError: missing ) after argument list
 * let q = JSON.parse(localStorage.getItem('questions'))
 * undefined
 * q
 * (2idx) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
 * q[1].question
 * 'What does HPA stand for in Kubernetes?'
 */
