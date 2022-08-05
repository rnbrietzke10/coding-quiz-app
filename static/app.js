const $choice = $('.choice-container')

$choice.on("click",
    function (evt) {
        // console.log(evt.target)
        $(evt.target).toggleClass("selected")

    })