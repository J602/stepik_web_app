function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        }
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getTags(url) {
    $('#tagcloud').load(url);
}

function ajaxSearch() {
    $('#search-button').click(function (e) {
        e.preventDefault();
        $.ajax({
            method: 'post',
            url: this.baseURI,
            data: JSON.stringify({'search_text': $('#search-box').val()}),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function (data) {
                if (data.status == 'ok') {
                    var list_elem = $('#search-result');
                    list_elem.empty();
                    var questions = data.questions;
                    if (questions.length != 0) {
                        var buffer = "";
                        $.each(questions, function (index, val) {
                            buffer += "<li class='list-unstyled' ><a href='" + val.url + "'>" + val.title + "</a></li>";
                            list_elem.html(buffer);
                        });
                    } else {
                        list_elem.html("<li class='list-unstyled' >No results found</li>");
                    }
                }
            },
            error: function (errMsg) {
                console.log(errMsg);
            }
        });
    })
}

function addBaseEventHandler() {
    $('#git-send').on('click', sendGitClickHandler)
}

function addQuestionsEventHandler() {
    $('.q-like, .q-dislike').on('click', questionLikeDislikeClickHandler)
}

function questionLikeDislikeClickHandler() {
    var addressValue = $(this).attr('href');
    $.ajax({
        type: 'post',
        url: addressValue,
        success: function (data) {
            if (data.status == 'ok') {
                $('#q-rating-'.concat(data.id)).text(data.rating);
                var elem = $('#q-like-'.concat(data.id));
                if (elem.hasClass('i-like')) {
                    elem.removeClass('i-like glyphicon-heart');
                    elem.addClass('glyphicon-triangle-top');
                } else {
                    elem.removeClass('glyphicon-triangle-top');
                    elem.addClass('i-like glyphicon-heart');
                }
            }
            if (data.status == 'error') {
                console.log(data);
            }
        },
        error: function (errMsg) {
            console.log(errMsg);
        }
    });
    return false;
}

function addAnswersEventHandler() {
    $('#answers').on('click', '.a-like, .a-dislike', answerLikeDislikeClickHandler)
    .on('change', '.a-correct', answerCorrectChangeHandler)
    .on('click', '.a-delete', removeAnswerClickHandler)
    .on('click', '.a-edit', answerEditClickHandler);
    $("#add-answer").on('click', addAnswerClickHandler);
    $('#save-answer').on('click', saveAnswerClickHandler);
}

function addQuestionsAnswersEventHandler() {
    addQuestionsEventHandler();
    addAnswersEventHandler();
}

function answerLikeDislikeClickHandler() {
    var addressValue = $(this).attr('href');
    $.ajax({
        type: 'post',
        url: addressValue,
        success: function (data) {
            if (data.status == 'ok') {
                $('#a-rating-'.concat(data.id)).text(data.rating);
                var elem = $('#a-like-'.concat(data.id));
                if (elem.hasClass('i-like')) {
                    elem.removeClass('i-like glyphicon-heart');
                    elem.addClass('glyphicon-triangle-top');
                } else {
                    elem.removeClass('glyphicon-triangle-top');
                    elem.addClass('i-like glyphicon-heart');
                }
            }
        },
        error: function (errMsg) {
            console.log(errMsg)
        }
    });
}

function answerCorrectChangeHandler() {
    var addressValue = $(this).attr('href');
    $.ajax({
        type: 'post',
        url: addressValue,
        success: function (data) {
            if (data.status == 'ok') {
                console.log(data);
            }
        },
        error: function (errMsg) {
            console.log(errMsg);
        }
    });
}

function addAnswerClickHandler(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    if (url != undefined) {
        $.ajax({
                method: 'post',
                url: url,
                data: JSON.stringify({'text': tinymce.get('answer-textarea').getContent()}),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',

                success: function (data) {
                    if (data.status == 'ok') {
                        $.ajax({
                            url: data.url,
                            method: 'get',
                            dataType: "html"
                        }).done(function (response) {
                            $('#answers').append(response);
                        });
                        tinymce.get('answer-textarea').setContent('');
                    }
                },
                error: function (errMsg) {
                    console.log(errMsg)
                }
            }
        )
    }

}

function removeAnswerClickHandler(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    $.ajax({
        method: 'post',
        url: url,
        success: function (data) {
            if (data.status == 'ok') {
                console.log('Deleted!!!');
                $('#answer-' + data.id).remove();
            }
        },
        error: function (errMsg) {
            console.log(errMsg)
        }
    })
}

function saveAnswerClickHandler(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    var id = $('#answer-edit-id').val();
    var content = tinymce.get('answer-edit-textarea').getContent();
    if (url != undefined) {
        $.ajax({
            method: 'post',
            url: url,
            data: JSON.stringify(
                {
                    'text': content,
                    'id': id
                }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function (data) {
                if (data.status == 'ok') {
                    $('#answer-text-' + id).html(content);
                    tinymce.get('answer-edit-textarea').setContent('');
                    $('#answer-edit-id').val('');
                }
            },
            error: function (errMsg) {
                console.log(errMsg)
            }
        })
    }
}

function answerEditClickHandler() {
    $('#answer-edit-id').val($(this).attr('id'));
    $('#answer-edit-url').val($(this).attr('href'));
    $.ajax({
        method: 'get',
        url: $(this).attr('url'),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: {'json': true},
        success: function (data) {
            if (data.status == 'ok') {
                tinymce.get('answer-edit-textarea').setContent(data.text)

            }
        }
    });

}

function showGit() {
    $('#git-open').click(function (e) {
        e.preventDefault();
        $('#overlay, #git-div').css('display', 'block');
        $('#git-email').val('');
        $('#git-msg').html('');
    });
    $('#git-cancel').click(function () {
        $('#overlay, #git-div').css('display', 'none');
    })
}

function sendGitClickHandler(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    var email = $('#git-email').val();
    if (url != undefined) {
        $.ajax({
                method: 'post',
                url: url,
                data: JSON.stringify({'text': email}),
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function (data) {
                    if (data.status == 'ok') {
                        $('#git-msg').html('Message sent on: '.concat(email));
                        setTimeout(function () {
                            $('#overlay, #git-div').css('display', 'none');
                        }, 1500)
                    }
                },
                error: function (errMsg) {
                    console.log(errMsg);
                }
            }
        )
    }
}

