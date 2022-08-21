const $choice = $('.choice-container')

const answeredQuestions = {}
$choice.on("click",
    function (evt) {
        let choiceIdArray = evt.target.id.split('-')
        let id = choiceIdArray[0]
        let choice = choiceIdArray[1]
        if (id in answeredQuestions && !$(evt.target).hasClass('selected')) {
            answeredQuestions[id].push(choice)
        } else if (!$(evt.target).hasClass('selected')) {
            answeredQuestions[id] = [choice]
        }
        if (id in answeredQuestions && $(evt.target).hasClass('selected')) {
            let idxChoice = answeredQuestions[id].indexOf(choice)
            answeredQuestions[id].splice(idxChoice, 1)

        }

        $(evt.target).toggleClass("selected")
    })




$('#submit-quiz-btn').on('click', async function () {
    const response = await axios.post('/quiz-results-data', {answers: answeredQuestions}).then(function (response) {
        createResultElements(response.data)
    })
        .catch(function (error) {
            console.log("Something went wrong");
        });
})


function createResultElements(data) {
    $('.qa-container').remove()
    $('.quiz-btn-container').remove()


    if (data['correct_questions'].length !== 0) {
        $('.quiz-container').append('<div class="results-container" id="questions-correct" ><h3>Correct Answers</h3></div>')
        for (let i = 0; i < data['correct_questions'].length; i++) {
            $('#questions-correct').append(`<div class="answer correct">${data['correct_questions'][i]}</div>`)
        }
    }

    if (data['missed_questions'].length !== 0) {
        $('.quiz-container').append('<div class="results-container" id="questions-wrong" ><h3>Incorrect Answers</h3></div>')
        for (let i = 0; i < data['missed_questions'].length; i++) {
            $('#questions-wrong').append(`<div class="answer wrong">${data['missed_questions'][i]}</div>`)
        }
    }

    if (data['did_not_answer'].length !== 0) {
        $('.quiz-container').append('<div class="results-container" id="did-not-answer" ><h3>Did NotAnswer</h3></div>')
        for (let i = 0; i < data['did_not_answer'].length; i++) {
            $('#did-not-answer').append(`<div class="answer no-answer">${data['did_not_answer'][i]}</div>`)
        }
    }
    if (data['suggested_videos']) {
        $('#questions-wrong').append(`<div class="suggested-videos-container"><h3>Suggested Videos</h3><div class="suggested-videos"></div></div>`)
        for (let i = 0; i < data['suggested_videos'].length; i++) {
            $('.suggested-videos').append(`<div class="video"><a href="https://www.youtube.com/watch?v=${data['suggested_videos'][i][1]}" target="_blank" ><img src="${data['suggested_videos'][i][0]}"  class="video-img" alt="Suggested Video ${i + 1}"></a> <p class="video-title">${data['suggested_videos'][i][2]}</p></div>`)
        }
    }
}
