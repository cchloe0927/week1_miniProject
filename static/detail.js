function sign_out() {//로그아웃 버튼을 누르면
    $.removeCookie('mytoken', {path: '/'});//쿠키를 브라우저에서 삭제
    alert('로그아웃!')
    window.location.href = "/login"
}