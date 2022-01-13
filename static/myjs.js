//username에 반응하여 게시물을 불러온다.
function listing(username) {
    //만약 username에 담긴 값이 없을 경우 username은 없는 것으로 간주한다.
    if (username == undefined) {
        username = ""
    }
    //서버에서 정보 받아오기 전에 게시물이 담길 공간을 비운다.
    $("#post-box").empty()
    $.ajax({
        type: "GET",
        //서버에 사용자의 username을 보낸다.
        url: `/listing?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response['posts']
                for (let i = 0; i < posts.length; i++) {
                    //각 post 에서 필요한 값을 가져온다.
                    let post = posts[i]
                    let num = post['num']
                    let place_pic = post['place_pic']
                    let profile_name = post['profile_name']
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)
                     //class_heart는 첫번쨰항이 true면 fa-heart이고 false면 fa-heart-o이다.
                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"
                    let count_heart = post['count_heart']
                    // 가져온 값들을 원하는 곳에 넣어준다.
                    let temp_html = `<div style="margin:10px 0px 10px 20px; width: 18rem;" class="card" id="${post["_id"]}">
                                                <div class="pic" >
                                                    <img style="height: 13rem; object-fit: cover"  src="../static/place_pic/${place_pic}" id="${post["_id"]}" onclick="location.href = '/detail/${num}'">
                                                         <div class="level-left"><div class="name"> <strong>${profile_name}</strong>&nbsp;<small>${time_before}</small></div>&nbsp;
                                                              <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                                   <span style="color: red" class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>&nbsp;<span  style="color: red" class="like-num">${num2str(count_heart)}</span>
                                                              </a>
                                                         </div>
                                                    </nav>
                                                </div>
                                         </div>`
                    //게시물이 담길 공간으로 옮긴다.
                    $('#post-box').append(temp_html)
                }
            }
        }
    });
}

//좋아요 개수를 나타내는 숫자의 형식을 정해준다.
function num2str(count) {
    //만개가 넘으면 정수 뒤에 K
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    // 500개가 넘으면 소수점 뒤에 K
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    // 0개일 때는 숫자가 없다.
    if (count == 0) {
        return ""
    }//나머지는 그대로 나타낸다.
    return count
}

//게시물이 작성된지 얼마나 되었는가를 보여준다.
function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    //60초가 넘어가는 경우에는 분으로 보여준다.
    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    //60분이 넘어가는 경우에는 시간으로 보여준다.
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    //24시간이 넘어가는 경우에는 일 수로 보여준다.
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    //7일 이상일 때에는 날짜로 보여준다.
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}
//게시물의 post_id와 좋아요의 type을 확인해서 좋아요기능을 구현한다.
function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='heart']`)
    let $i_like = $a_like.find("i")
    //좋아요가 되어있는거면 좋아요를 취소한다.
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
                //찬 하트를 숨기고 빈 하트를 보여준다.
                $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                $a_like.find("span.like-num").text(response["count"])
            }
        })
        //아니면 좋아요를 실행한다.
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
                //빈 하트를 숨기고 찬 하트를 보여준다.
                $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                $a_like.find("span.like-num").text(response["count"])
            }
        })

    }
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