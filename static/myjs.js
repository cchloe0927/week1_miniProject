function listing(username) {
    if (username == undefined) {
        username = ""
    }
    $("#post-box").empty()
    $.ajax({
        type: "GET",
        url: `/listing?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response['posts']
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let place_pic = post['place_pic']
                    let profile_name = post['profile_name']

                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)

                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o" //class_heart는 첫번쨰항이 true면 fa-heart이고 false면 fa-heart-o이다
                    let count_heart = post['count_heart']
                    let temp_html = `<div class="card" id="${post["_id"]}">
                                                <div class="pic" >
                                                    <img src="../static/place_pic/${place_pic}" onclick="location.href = '/'">
                                                         <div class="level-left"><div class="name"> <strong>${profile_name}</strong>&nbsp;<small>${time_before}</small></div>&nbsp;
                                                              <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                                   <span class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(count_heart)}</span>
                                                              </a>
                                                         </div>
                                                    </nav>
                                                </div>
                                         </div>`

                    $('#post-box').append(temp_html)
                }
            }
        }
    });
}


function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}

function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='heart']`)
    let $i_like = $a_like.find("i")
    if ($i_like.hasClass("fa-heart")) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                $a_like.find("span.like-num").text(response["count"])
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                $a_like.find("span.like-num").text(response["count"])
            }
        })

    }
}


function this_post() { //디테일로 이동하는 함수
    location.href = "/detail"
}


// {#로그아웃 기능#}
function sign_out() {//로그아웃 버튼을 누르면
    $.removeCookie('mytoken', {path: '/'});//쿠키를 브라우저에서 삭제
    alert('로그아웃!')
    window.location.href = "/login"
}


function update_profile() {
    let name = $('#input-name').val()
    let file = $('#input-pic')[0].files[0]    //프로필 파옴
    let about = $("#textarea-about").val()    //자기소개 칸
    let form_data = new FormData()
    form_data.append("file_give", file)
    form_data.append("name_give", name)
    form_data.append("about_give", about)
    console.log(name, file, about, form_data)

    $.ajax({
        type: "POST",
        url: "/update_profile",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response["result"] == "success") {
                alert(response["msg"])
                window.location.reload()

            }
        }
    });
}