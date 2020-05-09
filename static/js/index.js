$("#list-tab a").on("click", function (e) {
    e.preventDefault();
    history.pushState("", "", "#" + this.id);
    $(this).tab("show");
});

const allowed = ["#list-main-settings-open", "#list-keys-open", "#list-mixin-settings-open",
"#list-username-change", "#list-email-change", "#list-password-change"];

$(document).ready(() => {
    var hash = window.location.hash;
    if (allowed.indexOf(hash) >= 0) {
        $(hash).tab("show");
    }
});

$("#can-read").change(() => {
    $("#allow-info").toggle();
});

$("#can-write").change(() => {
    $("#allow-info").toggle();
});


$("#allow-info").change(() => {
    $("#selected-info").toggle();
});


$('form').submit(function () {
    console.log(111);

    var value_input1 = $(".pass1").val();
    var value_input2 = $(".pass2").val();
    if(value_input1 != value_input2) {
        $(".passwords-mismatch").html("Пароли не совпадают");
        return false;
    } else {
        return true;
    }
});