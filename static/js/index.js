$("#list-tab a").on("click", function (e) {
    e.preventDefault();
    history.pushState('', '', "#" + this.id);
    $(this).tab("show");
});

const allowed = ["#list-main-settings-open", "#list-keys-open", "#list-mixin-settings-open"];

$(document).ready(() => {
    var hash = window.location.hash;
    console.log(hash);
    if (allowed.indexOf(hash) >= 0) {
        $(hash).tab("show");
    }
});

$("#can-read").click(() => {
    $("#allow-info").toggle();
});
