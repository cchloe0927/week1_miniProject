function sign_out() {//로그아웃 버튼을 누르면
    $.removeCookie('mytoken', {path: '/'});//쿠키를 브라우저에서 삭제
    alert('로그아웃!')
    window.location.href = "/login"
}

function showReview() {
                $.ajax({
                    type: "GET",
                    url: "/review",
                    data: {},
                    success: function (response) {
                        let reviews = response['all_reviews']
                        for (let i = 0; i<reviews.length; i++ ) {
                            let title = reviews[i]['title']
                            let author = reviews[i]['author']
                            let review = reviews[i]['review']

                            let temp_html = `
                                            <tr>
                                                <td>${title}</td>
                                                <td>${author}</td>
                                                <td>${review}</td>
                                            </tr>
                                            `
                            $('#reviews-box').append(temp_html)

                        }
                    }
                })
            }