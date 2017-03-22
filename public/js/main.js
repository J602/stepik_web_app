function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
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


function ajaxQuestionLikeDislike() {
    $('.q-like, .q-dislike').click(
        function () {
            var addressValue = $(this).attr("href");
            $.ajax({
                type: 'post',
                url: addressValue,
                contentType: "application/json; charset=utf-8",
                dataType: 'json',

                success: function (data) {
                    if (data.status == 'ok') {
                        $('#q-rating-'.concat(data.id)).text(data.rating)
                        if(data.code == 200) {
                            var elem = $('#q-like-'.concat(data.id));
                             if (elem.hasClass('i-like')) {
                                 elem.removeClass('i-like')
                             } else {
                                 elem.addClass('i-like')
                             }
                         }
                    }
                    if (data.status == 'error') {

                    }
                },
                error: function (errMsg) {

                }
            });
            return false;
        })
}

function ajaxAnswerLikeDislike() {
    $('.a-like, .a-dislike').click(
        function () {
            var addressValue = $(this).attr("href");
            $.ajax({
                type: 'post',
                url: addressValue,
                contentType: "application/json; charset=utf-8",
                dataType: 'json',

                success: function (data) {
                    if (data.status == 'ok') {
                        $('#a-rating-'.concat(data.id)).text(data.rating)
                         if(data.code == 200) {
                            var elem = $('#a-like-'.concat(data.id));
                             if (elem.hasClass('i-like')) {
                                 elem.removeClass('i-like')
                             } else {
                                 elem.addClass('i-like')
                             }
                         }
                    }
                },
                error: function (errMsg) {
                    console.log(errMsg)
                }
            });
            return false;
        })
}